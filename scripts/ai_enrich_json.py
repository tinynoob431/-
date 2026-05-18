import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib import error, request


DEFAULT_VALUE = "needs-check"


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
    "survey_scope",
    "survey_taxonomy",
    "survey_key_papers",
    "survey_gaps",
    "method_idea",
    "method_framework",
    "experiment_results",
    "zotero_annotations_and_evidence",
    "citable_materials",
    "core_library_review_plan",
    "my_assessment",
    "open_questions",
    "next_actions",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="调用 OpenAI/DeepSeek 兼容 API 自动回填 JSON。"
    )
    parser.add_argument("input_json", help="输入 JSON 路径")
    parser.add_argument("--output", default=None, help="输出 JSON 路径")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已有字段")
    parser.add_argument(
        "--fill-mode",
        choices=["key", "all"],
        default="key",
        help="key=只填关键字段；all=尽量填满所有模块字段",
    )
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
        return "deepseek-chat"
    return None


def post_chat(base_url, api_key, model, messages):
    url = base_url.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            obj = json.loads(raw)
            return obj["choices"][0]["message"]["content"]
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e
    except error.URLError as e:
        raise RuntimeError(f"Network error: {e}") from e


def parse_model_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.I)
    text = re.sub(r"```$", "", text)
    return json.loads(text)


def build_messages(data, fields_to_fill, fill_mode):
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

    if fill_mode == "all":
        extra_rule = (
            "你必须尽量为每个字段生成完整内容，不要输出 needs-check。"
            "允许基于论文标题、摘要和常见研究写作范式进行合理扩展。"
        )
    else:
        extra_rule = (
            "如果信息不足可写 needs-check，保持保守。"
        )

    system = (
        "你是科研文献笔记助手。输出必须是严格 JSON 对象，不要输出任何额外文本。"
        "输出语言必须为中文。"
        + extra_rule
    )

    user = {
        "task": "回填论文笔记字段",
        "required_fields": fields_to_fill,
        "paper_info": paper_info,
        "field_format_rules": {
            "survey_key_papers": "使用Markdown项目符号列表，每行以'- '开头",
            "open_questions": "使用Markdown项目符号列表，每行以'- '开头",
            "next_actions": "使用编号列表，格式如'1. ...'",
            "core_library_decision": "返回一个简短决策词，例如 候选/纳入/排除",
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
    provider=None,
    api_key=None,
    base_url=None,
    model=None,
):
    provider = (provider or os.getenv("AI_PROVIDER") or "openai").strip().lower()
    api_key = api_key or get_env("AI_API_KEY")
    base_url = base_url or os.getenv("AI_BASE_URL") or default_base_url(provider)
    model = model or os.getenv("AI_MODEL") or default_model(provider)

    if not base_url:
        raise RuntimeError("未知 provider，请设置 AI_BASE_URL")
    if not model:
        raise RuntimeError("未知 provider，请设置 AI_MODEL")

    target_fields = ALL_MODULE_FIELDS if fill_mode == "all" else KEY_FIELDS
    fields_to_fill = []
    for field in target_fields:
        if overwrite or value_is_empty(data.get(field)):
            fields_to_fill.append(field)

    if not fields_to_fill:
        return data, []

    messages = build_messages(data, fields_to_fill, fill_mode)
    content = post_chat(base_url, api_key, model, messages)
    generated = parse_model_json(content)

    for field in fields_to_fill:
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
    )

    if not filled:
        print("无需回填：目标字段已有内容。")
        return

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_name(input_path.stem + "_enriched.json")
    )
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
