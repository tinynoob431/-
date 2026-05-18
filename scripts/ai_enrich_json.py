import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path
from urllib import error, request


DEFAULT_VALUE = "needs-check"
FIELD_BATCH_SIZE = 24

KEY_FIELDS = [
    "one_sentence_summary",
    "why_read",
    "core_problem",
    "my_assessment",
    "open_questions",
    "next_actions",
]

ALL_MODULE_FIELDS = [
    "one_sentence_summary",
    "research_relation",
    "core_library_decision",
    "core_library_reason",
    "why_read",
    "core_problem",
    "core_bottleneck",
    "other_methods",
    "method_one_liner",
    "main_contributions",
    "headline_results",
    "application_scenarios",
    "main_limitations",
    "method_idea",
    "training_strategy",
    "inference_pipeline",
    "key_equations",
    "equation_symbols",
    "equation_role",
    "equation_vs_baseline",
    "datasets",
    "backbone",
    "baselines",
    "metrics",
    "main_results_table_or_text",
    "ablation_results",
    "efficiency_cost",
    "error_analysis",
    "citable_background",
    "citable_gap",
    "citable_method_compare",
    "citable_experiment",
    "citable_limitation",
    "core_library_review_plan",
    "my_assessment",
    "open_questions",
    "next_actions",
]

# 这些字段通常来自外部系统或脚本抽取；如果已有有效值，默认不覆盖。
NON_OVERWRITABLE_IF_PRESENT_FIELDS = {
    "zotero_item_key",
    "pdf_key",
    "framework_image_path",
    "framework_source",
    "framework_type",
}

# 对这些高风险字段，要求 AI 仅在“确定正确”时填写，否则必须写 needs-check。
HIGH_RISK_FIELDS = {
    "zotero_item_key",
    "pdf_key",
    "zotero_annotations_and_evidence",
    "framework_image_path",
    "framework_source",
    "framework_type",
    "framework_needs_check",
    "key_equations",
    "equation_symbols",
    "equation_role",
    "equation_vs_baseline",
}

# 这些字段通常需要逐页核对，同样按“确定才填，否则 needs-check”处理。
MANUAL_REVIEW_FIELDS = {
    "data_split",
    "seeds",
    "hyperparameters",
    "infra",
    "significance_and_variance",
    "code_availability",
    "data_availability",
    "repro_risks",
}
MANUAL_REVIEW_PREFIXES = ("evidence_",)
MANUAL_REVIEW_SUFFIXES = ("_source",)

# 这些字段偏“理解与总结”，允许基于上下文给出暂定草案，避免过度保守。
LOW_RISK_SYNTHESIS_FIELDS = {
    "one_sentence_summary",
    "research_relation",
    "core_library_reason",
    "why_read",
    "core_problem",
    "core_bottleneck",
    "other_methods",
    "method_one_liner",
    "main_contributions",
    "headline_results",
    "application_scenarios",
    "main_limitations",
    "core_modules",
    "pipeline_flow",
    "framework_explanation",
    "task_input",
    "task_output",
    "assumptions",
    "module_1",
    "module_2",
    "method_idea",
    "training_strategy",
    "inference_pipeline",
    "datasets",
    "backbone",
    "baselines",
    "metrics",
    "main_results_table_or_text",
    "ablation_results",
    "efficiency_cost",
    "error_analysis",
    "citable_background",
    "citable_gap",
    "citable_method_compare",
    "citable_experiment",
    "citable_limitation",
    "core_library_review_plan",
    "my_assessment",
    "open_questions",
    "next_actions",
}


def parse_args():
    parser = argparse.ArgumentParser(description="调用 OpenAI/DeepSeek 兼容 API 自动回填 JSON。")
    parser.add_argument("input_json", help="输入 JSON 路径")
    parser.add_argument("--output", default=None, help="输出 JSON 路径")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已有字段")
    parser.add_argument("--fill-mode", choices=["key", "all"], default="key", help="回填模式")
    parser.add_argument("--all-fields", action="store_true", help="回填输入 JSON 中的所有字段")
    parser.add_argument("--pdf-path", default=None, help="可选：本地 PDF 路径，用于抽取正文片段增强 AI 回填")
    parser.add_argument("--pdf-context-chars", type=int, default=12000, help="注入给 AI 的 PDF 文本片段最大字符数（默认 12000）")
    return parser.parse_args()


def get_env(name, required=True, default=None):
    value = os.getenv(name, default)
    if required and (value is None or not str(value).strip()):
        raise RuntimeError(f"缺少环境变量: {name}")
    return value


def value_is_empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        text = v.strip().lower()
        return text == "" or text == DEFAULT_VALUE
    return False


def is_high_risk_field(field):
    if field in HIGH_RISK_FIELDS or field in MANUAL_REVIEW_FIELDS:
        return True
    if any(field.startswith(prefix) for prefix in MANUAL_REVIEW_PREFIXES):
        return True
    if any(field.endswith(suffix) for suffix in MANUAL_REVIEW_SUFFIXES):
        return True
    return False


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


def extract_text_with_pdftotext(pdf_path):
    pdftotext_bin = shutil.which("pdftotext")
    if not pdftotext_bin:
        return ""
    cmd = [pdftotext_bin, "-layout", "-enc", "UTF-8", str(pdf_path), "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if proc.returncode != 0:
        return ""
    return normalize_text(proc.stdout)


def extract_text_from_pdf_path(pdf_path):
    text = extract_text_with_pdftotext(pdf_path)
    # pdftotext usually gives much cleaner spacing than raw stream parsing.
    if len(text) >= 2000:
        return text
    return extract_text_from_pdf_bytes(pdf_path.read_bytes())


def build_pdf_excerpt(raw_text, max_chars):
    text = normalize_text(raw_text or "")
    if not text:
        return ""
    max_chars = max(1000, int(max_chars))

    pieces = []
    seen = set()

    def add_piece(segment):
        segment = normalize_text(segment)
        if not segment:
            return
        if segment in seen:
            return
        seen.add(segment)
        pieces.append(segment)

    # Keep head context (often contains title/abstract/introduction).
    add_piece(text[: min(len(text), max_chars // 3)])

    lower = text.lower()
    anchors = [
        "abstract",
        "introduction",
        "method",
        "approach",
        "experiment",
        "evaluation",
        "benchmark",
        "dataset",
        "table",
        "ablation",
        "results",
        "conclusion",
        "limitation",
        "appendix",
        "摘要",
        "引言",
        "方法",
        "实验",
        "结果",
        "结论",
    ]
    window = 1800
    for key in anchors:
        positions = [m.start() for m in re.finditer(re.escape(key), lower)]
        if not positions:
            continue
        # Avoid exploding context: keep a few representative hits per anchor.
        if len(positions) > 6:
            positions = positions[:3] + positions[-3:]
        for idx in positions:
            start = max(0, idx - window // 2)
            end = min(len(text), idx + window)
            add_piece(text[start:end])

    # Sample middle/late sections to capture experiment details that are not near first anchors.
    for ratio in (0.35, 0.55, 0.75):
        center = int(len(text) * ratio)
        start = max(0, center - window // 2)
        end = min(len(text), center + window // 2)
        add_piece(text[start:end])

    # Keep tail context (often has discussion/limitations/conclusion).
    add_piece(text[-(max_chars // 5) :])

    joined = "\n\n[...]\n\n".join(pieces)
    return joined[:max_chars]


def load_pdf_excerpt(pdf_path, pdf_context_chars):
    if not pdf_path:
        return None, ""
    path = Path(pdf_path).expanduser().resolve()
    if not path.exists():
        raise RuntimeError(f"--pdf-path 指向的文件不存在: {path}")
    raw_text = extract_text_from_pdf_path(path)
    excerpt = build_pdf_excerpt(raw_text, pdf_context_chars)
    return path, excerpt


def iter_field_batches(fields, batch_size=FIELD_BATCH_SIZE):
    size = max(1, int(batch_size))
    for idx in range(0, len(fields), size):
        yield fields[idx : idx + size]


def default_base_url(provider):
    provider = provider.lower()
    if provider == "openai":
        return "https://api.openai.com"
    if provider == "deepseek":
        return "https://api.deepseek.com"
    return None


def default_model(provider):
    provider = provider.lower()
    if provider == "openai":
        return "gpt-4o-mini"
    if provider == "deepseek":
        return "deepseek-v4-pro"
    return None


def normalize_base_url(base_url):
    url = (base_url or "").strip()
    if not url:
        return url
    url = url.rstrip("/")
    # Avoid ending up with /v1/v1/chat/completions when user provides a /v1 base URL.
    if url.endswith("/v1"):
        url = url[: -len("/v1")]
    return url


def post_chat(base_url, api_key, model, messages):
    normalized_base = normalize_base_url(base_url)
    url = normalized_base + "/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }

    def do_request(body):
        req = request.Request(
            url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            obj = json.loads(raw)
            return obj["choices"][0]["message"]["content"]

    try:
        return do_request(payload)
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        # Some compatible gateways/providers reject response_format json_object.
        # Retry once without response_format to improve robustness.
        if e.code == 400:
            fallback_payload = dict(payload)
            fallback_payload.pop("response_format", None)
            try:
                return do_request(fallback_payload)
            except error.HTTPError as e2:
                detail2 = e2.read().decode("utf-8", errors="ignore")
                raise RuntimeError(
                    f"HTTP {e2.code}: {detail2}\n(request_url={url}, model={model}, retried_without_response_format=true)"
                ) from e2
            except error.URLError as e2:
                raise RuntimeError(
                    f"Network error: {e2}\n(request_url={url}, model={model}, retried_without_response_format=true)"
                ) from e2
        raise RuntimeError(f"HTTP {e.code}: {detail}\n(request_url={url}, model={model})") from e
    except error.URLError as e:
        raise RuntimeError(f"Network error: {e}\n(request_url={url}, model={model})") from e


def parse_model_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.I)
    text = re.sub(r"```$", "", text)
    return json.loads(text)


def build_messages(data, fields_to_fill, fill_mode, pdf_excerpt="", pdf_path=None):
    paper_info = {
        "title": data.get("title", DEFAULT_VALUE),
        "authors": data.get("authors", [DEFAULT_VALUE]),
        "year": data.get("year", DEFAULT_VALUE),
        "venue": data.get("venue", DEFAULT_VALUE),
        "doi": data.get("doi", DEFAULT_VALUE),
        "paper_type": data.get("paper_type", DEFAULT_VALUE),
        "abstract": data.get("abstract", DEFAULT_VALUE),
        "tags": data.get("tags", []),
        "zotero_annotations_and_evidence": data.get("zotero_annotations_and_evidence", DEFAULT_VALUE),
    }

    mode_rule = (
        "普通字段可基于标题、摘要、批注和正文片段做合理推断，优先给出可用草案；仅在确实无依据时填写 needs-check。"
        if fill_mode == "all"
        else "普通字段可做保守推断；信息不足时可填写 needs-check。"
    )
    high_risk_fields = [field for field in fields_to_fill if is_high_risk_field(field)]
    low_risk_synthesis_fields = [
        field for field in fields_to_fill if field in LOW_RISK_SYNTHESIS_FIELDS and field not in high_risk_fields
    ]
    experiment_focus_fields = [
        field
        for field in fields_to_fill
        if field in {"datasets", "backbone", "baselines", "metrics", "main_results_table_or_text", "ablation_results"}
    ]
    high_risk_rule = (
        (
            "以下字段属于高风险关键字段："
            + ", ".join(high_risk_fields)
            + "。只有在你能确定内容准确时才填写；如果有任何不确定，必须填写 needs-check，严禁猜测。"
        )
        if high_risk_fields
        else "本轮没有高风险字段，优先输出可用草案。"
    )
    low_risk_rule = (
        (
            "以下字段属于低风险总结字段："
            + ", ".join(low_risk_synthesis_fields)
            + "。除非完全没有线索，否则不要仅输出 needs-check；可使用“基于当前信息推断：...”的写法给出暂定结论。"
        )
        if low_risk_synthesis_fields
        else "普通字段若有任意线索，优先给出暂定结论。"
    )
    experiment_focus_rule = (
        (
            "以下实验字段需要优先从正文片段提取具体名词和数字："
            + ", ".join(experiment_focus_fields)
            + "。若片段中出现任务名/数据集名/baseline名/结果数字，请直接填写，不要写 needs-check。"
        )
        if experiment_focus_fields
        else ""
    )

    system = (
        "你是科研论文笔记助手。输出必须是严格 json 对象，不要输出任何额外文本。"
        "输出语言必须为中文。"
        + mode_rule
        + high_risk_rule
        + low_risk_rule
        + experiment_focus_rule
    )
    user = {
        "task": "回填论文笔记字段",
        "required_fields": fields_to_fill,
        "current_values_for_required_fields": {field: data.get(field, DEFAULT_VALUE) for field in fields_to_fill},
        "paper_info": paper_info,
        "pdf_context": {
            "pdf_path": str(pdf_path) if pdf_path else DEFAULT_VALUE,
            "pdf_excerpt": pdf_excerpt if pdf_excerpt else DEFAULT_VALUE,
        },
        "format_rules": {
            "open_questions": "使用 Markdown 项目符号列表，每行以 '- ' 开头",
            "next_actions": "使用编号列表，如 '1. ...'",
            "core_library_decision": "返回一个短词，如 candidate/include/exclude",
            "required_fields_completeness": "必须覆盖 required_fields 中的每个字段",
            "low_risk_placeholder_rule": "低风险总结字段如有线索，不要只写 needs-check",
        },
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
    ]


def enrich_data(
    data,
    overwrite=False,
    fill_mode="key",
    all_fields=False,
    provider=None,
    api_key=None,
    base_url=None,
    model=None,
    pdf_path=None,
    pdf_context_chars=12000,
):
    provider = (provider or os.getenv("AI_PROVIDER") or "deepseek").strip().lower()
    api_key = api_key or get_env("AI_API_KEY")
    base_url = base_url or os.getenv("AI_BASE_URL") or default_base_url(provider)
    model = model or os.getenv("AI_MODEL") or default_model(provider)
    if not base_url:
        raise RuntimeError("未知 provider，请设置 AI_BASE_URL")
    if not model:
        raise RuntimeError("未知 provider，请设置 AI_MODEL")

    if all_fields:
        target_fields = list(data.keys())
    else:
        target_fields = ALL_MODULE_FIELDS if fill_mode == "all" else KEY_FIELDS

    fields_to_fill = []
    for field in target_fields:
        if field in NON_OVERWRITABLE_IF_PRESENT_FIELDS and not value_is_empty(data.get(field)):
            continue
        if overwrite or value_is_empty(data.get(field)):
            fields_to_fill.append(field)

    if not fields_to_fill:
        return data, []

    resolved_pdf_path, pdf_excerpt = load_pdf_excerpt(pdf_path, pdf_context_chars)
    for batch in iter_field_batches(fields_to_fill):
        messages = build_messages(
            data=data,
            fields_to_fill=batch,
            fill_mode=fill_mode,
            pdf_excerpt=pdf_excerpt,
            pdf_path=resolved_pdf_path,
        )
        content = post_chat(base_url, api_key, model, messages)
        generated = parse_model_json(content)

        for field in batch:
            value = generated.get(field, DEFAULT_VALUE)
            if isinstance(value, str):
                value = value.strip() or DEFAULT_VALUE
            data[field] = value

    # Focused second pass for unresolved low-risk synthesis fields.
    unresolved_low_risk = [
        field
        for field in fields_to_fill
        if field in LOW_RISK_SYNTHESIS_FIELDS and value_is_empty(data.get(field))
    ]
    if unresolved_low_risk:
        messages = build_messages(
            data=data,
            fields_to_fill=unresolved_low_risk,
            fill_mode="all",
            pdf_excerpt=pdf_excerpt,
            pdf_path=resolved_pdf_path,
        )
        content = post_chat(base_url, api_key, model, messages)
        generated = parse_model_json(content)
        for field in unresolved_low_risk:
            value = generated.get(field, DEFAULT_VALUE)
            if isinstance(value, str):
                value = value.strip() or DEFAULT_VALUE
            data[field] = value

    return data, fields_to_fill


def main():
    args = parse_args()
    input_path = Path(args.input_json).expanduser().resolve()
    if not input_path.exists():
        raise RuntimeError(f"输入文件不存在: {input_path}")

    with input_path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    data, filled = enrich_data(
        data=data,
        overwrite=args.overwrite,
        fill_mode=args.fill_mode,
        all_fields=args.all_fields,
        pdf_path=args.pdf_path,
        pdf_context_chars=args.pdf_context_chars,
    )
    if not filled:
        print("无需回填：目标字段已有内容。")
        return

    output_path = Path(args.output).expanduser().resolve() if args.output else input_path.with_name(input_path.stem + "_enriched.json")
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 enriched JSON: {output_path}")
    print("已回填字段: " + ", ".join(filled))
    print(f"下一步可运行: python scripts/generate_note.py {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"失败: {e}")
        sys.exit(1)
