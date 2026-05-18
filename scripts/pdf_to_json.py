import argparse
import json
import re
import sys
import zlib
from pathlib import Path

from ai_enrich_json import enrich_data


DEFAULT_VALUE = "needs-check"


def parse_args():
    parser = argparse.ArgumentParser(
        description="从 PDF 抽取基础信息并生成 JSON，可选接入 AI 自动补全模块。"
    )
    parser.add_argument("pdf_path", help="PDF 路径")
    parser.add_argument(
        "--output",
        default=None,
        help="输出 JSON 路径（默认 input/<pdf文件名>.json）",
    )
    parser.add_argument(
        "--ai-summary",
        action="store_true",
        help="启用 AI 自动补全。不开启时仅输出脚本可抽取的信息。",
    )
    parser.add_argument(
        "--ai-fill-mode",
        choices=["key", "all"],
        default="all",
        help="AI补全模式：key=关键字段，all=全部模块字段（默认 all）",
    )
    parser.add_argument(
        "--ai-overwrite",
        action="store_true",
        help="AI补全时覆盖已有字段（建议与 all 一起用）",
    )
    return parser.parse_args()


def normalize_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def decode_pdf_literal(raw):
    out = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue

        i += 1
        if i >= len(raw):
            break

        esc = raw[i]
        mapping = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f", "\\": "\\", "(": "(", ")": ")"}
        if esc in mapping:
            out.append(mapping[esc])
            i += 1
            continue

        # PDF literal octal escapes only allow digits 0-7.
        if esc in "01234567":
            oct_digits = esc
            i += 1
            for _ in range(2):
                if i < len(raw) and raw[i] in "01234567":
                    oct_digits += raw[i]
                    i += 1
                else:
                    break
            try:
                out.append(chr(int(oct_digits, 8)))
            except ValueError:
                out.append(oct_digits)
            continue

        out.append(esc)
        i += 1
    return "".join(out)


def extract_text_from_decoded_stream(stream_text):
    snippets = []

    for block in re.findall(r"BT(.*?)ET", stream_text, flags=re.S):
        for m in re.finditer(r"\((?:\\.|[^\\)])*\)\s*T[Jj]", block, flags=re.S):
            literal = m.group(0)
            literal = literal.rsplit(")", 1)[0][1:]
            snippets.append(decode_pdf_literal(literal))

        for arr in re.finditer(r"\[(.*?)\]\s*TJ", block, flags=re.S):
            items = re.findall(r"\((?:\\.|[^\\)])*\)", arr.group(1), flags=re.S)
            joined = "".join(decode_pdf_literal(item[1:-1]) for item in items)
            if joined:
                snippets.append(joined)

    if snippets:
        return "\n".join(snippets)

    rough = re.findall(r"\(([^)]{3,2000})\)", stream_text, flags=re.S)
    return "\n".join(decode_pdf_literal(x) for x in rough)


def extract_text_from_pdf_bytes(pdf_bytes):
    chunks = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, flags=re.S):
        raw_stream = match.group(1)
        try:
            decoded = zlib.decompress(raw_stream)
        except Exception:
            decoded = raw_stream

        text = decoded.decode("latin-1", errors="ignore")
        extracted = extract_text_from_decoded_stream(text)
        if extracted.strip():
            chunks.append(extracted)

    return normalize_text("\n\n".join(chunks))


def extract_text(pdf_path):
    data = pdf_path.read_bytes()
    return extract_text_from_pdf_bytes(data)


def guess_title(text, fallback_name):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    head = lines[:30]
    bad_keywords = ("arxiv", "doi", "copyright", "abstract", "keywords", "accepted")

    scored = []
    for idx, line in enumerate(head):
        lowered = line.lower()
        if any(k in lowered for k in bad_keywords):
            continue
        if len(line) < 12 or len(line) > 220:
            continue
        if re.search(r"[A-Za-z]", line):
            score = 0
            score += max(0, 20 - idx)
            if not line.endswith("."):
                score += 6
            if ":" in line:
                score += 3
            if line[:1].isupper():
                score += 2
            if re.search(r"\b(we|this paper|the paper|demonstrates|present|propose)\b", lowered):
                score -= 8
            if len(line.split()) > 25:
                score -= 3
            scored.append((score, line))

    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    return fallback_name.replace("_", " ").replace("-", " ")


def guess_authors(text, title):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    try:
        t_idx = next(i for i, line in enumerate(lines[:60]) if title[:30] in line[:80] or line[:30] in title[:80])
    except StopIteration:
        t_idx = 0

    window = lines[t_idx + 1 : t_idx + 8]
    block = " ".join(window)
    block = re.split(r"\babstract\b", block, maxsplit=1, flags=re.I)[0]
    block = block.replace(" and ", ", ")
    tokens = [x.strip() for x in block.split(",")]

    authors = []
    for token in tokens:
        token = re.sub(r"\s+", " ", token)
        if len(token.split()) < 2 or len(token.split()) > 5:
            continue
        if re.search(r"\d|@|university|school|department|institute", token, flags=re.I):
            continue
        if token and re.search(r"[A-Za-z]", token):
            authors.append(token)

    if not authors:
        return [DEFAULT_VALUE]
    return authors[:20]


def guess_abstract(text):
    m = re.search(
        r"(?is)\babstract\b\s*[:\-—]?\s*(.+?)(?=\n\s*(?:keywords?|index terms|1[\.\s]+introduction|introduction)\b)",
        text,
    )
    if m:
        return normalize_text(m.group(1))

    m2 = re.search(r"(?is)\babstract\b\s*[:\-—]?\s*(.+)", text)
    if m2:
        return normalize_text(m2.group(1)[:1200])
    return DEFAULT_VALUE


def guess_doi(text):
    m = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", text, flags=re.I)
    return m.group(0) if m else DEFAULT_VALUE


def guess_venue_and_year(text, pdf_name):
    arxiv = re.search(r"arXiv\s*:\s*(\d{4}\.\d{4,5})(?:v\d+)?(?:\s*\[([^\]]+)\])?", text, flags=re.I)
    if arxiv:
        arxiv_id = arxiv.group(1)
        category = arxiv.group(2) or "cs"
        year = f"20{arxiv_id[:2]}"
        venue = f"arXiv:{arxiv_id} [{category}]"
        return venue, year

    years = re.findall(r"\b(19\d{2}|20\d{2})\b", text[:4000])
    if years:
        valid = [y for y in years if 1990 <= int(y) <= 2035]
        if valid:
            return DEFAULT_VALUE, str(max(int(y) for y in valid))

    from_name = re.search(r"(19\d{2}|20\d{2})", pdf_name)
    if from_name:
        return DEFAULT_VALUE, from_name.group(1)

    return DEFAULT_VALUE, DEFAULT_VALUE


def guess_paper_type(title, abstract):
    blob = f"{title}\n{abstract}".lower()
    if any(k in blob for k in ("survey", "review", "taxonomy", "overview", "systematic review")):
        return "survey"
    return "method"


def build_base_json(pdf_path):
    text = extract_text(pdf_path)
    title = guess_title(text, pdf_path.stem)
    abstract = guess_abstract(text)
    venue, year = guess_venue_and_year(text, pdf_path.stem)
    paper_type = guess_paper_type(title, abstract)
    doi = guess_doi(text)
    authors = guess_authors(text, title)

    tags = [paper_type]
    if paper_type == "survey":
        tags.extend(["taxonomy", "review-paper"])

    data = {
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "doi": doi,
        "paper_type": paper_type,
        "abstract": abstract,
        "zotero_item_key": DEFAULT_VALUE,
        "pdf_key": DEFAULT_VALUE,
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
        "zotero_annotations_and_evidence": DEFAULT_VALUE,
        "citable_materials": DEFAULT_VALUE,
        "core_library_review_plan": DEFAULT_VALUE,
        "my_assessment": DEFAULT_VALUE,
        "open_questions": DEFAULT_VALUE,
        "next_actions": DEFAULT_VALUE,
    }
    return data


def sanitize_stem(name):
    sanitized = re.sub(r"[^\w\-]+", "_", name, flags=re.U)
    sanitized = sanitized.strip("_")
    return sanitized or "paper"


def main():
    args = parse_args()
    pdf_path = Path(args.pdf_path).expanduser().resolve()
    if not pdf_path.exists():
        print(f"未找到PDF: {pdf_path}")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    default_output = repo_root / "input" / f"{sanitize_stem(pdf_path.stem)}.json"
    output_path = Path(args.output).expanduser().resolve() if args.output else default_output

    data = build_base_json(pdf_path)

    if args.ai_summary:
        # 用户选择 AI 时，默认尽量填满所有模块字段。
        fill_mode = args.ai_fill_mode or "all"
        data, filled = enrich_data(
            data=data,
            overwrite=True if fill_mode == "all" else args.ai_overwrite,
            fill_mode=fill_mode,
        )
        print("AI 已回填字段: " + (", ".join(filled) if filled else "无"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已生成 JSON: {output_path}")
    print("下一步运行: python scripts/generate_note.py " + str(output_path))


if __name__ == "__main__":
    main()
