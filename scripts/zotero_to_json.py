import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib import error, parse, request


DEFAULT_VALUE = "needs-check"


def http_get_json(url, headers):
    req = request.Request(url, headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code} for {url}\n{body}") from e
    except error.URLError as e:
        raise RuntimeError(f"Network error for {url}: {e}") from e


def parse_args():
    parser = argparse.ArgumentParser(
        description="从 Zotero API 拉取条目并生成与本项目兼容的 JSON 输入。"
    )
    parser.add_argument(
        "--item-key",
        required=True,
        help="Zotero 条目 key，例如 XBXJDM7G",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出 JSON 路径（默认 input/<item-key>.json）",
    )
    parser.add_argument(
        "--include-annotations",
        action="store_true",
        help="尝试提取子条目中的批注文本并写入证据字段。",
    )
    return parser.parse_args()


def get_env(name, required=True, default=None):
    value = os.getenv(name, default)
    if required and (value is None or not str(value).strip()):
        raise RuntimeError(f"缺少环境变量: {name}")
    return value


def pick_year(date_text):
    if not date_text:
        return DEFAULT_VALUE
    m = re.search(r"\b(19\d{2}|20\d{2})\b", date_text)
    return m.group(1) if m else DEFAULT_VALUE


def pick_venue(data):
    for key in (
        "publicationTitle",
        "proceedingsTitle",
        "conferenceName",
        "archive",
        "journalAbbreviation",
        "websiteTitle",
    ):
        value = (data.get(key) or "").strip()
        if value:
            return value
    return DEFAULT_VALUE


def creators_to_authors(creators):
    authors = []
    for c in creators or []:
        ctype = (c.get("creatorType") or "").lower()
        # 优先 author，其次保底接受其他作者相关角色。
        if ctype not in ("author", "presenter", "contributor"):
            continue

        if c.get("name"):
            name = str(c.get("name")).strip()
        else:
            first = str(c.get("firstName") or "").strip()
            last = str(c.get("lastName") or "").strip()
            name = f"{first} {last}".strip()
        if name:
            authors.append(name)

    if not authors:
        return [DEFAULT_VALUE]
    return authors


def infer_paper_type(title, abstract_text, tags):
    blob = " ".join([title or "", abstract_text or "", " ".join(tags or [])]).lower()
    if any(k in blob for k in ("survey", "review", "taxonomy", "overview", "systematic review")):
        return "survey"
    return "method"


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
    lines = [line for _, line in rows]
    return "\n".join(lines)


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


def collect_annotations(item_key, children, headers, library_type, user_id):
    # 1) 先收集主条目直接 children 里的 annotation（有些场景会有）
    collected = []
    direct = extract_annotations(children)
    if direct != DEFAULT_VALUE:
        collected.append(direct)

    # 2) 再下钻到每个 attachment 的 children（常见批注存放位置）
    for att_key in extract_attachment_keys(children):
        sub_url = (
            f"https://api.zotero.org/{library_type}s/{user_id}/items/"
            f"{parse.quote(att_key)}/children"
        )
        sub_children = http_get_json(sub_url, headers=headers)
        sub_ann = extract_annotations(sub_children)
        if sub_ann != DEFAULT_VALUE:
            collected.append(sub_ann)

    if not collected:
        return DEFAULT_VALUE
    return "\n".join(collected)


def build_payload(item_data, item_key, pdf_key, annotation_text):
    title = (item_data.get("title") or "").strip() or item_key
    abstract_text = (item_data.get("abstractNote") or "").strip() or DEFAULT_VALUE
    tags = normalize_tags(item_data.get("tags"))
    paper_type = infer_paper_type(title, abstract_text, tags)

    if not tags:
        tags = [paper_type]

    payload = {
        "title": title,
        "authors": creators_to_authors(item_data.get("creators")),
        "year": pick_year(item_data.get("date")),
        "venue": pick_venue(item_data),
        "doi": (item_data.get("DOI") or "").strip() or DEFAULT_VALUE,
        "paper_type": paper_type,
        "abstract": abstract_text,
        "zotero_item_key": item_key,
        "pdf_key": pdf_key,
        "tags": tags,
        "one_sentence_summary": DEFAULT_VALUE,
        "research_relation": DEFAULT_VALUE,
        "core_library_decision": "候选",
        "core_library_reason": DEFAULT_VALUE,
        "why_read": DEFAULT_VALUE,
        "core_problem": DEFAULT_VALUE,
        "survey_scope": DEFAULT_VALUE,
        "survey_taxonomy": DEFAULT_VALUE,
        "survey_key_papers": "- needs-check\n- needs-check\n- needs-check",
        "survey_gaps": DEFAULT_VALUE,
        "method_idea": DEFAULT_VALUE,
        "method_framework": DEFAULT_VALUE,
        "experiment_results": DEFAULT_VALUE,
        "zotero_annotations_and_evidence": (
            f"- Zotero item key: {item_key}\n- PDF key: {pdf_key}\n- 批注摘录:\n{annotation_text}"
            if annotation_text != DEFAULT_VALUE
            else f"- Zotero item key: {item_key}\n- PDF key: {pdf_key}\n- 批注摘录: {DEFAULT_VALUE}"
        ),
        "citable_materials": DEFAULT_VALUE,
        "core_library_review_plan": DEFAULT_VALUE,
        "my_assessment": DEFAULT_VALUE,
        "open_questions": DEFAULT_VALUE,
        "next_actions": DEFAULT_VALUE,
    }
    return payload


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

    headers = {
        "Zotero-API-Key": api_key,
        "Zotero-API-Version": "3",
    }

    item_url = f"https://api.zotero.org/{library_type}s/{user_id}/items/{parse.quote(item_key)}"
    item_resp = http_get_json(item_url, headers=headers)
    item_data = item_resp.get("data", {})
    if not item_data:
        raise RuntimeError(f"未读取到条目 data: {item_key}")

    children_url = f"https://api.zotero.org/{library_type}s/{user_id}/items/{parse.quote(item_key)}/children"
    children = http_get_json(children_url, headers=headers)
    pdf_key = extract_pdf_key(children)
    annotation_text = (
        collect_annotations(item_key, children, headers, library_type, user_id)
        if args.include_annotations
        else DEFAULT_VALUE
    )

    payload = build_payload(item_data, item_key, pdf_key, annotation_text)

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
