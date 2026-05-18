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
        item_text = str(normalize_value(item)).replace('"', '\\"')
        cleaned.append(f'"{item_text}"')
    return "[" + ", ".join(cleaned) + "]"


def markdown_list(value):
    if not isinstance(value, list) or not value:
        return DEFAULT_VALUE
    return "\n".join(f"- {normalize_value(item)}" for item in value)


def get_field(data, key):
    return normalize_value(data.get(key, DEFAULT_VALUE))


def build_context(data):
    context = {}

    simple_keys = [
        "title",
        "year",
        "venue",
        "doi",
        "paper_type",
        "abstract",
        "zotero_item_key",
        "pdf_key",
        "one_sentence_summary",
        "research_relation",
        "core_library_decision",
        "core_library_reason",
    ]
    for key in simple_keys:
        context[key] = get_field(data, key)

    context["authors_yaml"] = yaml_inline_list(data.get("authors"))
    context["tags_yaml"] = yaml_inline_list(data.get("tags"))

    optional_keys = [
        "why_read",
        "core_problem",
        "survey_scope",
        "survey_taxonomy",
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
    for key in optional_keys:
        context[key] = get_field(data, key)

    survey_key_papers_value = data.get("survey_key_papers")
    if isinstance(survey_key_papers_value, list):
        context["survey_key_papers"] = markdown_list(survey_key_papers_value)
    else:
        context["survey_key_papers"] = get_field(data, "survey_key_papers")

    if context["paper_type"].lower() == "survey":
        if context["method_idea"] == DEFAULT_VALUE:
            context["method_idea"] = "N/A（综述论文）"
        if context["method_framework"] == DEFAULT_VALUE:
            context["method_framework"] = "N/A（综述论文）"
        if context["experiment_results"] == DEFAULT_VALUE:
            context["experiment_results"] = "N/A（综述论文，不编造具体实验数值）"

    return context


def render_template(template_text, context):
    pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    def replacer(match):
        key = match.group(1)
        value = context.get(key, DEFAULT_VALUE)
        return str(value)

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
