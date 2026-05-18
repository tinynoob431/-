import json
import re
import sys
from pathlib import Path


DEFAULT_VALUE = "needs-check"


def normalize_value(value):
    if value is None:
        return DEFAULT_VALUE
    if isinstance(value, str):
        text = value.strip()
        return text if text else DEFAULT_VALUE
    if isinstance(value, (int, float)):
        return str(value)
    return value


def yaml_inline_list(value):
    if not isinstance(value, list) or not value:
        return f'["{DEFAULT_VALUE}"]'
    cleaned = []
    for item in value:
        text = str(normalize_value(item)).replace('"', '\\"')
        cleaned.append(f'"{text}"')
    return "[" + ", ".join(cleaned) + "]"


def markdown_bullet_list(value):
    if isinstance(value, list):
        if not value:
            return DEFAULT_VALUE
        return "\n".join(f"- {normalize_value(item)}" for item in value)
    return normalize_value(value)


def markdown_numbered_list(value):
    if isinstance(value, list):
        if not value:
            return DEFAULT_VALUE
        return "\n".join(f"{i}. {normalize_value(item)}" for i, item in enumerate(value, 1))
    return normalize_value(value)


def plain_list_text(value):
    if not isinstance(value, list) or not value:
        return DEFAULT_VALUE
    return ", ".join(str(normalize_value(item)) for item in value)


def render_template(template_text, context):
    pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    def replacer(match):
        key = match.group(1)
        return str(context.get(key, DEFAULT_VALUE))

    return pattern.sub(replacer, template_text)


def sanitize_filename(name):
    invalid_chars = '<>:"/\\|?*'
    sanitized = "".join("_" if ch in invalid_chars else ch for ch in name).strip()
    return sanitized or "generated_note"


def build_output_filename(title):
    title_text = normalize_value(title)
    if title_text == DEFAULT_VALUE:
        return "generated_note.md"
    base = title_text.split(":", 1)[0].strip()
    return f"{sanitize_filename(base)}.md"


def build_context(data):
    context = {}

    # 直接透传所有输入字段，缺失时统一兜底为 needs-check。
    for key in data.keys():
        context[key] = normalize_value(data.get(key))

    list_yaml_map = {
        "aliases_yaml": "aliases",
        "authors_yaml": "authors",
        "tags_yaml": "tags",
        "zotero_collections_yaml": "zotero_collections",
        "zotero_tags_yaml": "zotero_tags",
        "canonical_tags_yaml": "canonical_tags",
        "candidate_tags_yaml": "candidate_tags",
    }
    for ctx_key, data_key in list_yaml_map.items():
        context[ctx_key] = yaml_inline_list(data.get(data_key))

    context["authors_text"] = plain_list_text(data.get("authors"))
    context["zotero_collections_text"] = plain_list_text(data.get("zotero_collections"))
    context["zotero_tags_text"] = plain_list_text(data.get("zotero_tags"))

    # 列表型字段自动转为 Markdown 列表，便于模板直接渲染。
    context["open_questions"] = markdown_bullet_list(data.get("open_questions"))
    context["survey_key_papers"] = markdown_bullet_list(data.get("survey_key_papers"))
    context["next_actions"] = markdown_numbered_list(data.get("next_actions"))

    # 模板中常用但输入可能不存在的字段，统一补默认值。
    must_have = [
        "title",
        "year",
        "venue",
        "doi",
        "paper_type",
        "status",
        "zotero_item_key",
        "pdf_key",
        "one_sentence_summary",
        "core_library_decision",
        "core_library_reason",
        "research_relation",
        "zotero_annotations_and_evidence",
    ]
    for key in must_have:
        context[key] = normalize_value(context.get(key))

    if context["status"] == DEFAULT_VALUE:
        context["status"] = "seed"

    return context


def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    input_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else repo_root / "input" / "graph_agent_memory.json"
    template_path = repo_root / "templates" / "literature_note_template.md"
    output_dir = repo_root / "output"

    with input_path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    with template_path.open("r", encoding="utf-8-sig") as f:
        template_text = f.read()

    context = build_context(data)
    content = render_template(template_text, context)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / build_output_filename(context.get("title"))
    output_path.write_text(content, encoding="utf-8")

    print(f"已生成：{output_path}")


if __name__ == "__main__":
    main()
