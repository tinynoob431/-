import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib import error, parse, request


DEFAULT_VALUE = "needs-check"


def http_get_json(url, headers):
    req = request.Request(url, headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code} for {url}\n{detail}") from e
    except error.URLError as e:
        raise RuntimeError(f"Network error for {url}: {e}") from e


def parse_args():
    parser = argparse.ArgumentParser(description="从 Zotero API 拉取指定条目并生成项目 JSON。")
    parser.add_argument("--item-key", required=True, help="Zotero 条目 key，例如 XBXJDM7G")
    parser.add_argument("--output", default=None, help="输出 JSON 路径（默认 input/<item-key>.json）")
    parser.add_argument("--include-annotations", action="store_true", help="拉取批注并写入证据字段")
    parser.add_argument("--extract-framework-image", action="store_true", help="从 PDF 自动抽取主图并写入 JSON")
    parser.add_argument("--pdf-path", default=None, help="本地 PDF 路径（用于抽图）")
    parser.add_argument("--assets-dir", default="assets", help="图片输出根目录（默认 assets）")
    parser.add_argument("--max-figure-pages", type=int, default=8, help="抽图时最多扫描前 N 页（默认 8）")
    return parser.parse_args()


def get_env(name, required=True, default=None):
    value = os.getenv(name, default)
    if required and (value is None or not str(value).strip()):
        raise RuntimeError(f"缺少环境变量: {name}")
    return value


def pick_year(date_text):
    if not date_text:
        return DEFAULT_VALUE
    m = re.search(r"\b(19\d{2}|20\d{2})\b", str(date_text))
    return m.group(1) if m else DEFAULT_VALUE


def pick_venue(data):
    for key in ("publicationTitle", "proceedingsTitle", "conferenceName", "archive", "journalAbbreviation", "websiteTitle"):
        value = (data.get(key) or "").strip()
        if value:
            return value
    return DEFAULT_VALUE


def creators_to_authors(creators):
    out = []
    for c in creators or []:
        ctype = (c.get("creatorType") or "").lower()
        if ctype not in ("author", "presenter", "contributor"):
            continue
        if c.get("name"):
            name = str(c.get("name")).strip()
        else:
            first = str(c.get("firstName") or "").strip()
            last = str(c.get("lastName") or "").strip()
            name = f"{first} {last}".strip()
        if name:
            out.append(name)
    return out if out else [DEFAULT_VALUE]


def normalize_tags(tags):
    out = []
    for tag in tags or []:
        if isinstance(tag, dict):
            value = str(tag.get("tag") or "").strip()
        else:
            value = str(tag).strip()
        if value:
            out.append(value)
    return out


def sanitize_stem(name):
    cleaned = re.sub(r"[^\w\-]+", "_", name, flags=re.U).strip("_")
    return cleaned or "paper"


def extract_pdf_key(children):
    for child in children or []:
        data = child.get("data", {})
        if data.get("itemType") != "attachment":
            continue
        content_type = (data.get("contentType") or "").lower()
        filename = (data.get("filename") or "").lower()
        if "pdf" in content_type or filename.endswith(".pdf"):
            key = (data.get("key") or "").strip()
            if key:
                return key
    return DEFAULT_VALUE


def _page_sort_key(page):
    if page is None:
        return (10**9, "")
    text = str(page).strip()
    if not text:
        return (10**9, "")
    m = re.search(r"\d+", text)
    if m:
        return (int(m.group(0)), text)
    return (10**9, text)


def extract_annotations(items):
    rows = []
    for item in items or []:
        data = item.get("data", {})
        if data.get("itemType") != "annotation":
            continue
        text = (data.get("annotationText") or "").strip()
        comment = (data.get("annotationComment") or "").strip()
        page = data.get("annotationPageLabel") or data.get("annotationPosition")

        merged = []
        if text:
            merged.append(text)
        if comment:
            merged.append(f"评论: {comment}")
        if page:
            merged.append(f"页码: {page}")
        if merged:
            rows.append((page, "- " + " | ".join(merged)))

    if not rows:
        return DEFAULT_VALUE
    rows.sort(key=lambda x: _page_sort_key(x[0]))
    return "\n".join(line for _, line in rows)


def extract_attachment_keys(children):
    keys = []
    for child in children or []:
        data = child.get("data", {})
        if data.get("itemType") != "attachment":
            continue
        key = (data.get("key") or "").strip()
        if key:
            keys.append(key)
    return keys


def collect_annotations(children, headers, library_type, user_id):
    collected = []
    direct = extract_annotations(children)
    if direct != DEFAULT_VALUE:
        collected.append(direct)

    for att_key in extract_attachment_keys(children):
        sub_url = f"https://api.zotero.org/{library_type}s/{user_id}/items/{parse.quote(att_key)}/children"
        sub_children = http_get_json(sub_url, headers=headers)
        sub_ann = extract_annotations(sub_children)
        if sub_ann != DEFAULT_VALUE:
            collected.append(sub_ann)

    if not collected:
        return DEFAULT_VALUE
    return "\n".join(collected)


def parse_pdfimages_list(stdout_text):
    rows = []
    seen_sep = False
    for raw_line in stdout_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("-----"):
            seen_sep = True
            continue
        if not seen_sep:
            continue

        parts = line.split()
        if len(parts) < 6 or not parts[0].isdigit() or not parts[1].isdigit():
            continue
        page = int(parts[0])
        num = int(parts[1])
        width = int(parts[3]) if parts[3].isdigit() else 0
        height = int(parts[4]) if parts[4].isdigit() else 0
        rows.append({"page": page, "num": num, "width": width, "height": height, "area": width * height})
    return rows


def detect_figure_page_from_text(pdf_path, max_pages=8):
    pdftotext_bin = shutil.which("pdftotext")
    if not pdftotext_bin:
        return None
    best_page = None
    best_score = -10**9
    for page in range(1, max_pages + 1):
        proc = subprocess.run(
            [pdftotext_bin, "-f", str(page), "-l", str(page), str(pdf_path), "-"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if proc.returncode != 0:
            continue
        page_text = (proc.stdout or "").lower()
        score = 0
        if re.search(r"\bfigure\s*1\b|\bfig\.?\s*1\b", page_text):
            score += 200
        if re.search(r"\bfigure\b|\bfig\.\b", page_text):
            score += 80
        if "framework" in page_text or "architecture" in page_text:
            score += 40
        score -= abs(page - 2) * 8
        if page == 1:
            score -= 30
        if score > best_score:
            best_score = score
            best_page = page
    if best_score < 0:
        return 2 if max_pages >= 2 else 1
    return best_page


def render_page_png_fallback(pdf_path, out_dir, page):
    pdftoppm_bin = shutil.which("pdftoppm")
    if not pdftoppm_bin:
        return None, "pdftoppm not found; page-render fallback is unavailable."

    prefix = out_dir / "page_render"
    proc = subprocess.run(
        [pdftoppm_bin, "-f", str(page), "-l", str(page), "-png", str(pdf_path), str(prefix)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "pdftoppm render failed"
        return None, msg
    candidates = sorted(out_dir.glob("page_render-*.png"))
    if not candidates:
        return None, "Page render finished but no PNG was produced."
    return candidates[0], ""


def extract_framework_image_from_pdf(pdf_path, item_key, assets_root, max_pages):
    pdfimages_bin = shutil.which("pdfimages")

    out_dir = assets_root / item_key
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "img"

    if pdfimages_bin:
        list_cmd = [pdfimages_bin, "-f", "1", "-l", str(max_pages), "-list", str(pdf_path)]
        list_proc = subprocess.run(list_cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if list_proc.returncode == 0:
            rows = parse_pdfimages_list(list_proc.stdout)
            if rows:
                rows.sort(key=lambda r: (r["area"] - r["page"] * 1000), reverse=True)
                best = rows[0]

                extract_cmd = [pdfimages_bin, "-f", "1", "-l", str(max_pages), "-png", str(pdf_path), str(prefix)]
                extract_proc = subprocess.run(extract_cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
                if extract_proc.returncode == 0:
                    candidates = list(out_dir.glob("img-*.png"))
                    if candidates:
                        chosen = None
                        for p in candidates:
                            m = re.search(r"img-(\d+)\.png$", p.name)
                            if m and int(m.group(1)) == best["num"]:
                                chosen = p
                                break
                        if chosen is None:
                            chosen = max(candidates, key=lambda p: p.stat().st_size)

                        final_name = f"framework_p{best['page']:02d}_n{best['num']:03d}.png"
                        final_path = out_dir / final_name
                        if final_path.exists():
                            final_path.unlink()
                        chosen.replace(final_path)

                        relative = Path("assets") / item_key / final_name
                        return relative.as_posix(), f"Auto extracted from PDF page {best['page']} image {best['num']}"

    # fallback for vector-only PDFs (no embedded raster image)
    page = detect_figure_page_from_text(pdf_path, max_pages=max_pages) or (2 if max_pages >= 2 else 1)
    rendered, err = render_page_png_fallback(pdf_path, out_dir, page)
    if rendered:
        final_name = f"framework_page_{page:02d}_render.png"
        final_path = out_dir / final_name
        if final_path.exists():
            final_path.unlink()
        rendered.replace(final_path)
        relative = Path("assets") / item_key / final_name
        return relative.as_posix(), f"Rendered PDF page {page} as fallback (vector figure likely)."

    return None, f"Figure extraction failed: {err}"


def build_payload(item_data, item_key, pdf_key, annotations):
    title = (item_data.get("title") or "").strip() or item_key
    zotero_tags = normalize_tags(item_data.get("tags"))
    collections = item_data.get("collections") or []
    doi = (item_data.get("DOI") or "").strip() or DEFAULT_VALUE

    return {
        "title": title,
        "aliases": [],
        "authors": creators_to_authors(item_data.get("creators")),
        "year": pick_year(item_data.get("date")),
        "venue": pick_venue(item_data),
        "doi": doi,
        "paper_type": "method",
        "paper_subtype": DEFAULT_VALUE,
        "status": "seed",
        "abstract": (item_data.get("abstractNote") or "").strip() or DEFAULT_VALUE,
        "zotero_item_key": item_key,
        "pdf_key": pdf_key,
        "zotero_collections": collections if collections else [],
        "zotero_tags": zotero_tags if zotero_tags else [],
        "canonical_tags": [],
        "candidate_tags": [],
        "tags": ["method"],
        "one_sentence_summary": DEFAULT_VALUE,
        "research_relation": DEFAULT_VALUE,
        "core_library_decision": "candidate",
        "core_library_reason": DEFAULT_VALUE,
        "why_read": DEFAULT_VALUE,
        "core_problem": DEFAULT_VALUE,
        "core_bottleneck": DEFAULT_VALUE,
        "other_methods": DEFAULT_VALUE,
        "method_one_liner": DEFAULT_VALUE,
        "main_contributions": DEFAULT_VALUE,
        "headline_results": DEFAULT_VALUE,
        "application_scenarios": DEFAULT_VALUE,
        "main_limitations": DEFAULT_VALUE,
        "evidence_core_problem": DEFAULT_VALUE,
        "evidence_core_bottleneck": DEFAULT_VALUE,
        "evidence_other_methods": DEFAULT_VALUE,
        "evidence_method": DEFAULT_VALUE,
        "evidence_contributions": DEFAULT_VALUE,
        "evidence_results": DEFAULT_VALUE,
        "evidence_scenarios": DEFAULT_VALUE,
        "evidence_limitations": DEFAULT_VALUE,
        "framework_image_path": DEFAULT_VALUE,
        "framework_source": DEFAULT_VALUE,
        "framework_type": DEFAULT_VALUE,
        "core_modules": DEFAULT_VALUE,
        "pipeline_flow": DEFAULT_VALUE,
        "framework_explanation": DEFAULT_VALUE,
        "framework_needs_check": DEFAULT_VALUE,
        "task_input": DEFAULT_VALUE,
        "task_output": DEFAULT_VALUE,
        "assumptions": DEFAULT_VALUE,
        "module_1": DEFAULT_VALUE,
        "module_2": DEFAULT_VALUE,
        "method_idea": DEFAULT_VALUE,
        "training_strategy": DEFAULT_VALUE,
        "inference_pipeline": DEFAULT_VALUE,
        "key_equations": DEFAULT_VALUE,
        "equation_symbols": DEFAULT_VALUE,
        "equation_role": DEFAULT_VALUE,
        "equation_vs_baseline": DEFAULT_VALUE,
        "datasets": DEFAULT_VALUE,
        "backbone": DEFAULT_VALUE,
        "baselines": DEFAULT_VALUE,
        "metrics": DEFAULT_VALUE,
        "main_results_table_or_text": DEFAULT_VALUE,
        "result_reliability": DEFAULT_VALUE,
        "most_important_figure_or_table": DEFAULT_VALUE,
        "figure_table_takeaway": DEFAULT_VALUE,
        "ablation_results": DEFAULT_VALUE,
        "efficiency_cost": DEFAULT_VALUE,
        "error_analysis": DEFAULT_VALUE,
        "evidence_datasets": DEFAULT_VALUE,
        "evidence_backbone": DEFAULT_VALUE,
        "evidence_baselines": DEFAULT_VALUE,
        "evidence_metrics": DEFAULT_VALUE,
        "evidence_main_results": DEFAULT_VALUE,
        "evidence_ablation": DEFAULT_VALUE,
        "evidence_efficiency": DEFAULT_VALUE,
        "evidence_failures": DEFAULT_VALUE,
        "citable_background": DEFAULT_VALUE,
        "citable_background_source": DEFAULT_VALUE,
        "citable_gap": DEFAULT_VALUE,
        "citable_gap_source": DEFAULT_VALUE,
        "citable_method_compare": DEFAULT_VALUE,
        "citable_method_compare_source": DEFAULT_VALUE,
        "citable_experiment": DEFAULT_VALUE,
        "citable_experiment_source": DEFAULT_VALUE,
        "citable_limitation": DEFAULT_VALUE,
        "citable_limitation_source": DEFAULT_VALUE,
        "zotero_annotations_and_evidence": (
            f"- Zotero item key: {item_key}\n- PDF key: {pdf_key}\n- 批注摘录:\n{annotations}"
            if annotations != DEFAULT_VALUE
            else f"- Zotero item key: {item_key}\n- PDF key: {pdf_key}\n- 批注摘录: {DEFAULT_VALUE}"
        ),
        "core_library_review_plan": DEFAULT_VALUE,
        "worth_deep_reading": DEFAULT_VALUE,
        "value_for_my_research": DEFAULT_VALUE,
        "what_to_reuse": DEFAULT_VALUE,
        "what_to_ignore": DEFAULT_VALUE,
        "my_assessment": DEFAULT_VALUE,
        "open_questions": DEFAULT_VALUE,
        "next_actions": DEFAULT_VALUE,
    }


def main():
    args = parse_args()

    user_id = get_env("ZOTERO_USER_ID")
    api_key = get_env("ZOTERO_API_KEY")
    library_type = get_env("ZOTERO_LIBRARY_TYPE", required=False, default="user").strip().lower()
    if library_type not in ("user", "group"):
        raise RuntimeError("ZOTERO_LIBRARY_TYPE 必须是 user 或 group")

    item_key = args.item_key.strip()
    if not item_key:
        raise RuntimeError("--item-key 不能为空")

    headers = {"Zotero-API-Key": api_key, "Zotero-API-Version": "3"}
    item_url = f"https://api.zotero.org/{library_type}s/{user_id}/items/{parse.quote(item_key)}"
    item_resp = http_get_json(item_url, headers=headers)
    item_data = item_resp.get("data", {})
    if not item_data:
        raise RuntimeError(f"未读取到条目 data: {item_key}")

    children_url = f"https://api.zotero.org/{library_type}s/{user_id}/items/{parse.quote(item_key)}/children"
    children = http_get_json(children_url, headers=headers)
    pdf_key = extract_pdf_key(children)
    annotations = collect_annotations(children, headers, library_type, user_id) if args.include_annotations else DEFAULT_VALUE

    payload = build_payload(item_data, item_key, pdf_key, annotations)

    if args.extract_framework_image:
        if not args.pdf_path:
            payload["framework_needs_check"] = "已请求抽图，但未提供 --pdf-path。"
        else:
            pdf_path = Path(args.pdf_path).expanduser().resolve()
            if not pdf_path.exists():
                payload["framework_needs_check"] = f"PDF 不存在: {pdf_path}"
            else:
                repo_root = Path(__file__).resolve().parent.parent
                assets_root = repo_root / args.assets_dir
                rel_path, source_or_error = extract_framework_image_from_pdf(
                    pdf_path=pdf_path,
                    item_key=item_key,
                    assets_root=assets_root,
                    max_pages=max(1, args.max_figure_pages),
                )
                if rel_path:
                    payload["framework_image_path"] = rel_path
                    payload["framework_source"] = source_or_error
                    payload["framework_type"] = "framework / architecture / pipeline (needs-check)"
                    payload["framework_needs_check"] = DEFAULT_VALUE
                else:
                    payload["framework_needs_check"] = source_or_error

    repo_root = Path(__file__).resolve().parent.parent
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else (repo_root / "input" / f"{sanitize_stem(item_key)}.json")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已生成 JSON: {output_path}")
    print(f"下一步可运行: python scripts/generate_note.py {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"失败: {e}")
        sys.exit(1)
