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
PAPER_SUBTYPE_CHOICES = (
    "survey",
    "method",
    "system",
    "benchmark",
    "dataset",
    "empirical",
    "theory",
    "application",
)
PAPER_SUBTYPE_ALIASES = {
    "review": "survey",
    "literature-review": "survey",
    "survey-paper": "survey",
    "model": "method",
    "framework": "method",
    "pipeline": "method",
    "architecture": "system",
    "system-paper": "system",
    "leaderboard": "benchmark",
    "benchmarking": "benchmark",
    "dataset-paper": "dataset",
    "data-paper": "dataset",
    "experiment": "empirical",
    "experimental": "empirical",
    "empirically": "empirical",
    "analysis": "theory",
    "analytical": "theory",
    "proof": "theory",
    "applied": "application",
    "real-world": "application",
}
STRICT_FACT_FIELDS = {
    "datasets",
    "backbone",
    "baselines",
    "metrics",
    "main_results_table_or_text",
    "ablation_results",
    "efficiency_cost",
    "training_strategy",
    "inference_pipeline",
    "key_equations",
    "equation_symbols",
    "equation_role",
    "equation_vs_baseline",
    "most_important_figure_or_table",
    "framework_source",
    "framework_type",
}
NO_GUESS_PATTERNS = (
    "基于当前信息推断",
    "推断",
    "可能",
    "可能为",
    "可能包括",
    "猜测",
    "估计",
    "未明确",
    "maybe",
    "likely",
    "possibly",
    "could be",
    "might be",
    "may include",
)
NEEDS_CHECK_HINTS = {
    "datasets": "needs-check",
    "backbone": "needs-check",
    "baselines": "needs-check",
    "metrics": "needs-check",
    "main_results_table_or_text": "needs-check",
    "ablation_results": "needs-check",
    "efficiency_cost": "needs-check",
    "training_strategy": "needs-check",
    "inference_pipeline": "needs-check",
    "key_equations": "needs-check",
    "equation_symbols": "needs-check",
    "equation_role": "needs-check",
    "equation_vs_baseline": "needs-check",
    "most_important_figure_or_table": "needs-check",
    "framework_source": "needs-check",
    "framework_type": "needs-check",
}

KEY_FIELDS = [
    "tags",
    "canonical_tags",
    "candidate_tags",
    "one_sentence_summary",
    "why_read",
    "core_problem",
    "my_assessment",
    "open_questions",
    "next_actions",
]

ALL_MODULE_FIELDS = [
    "tags",
    "canonical_tags",
    "candidate_tags",
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
    "paper_subtype",
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
    "result_reliability",
    "most_important_figure_or_table",
    "figure_table_takeaway",
    "ablation_results",
    "efficiency_cost",
    "error_analysis",
    "citable_background",
    "citable_gap",
    "citable_method_compare",
    "citable_experiment",
    "citable_limitation",
    "worth_deep_reading",
    "value_for_my_research",
    "what_to_reuse",
    "what_to_ignore",
    "core_library_review_plan",
    "my_assessment",
    "high_priority_checks",
    "open_questions",
    "next_actions",
]

NON_OVERWRITABLE_IF_PRESENT_FIELDS = {
    "zotero_item_key",
    "pdf_key",
    "framework_image_path",
    "framework_source",
    "framework_type",
}

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

LOW_RISK_SYNTHESIS_FIELDS = {
    "tags",
    "canonical_tags",
    "candidate_tags",
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
    "paper_subtype",
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
    "result_reliability",
    "most_important_figure_or_table",
    "figure_table_takeaway",
    "ablation_results",
    "efficiency_cost",
    "error_analysis",
    "citable_background",
    "citable_gap",
    "citable_method_compare",
    "citable_experiment",
    "citable_limitation",
    "worth_deep_reading",
    "value_for_my_research",
    "what_to_reuse",
    "what_to_ignore",
    "core_library_review_plan",
    "my_assessment",
    "high_priority_checks",
    "open_questions",
    "next_actions",
}

CHINESE_POLISH_FIELDS = {
    "one_sentence_summary",
    "why_read",
    "core_problem",
    "core_bottleneck",
    "other_methods",
    "method_one_liner",
    "main_contributions",
    "headline_results",
    "main_limitations",
    "method_idea",
    "training_strategy",
    "inference_pipeline",
    "result_reliability",
    "figure_table_takeaway",
    "core_modules",
    "pipeline_flow",
    "task_input",
    "task_output",
    "assumptions",
    "module_1",
    "module_2",
    "framework_explanation",
    "main_results_table_or_text",
    "value_for_my_research",
    "what_to_reuse",
    "what_to_ignore",
    "research_relation",
    "high_priority_checks",
    "next_actions",
    "open_questions",
    "core_library_reason",
}

TAG_CANONICAL_MAP = {
    "llm-agents": "llm-agent",
    "llm-agentic": "llm-agent",
    "chain-of-thoughts": "chain-of-thought",
    "few-shot-prompting": "prompting",
}

TAG_CANDIDATE_HINTS = (
    ("react", "react"),
    ("chain-of-thought", "chain-of-thought"),
    ("cot", "chain-of-thought"),
    ("interactive decision", "interactive-decision-making"),
    ("alfworld", "interactive-decision-making"),
    ("webshop", "interactive-decision-making"),
    ("hotpot", "knowledge-intensive-qa"),
    ("fever", "knowledge-intensive-qa"),
    ("memory trigger", "memory-trigger"),
    ("memory weaver", "memory-weaver"),
    ("latent token", "latent-token"),
    ("reinforcement learning", "reinforcement-learning"),
    ("self-evolving", "self-evolution"),
    ("self evolution", "self-evolution"),
    ("记忆触发", "memory-trigger"),
    ("记忆编织", "memory-weaver"),
    ("潜在 token", "latent-token"),
    ("潜在记忆", "latent-memory"),
    ("自进化", "self-evolution"),
)


def parse_args():
    parser = argparse.ArgumentParser(description="Fill paper-note JSON fields via OpenAI/DeepSeek-compatible API.")
    parser.add_argument("input_json", help="Input JSON path")
    parser.add_argument("--output", default=None, help="Output JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing values")
    parser.add_argument("--fill-mode", choices=["key", "all"], default="key", help="Fill mode")
    parser.add_argument("--all-fields", action="store_true", help="Fill all fields in the input JSON")
    parser.add_argument("--pdf-path", default=None, help="Optional local PDF path for stronger context")
    parser.add_argument(
        "--pdf-context-chars",
        type=int,
        default=12000,
        help="Max characters of PDF context to inject into the model",
    )
    return parser.parse_args()


def get_env(name, required=True, default=None):
    value = os.getenv(name, default)
    if required and (value is None or not str(value).strip()):
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def value_is_empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        text = v.strip().lower()
        return text == "" or text == DEFAULT_VALUE
    return False


def is_garbled_text(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    # Common corruption signals from encoding mismatch / placeholder bursts.
    if "???" in text:
        return True
    q_count = text.count("?")
    if q_count >= 3 and (q_count / max(1, len(text))) > 0.08:
        return True
    return False


def normalize_paper_subtype(value, paper_type=DEFAULT_VALUE):
    if value is None:
        return DEFAULT_VALUE

    raw = str(value).strip().lower()
    if not raw or raw == DEFAULT_VALUE:
        inferred_type = str(paper_type or "").strip().lower()
        return "survey" if inferred_type == "survey" else DEFAULT_VALUE

    # Normalize separators and capture potential english tokens.
    compact = raw.replace("_", "-")
    compact = re.sub(r"[\s/|,;，。]+", " ", compact)
    tokens = re.findall(r"[a-z\-]+", compact)

    for token in tokens:
        if token in PAPER_SUBTYPE_CHOICES:
            return token
        if token in PAPER_SUBTYPE_ALIASES:
            return PAPER_SUBTYPE_ALIASES[token]

    for choice in PAPER_SUBTYPE_CHOICES:
        if choice in compact:
            return choice
    for alias, mapped in PAPER_SUBTYPE_ALIASES.items():
        if alias in compact:
            return mapped

    inferred_type = str(paper_type or "").strip().lower()
    return "survey" if inferred_type == "survey" else DEFAULT_VALUE


def contains_no_guess_pattern(value):
    text = str(value or "").strip().lower()
    if not text:
        return False
    return any(token in text for token in NO_GUESS_PATTERNS)


def needs_check_fallback(field):
    return NEEDS_CHECK_HINTS.get(field, DEFAULT_VALUE)


def sanitize_key_equations_value(value):
    src = str(value or "").strip()
    if not src or src.lower() == DEFAULT_VALUE:
        return needs_check_fallback("key_equations")
    lines = [ln.strip() for ln in src.splitlines() if ln.strip()]
    cleaned = []
    for ln in lines:
        cl = _clean_equation_line(ln)
        if _looks_equation_line(cl):
            cleaned.append(cl)
    cleaned = dedupe_keep_order(cleaned)
    if not cleaned:
        return "needs-check: 公式文本抽取噪声较高，未识别到可靠公式行。"
    return "\n".join(cleaned[:3])


def sanitize_generated_value(field, value, paper_type=DEFAULT_VALUE):
    if isinstance(value, str):
        value = value.strip() or DEFAULT_VALUE

    if field == "paper_subtype":
        return normalize_paper_subtype(value, paper_type)

    if field == "key_equations":
        return sanitize_key_equations_value(value)

    if field in STRICT_FACT_FIELDS:
        if value_is_empty(value):
            return needs_check_fallback(field)
        if contains_no_guess_pattern(value):
            return needs_check_fallback(field)
        if is_garbled_text(value):
            return needs_check_fallback(field)

    if isinstance(value, str):
        # Normalize odd punctuation tails from model output.
        value = re.sub(r"[;；]+\s*[。.!?！？]?$", "", value.strip())
        # Convert JSON-like object strings into readable plain text for human-facing fields.
        if value.startswith("{") and value.endswith("}") and field in {
            "module_1",
            "module_2",
            "equation_symbols",
            "equation_role",
            "core_modules",
            "pipeline_flow",
        }:
            try:
                obj = json.loads(value)
            except Exception:
                obj = None
            if isinstance(obj, dict):
                pairs = []
                for k, v in obj.items():
                    key = str(k).strip()
                    val = str(v).strip()
                    if key and val:
                        pairs.append(f"{key}：{val}")
                if pairs:
                    value = "；".join(pairs)

    return value


def is_high_risk_field(field):
    if field in HIGH_RISK_FIELDS or field in MANUAL_REVIEW_FIELDS:
        return True
    if any(field.startswith(prefix) for prefix in MANUAL_REVIEW_PREFIXES):
        return True
    if any(field.endswith(suffix) for suffix in MANUAL_REVIEW_SUFFIXES):
        return True
    return False


def normalize_tag_token(value):
    text = str(value or "").strip().lower()
    if not text or text == DEFAULT_VALUE:
        return ""
    text = text.replace("/", " ")
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return TAG_CANONICAL_MAP.get(text, text)


def normalize_tag_list(values):
    if not isinstance(values, list):
        return []
    out = []
    seen = set()
    for item in values:
        token = normalize_tag_token(item)
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def dedupe_keep_order(values):
    out = []
    seen = set()
    for item in values:
        token = str(item or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def build_candidate_tag_suggestions(data):
    text = " ".join(
        str(data.get(key, ""))
        for key in (
            "title",
            "abstract",
            "one_sentence_summary",
            "method_one_liner",
            "core_modules",
            "evidence_method",
            "citable_method_compare",
        )
    ).lower()
    suggestions = []
    for key, token in TAG_CANDIDATE_HINTS:
        if key in text:
            suggestions.append(token)
    return dedupe_keep_order(suggestions)


def contains_cjk(text):
    return bool(re.search(r"[\u4e00-\u9fff]", str(text or "")))


def english_letter_ratio(text):
    text = str(text or "")
    letters = re.findall(r"[A-Za-z]", text)
    visible = re.findall(r"[A-Za-z\u4e00-\u9fff]", text)
    if not visible:
        return 0.0
    return len(letters) / len(visible)


_MOJIBAKE_MARKERS = ("鎻", "鍙", "鐨", "鏈", "锛", "銆", "浠", "鏂", "瀛", "鍥", "璁")


def _zh_readability_score(text):
    common = "的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等模型方法实验结果数据训练推理工具"
    return sum(text.count(ch) for ch in common)


def maybe_fix_mojibake_text(text):
    src = str(text or "")
    if not src:
        return src
    if not any(m in src for m in _MOJIBAKE_MARKERS):
        return src

    best = src
    best_score = _zh_readability_score(src)
    for enc in ("gb18030", "gbk"):
        try:
            fixed = src.encode(enc, errors="strict").decode("utf-8", errors="strict")
        except Exception:
            continue
        score = _zh_readability_score(fixed)
        if score > best_score + 3:
            best, best_score = fixed, score
    return best


def fix_mojibake_in_data(value):
    if isinstance(value, str):
        return maybe_fix_mojibake_text(value)
    if isinstance(value, list):
        return [fix_mojibake_in_data(v) for v in value]
    if isinstance(value, dict):
        return {k: fix_mojibake_in_data(v) for k, v in value.items()}
    return value


def needs_chinese_polish(field, value):
    if field not in CHINESE_POLISH_FIELDS:
        return False
    if value_is_empty(value):
        return False
    text = str(value)
    if text.strip().lower().startswith("needs-check"):
        return False
    if contains_cjk(text) and english_letter_ratio(text) < 0.55:
        return False
    return english_letter_ratio(text) >= 0.55


def sanitize_tags_block(data):
    tags = normalize_tag_list(data.get("tags"))
    canonical = normalize_tag_list(data.get("canonical_tags"))
    candidate = normalize_tag_list(data.get("candidate_tags"))
    if not tags:
        tags = [DEFAULT_VALUE]
    if not canonical:
        canonical = [DEFAULT_VALUE]
    if not candidate:
        candidate = []

    # Candidate tags = AI output + deterministic suggestion hints.
    suggestions = build_candidate_tag_suggestions(data)
    for token in suggestions:
        if token not in candidate and len(candidate) < 8:
            candidate.append(token)
    if not candidate:
        candidate = [DEFAULT_VALUE]

    tags = dedupe_keep_order(tags)
    canonical = dedupe_keep_order(canonical)
    candidate = dedupe_keep_order(candidate)

    data["tags"] = tags
    data["canonical_tags"] = canonical
    data["candidate_tags"] = candidate


def postprocess_generated_data(data):
    # Repair likely mojibake strings before downstream formatting.
    for k in list(data.keys()):
        data[k] = fix_mojibake_in_data(data.get(k))

    sanitize_tags_block(data)
    data["paper_subtype"] = normalize_paper_subtype(data.get("paper_subtype"), data.get("paper_type", DEFAULT_VALUE))
    # Avoid invalid wiki-image placeholders like `needs-check (...)`.
    for key in ("framework_image_path", "framework_source", "framework_type"):
        value = str(data.get(key, "")).strip()
        if re.match(r"(?i)^needs[- ]?check", value):
            data[key] = DEFAULT_VALUE

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


def _clean_equation_line(line):
    text = re.sub(r"\s+", " ", str(line or "")).strip(" .;，。")
    text = re.sub(r"\s+\(\d+\)\s*$", "", text)  # trim trailing equation number marker
    text = text.replace(":=", "=")
    text = text.replace("Mt", "M_t").replace("mt", "m_t")
    text = text.replace("Ht,<j", "H_{t,<j}")
    # Trim verbose sentence prefixes and keep the formula tail when possible.
    for rx in (
        r"(e\([^)]*\)\s*=.+)$",
        r"(m_t\s*=.+)$",
        r"(M_t\s*=.+)$",
        r"(z_\{t,j\}.+)$",
        r"(p_j\s*=.+)$",
        r"(L_i\s*=.+)$",
    ):
        m = re.search(rx, text, flags=re.I)
        if m:
            text = m.group(1).strip()
            break
    return text.strip()


def _looks_equation_line(line):
    text = re.sub(r"\s+", " ", str(line or "")).strip()
    if len(text) < 8 or len(text) > 240:
        return False
    if not any(op in text for op in ("=", ":=", "~", "∼")):
        return False
    # Avoid citation/statement noise lines like "... (Zhang et al., 2025a) ... t = 0 ..."
    if re.search(r"\bet al\.", text, flags=re.I):
        return False
    if re.search(r"\b(19|20)\d{2}[a-z]?\b", text) and not re.search(r"\(\d+\)\s*$", text):
        return False
    if re.search(r"[。.!?]$", text) and not re.search(r"\(\d+\)\s*$", text):
        return False
    math_signals = (
        r"(?:\bM_t\b|\bm_t\b|\bH_{?t\b|Wweaver|Ttrigger|p_j|σ|\\pi|pi_|R\(|E\(|z_\{t,j\}|d_j|s_t|τ|"
        r"e\([^)]*\)\s*=|L_i\s*=|<API>|</API>|->|→)"
    )
    has_signal = bool(re.search(math_signals, text, flags=re.I))
    if not has_signal:
        return False
    # Filter natural-language lines that only incidentally contain "=".
    long_words = re.findall(r"\b[A-Za-z]{3,}\b", text)
    if len(long_words) >= 10 and len(re.findall(math_signals, text, flags=re.I)) < 2:
        return False
    return True


def infer_equation_candidates(text):
    src = normalize_text(text or "")
    if not src:
        return []

    numbered = []
    symbolic = []

    # Line-wise extraction first: prefer explicit equation lines.
    for raw_line in src.splitlines():
        line = _clean_equation_line(raw_line)
        if not _looks_equation_line(line):
            continue
        if re.search(r"\(\d+\)\s*$", raw_line.strip()):
            numbered.append(line)
        else:
            symbolic.append(line)

    # Around Equation(n) anchors, capture nearby formula lines.
    for m in re.finditer(r"Equation\s*\(\d+\)", src, flags=re.I):
        window = src[max(0, m.start() - 220): m.end() + 420]
        for raw_line in window.splitlines():
            line = _clean_equation_line(raw_line)
            if _looks_equation_line(line):
                numbered.append(line)

    # Targeted regexes for MemGen-like notation as a backup.
    regexes = [
        r"M_t\s*=\s*Wweaver\s*\([^\n]{0,100}\)",
        r"m_t\s*=\s*f_M\([^\n]{0,120}\)",
        r"z_\{t,j\}\s*[~?]\s*[^\n]{0,120}",
        r"max[^\n]{0,80}E\([^\n]{0,140}R\([^\n]{0,80}\)\)",
        r"p_j\s*=\s*?\s*\([^\n]{0,120}\)",
        r"e\s*\(\s*c\s*(?:,\s*r\s*)?\)\s*=\s*<API>[^\n]{0,180}</API>",
        r"L_i\s*=\s*L_i\s*\([^\n]{0,120}\)",
    ]
    for rx in regexes:
        for hit in re.finditer(rx, src, flags=re.I):
            line = _clean_equation_line(hit.group(0))
            if _looks_equation_line(line):
                symbolic.append(line)

    # Deduplicate while keeping order and prioritizing numbered equations.
    out = []
    seen = set()
    for bucket in (numbered, symbolic):
        for c in bucket:
            key = c.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(c)
    return out[:5]

def try_fill_equation_fields_from_pdf(data, pdf_excerpt, resolved_pdf_path):
    paper_type = str(data.get("paper_type") or "").strip().lower()
    paper_subtype = str(data.get("paper_subtype") or "").strip().lower()
    # Survey cards should not auto-inject noisy method-level formulas.
    if paper_type == "survey" or paper_subtype == "survey":
        return

    if not value_is_empty(data.get("key_equations")) and str(data.get("key_equations")).strip().lower() != DEFAULT_VALUE:
        return

    candidates = infer_equation_candidates(pdf_excerpt)
    if not candidates and resolved_pdf_path is not None:
        try:
            full_text = extract_text_from_pdf_path(resolved_pdf_path)
        except Exception:
            full_text = ""
        candidates = infer_equation_candidates(full_text)

    if not candidates:
        return

    data["key_equations"] = "\n".join(candidates[:3])
    if value_is_empty(data.get("equation_symbols")):
        data["equation_symbols"] = "needs-check: 符号定义未可靠抽取，需回查原文公式段。"
    if value_is_empty(data.get("equation_role")):
        data["equation_role"] = "needs-check: 公式作用未可靠抽取，需结合方法章节确认。"


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
        "鎽樿",
        "寮曡█",
        "鏂规硶",
        "瀹為獙",
        "缁撴灉",
        "缁撹",
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
        raise RuntimeError(f"--pdf-path 鎸囧悜鐨勬枃浠朵笉瀛樺湪: {path}")
    raw_text = extract_text_from_pdf_path(path)
    excerpt = build_pdf_excerpt(raw_text, pdf_context_chars)
    return path, excerpt


def sanitize_stem(name):
    return re.sub(r"[^\w\-]+", "_", str(name or ""), flags=re.U).strip("_") or "paper"


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
        if "table 1" in page_text:
            score += 20
        score -= abs(page - 2) * 8
        score -= max(0, len(page_text) - 2500) // 250
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
        return None, "未找到 pdftoppm，无法使用页面渲染兜底。"

    prefix = out_dir / "page_render"
    proc = subprocess.run(
        [pdftoppm_bin, "-f", str(page), "-l", str(page), "-png", str(pdf_path), str(prefix)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "pdftoppm 渲染失败"
        return None, msg

    candidates = sorted(out_dir.glob("page_render-*.png"))
    if not candidates:
        return None, "页面渲染完成但未生成 PNG。"
    return candidates[0], ""


def auto_extract_framework_image(pdf_path, item_key, assets_root, max_pages=8):
    out_dir = assets_root / item_key
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfimages_bin = shutil.which("pdfimages")
    if pdfimages_bin:
        list_proc = subprocess.run(
            [pdfimages_bin, "-f", "1", "-l", str(max_pages), "-list", str(pdf_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if list_proc.returncode == 0:
            rows = parse_pdfimages_list(list_proc.stdout)
            if rows:
                rows.sort(key=lambda r: (r["area"] - r["page"] * 1000), reverse=True)
                best = rows[0]
                prefix = out_dir / "img"
                extract_proc = subprocess.run(
                    [pdfimages_bin, "-f", "1", "-l", str(max_pages), "-png", str(pdf_path), str(prefix)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                )
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
                        rel = (Path("assets") / item_key / final_name).as_posix()
                        return rel, f"Auto extracted from PDF page {best['page']} image {best['num']}", False

    # Fallback: vector-only PDFs often have no embedded raster image.
    page = detect_figure_page_from_text(pdf_path, max_pages=max_pages) or (2 if max_pages >= 2 else 1)
    rendered, err = render_page_png_fallback(pdf_path, out_dir, page)
    if rendered:
        final_name = f"framework_page_{page:02d}_render.png"
        final_path = out_dir / final_name
        if final_path.exists():
            final_path.unlink()
        rendered.replace(final_path)
        rel = (Path("assets") / item_key / final_name).as_posix()
        return rel, f"Rendered PDF page {page} as fallback (vector figure likely).", True
    return None, f"图表抽取失败：{err or '未知错误'}", True


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
        "Use title/abstract/annotations/pdf excerpts to produce concise and usable summaries. "
        "If evidence is insufficient, return needs-check."
        if fill_mode == "all"
        else "Use conservative completion. If evidence is insufficient, return needs-check."
    )
    high_risk_fields = [field for field in fields_to_fill if is_high_risk_field(field)]
    low_risk_synthesis_fields = [
        field
        for field in fields_to_fill
        if field in LOW_RISK_SYNTHESIS_FIELDS and field not in high_risk_fields and field not in STRICT_FACT_FIELDS
    ]
    strict_fact_fields = [field for field in fields_to_fill if field in STRICT_FACT_FIELDS]
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
            + "。尽量简洁，避免反复使用固定前缀措辞。"
        )
        if low_risk_synthesis_fields
        else ""
    )
    strict_fact_rule = (
        (
            "以下字段属于严格事实字段："
            + ", ".join(strict_fact_fields)
            + "。禁止编造具体 benchmark、backbone、算法名；若上下文未明确，必须写 needs-check，并给出简短回查提示。"
        )
        if strict_fact_fields
        else ""
    )
    experiment_focus_rule = (
        (
            "以下实验字段仅允许填写上下文中明确出现的实体和数字："
            + ", ".join(experiment_focus_fields)
            + "。若未明确出现，必须写 needs-check。"
        )
        if experiment_focus_fields
        else ""
    )
    paper_subtype_rule = (
        " If paper_subtype is in required_fields, output exactly one lowercase label from: "
        "survey, method, system, benchmark, dataset, empirical, theory, application. "
        "Use empirical for experiment-focused papers."
        if "paper_subtype" in fields_to_fill
        else ""
    )
    system = (
        "You are a research paper note assistant. "
        "Output must be a strict JSON object with no extra text. "
        "The output language should be Chinese; keep technical English terms only when necessary and add concise Chinese context. "
        "For human-facing body fields, avoid long English paragraphs. "
        "When generating review lists, keep items paper-specific and do not copy terms from other papers. "
        "Do not reuse fixed checklists from prior papers (e.g., trigger/weaver/ReAct+CoT) unless explicitly evidenced in this paper context. "
        "For tags: tags and canonical_tags must be AI judgment from this paper evidence only; do not rely on template defaults. "
        "candidate_tags can include AI judgment plus retrieval-friendly related terms if and only if semantically supported by the paper context. "
        "Term style rule: if a term is crucial for method identity or evaluation comparability, you may use first-mention format English(Chinese); otherwise prefer direct Chinese expression. "
        "If high_priority_checks is required, rank items from highest to lowest importance. "
        + mode_rule
        + high_risk_rule
        + low_risk_rule
        + strict_fact_rule
        + experiment_focus_rule
        + paper_subtype_rule
    )
    user = {
        "task": "Fill paper-note fields",
        "required_fields": fields_to_fill,
        "current_values_for_required_fields": {field: data.get(field, DEFAULT_VALUE) for field in fields_to_fill},
        "paper_info": paper_info,
        "pdf_context": {
            "pdf_path": str(pdf_path) if pdf_path else DEFAULT_VALUE,
            "pdf_excerpt": pdf_excerpt if pdf_excerpt else DEFAULT_VALUE,
        },
        "format_rules": {
            "tags": "return JSON array of short kebab-case tags based on this paper only (e.g., llm-agent, prompting); if uncertain return [\"needs-check\"]",
            "canonical_tags": "return JSON array of stable core tags; if uncertain return [\"needs-check\"]",
            "candidate_tags": "return JSON array of broader discoverability tags; may include related terms supported by evidence; if uncertain return [\"needs-check\"]",
            "open_questions": "use Markdown bullet list, each line starts with '- '",
            "high_priority_checks": "use Markdown bullet list sorted from high to low importance; only include unresolved checks relevant to this paper",
            "next_actions": "use numbered list like '1. ...'",
            "main_contributions": "prefer JSON array with 3-5 concise items; avoid one long paragraph",
            "pipeline_flow": "prefer JSON array of ordered steps",
            "module_1_module_2_style": "return plain text, do not return JSON object literals like {\"name\": ...}",
            "core_library_decision": "return one short label: candidate/include/exclude",
            "paper_subtype": "must be one of: survey/method/system/benchmark/dataset/empirical/theory/application",
            "factual_fields_no_guess": "for factual fields, no guessing; if unclear, return needs-check with check hint",
            "inferred_style": "keep inference concise; avoid repeated fixed prefix wording",
            "evidence_quote_rule": "if not verbatim quote, keep as paraphrase and do not claim direct quotation",
            "required_fields_completeness": "must cover every field in required_fields",
            "low_risk_placeholder_rule": "for low-risk summary fields, avoid outputting only needs-check when evidence exists",
            "term_style_rule": "for crucial terms use first-mention English(Chinese); for non-crucial terms prefer Chinese",
        },
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
    ]


def build_polish_messages(field_values):
    system = (
        "You are a scientific note language normalizer. "
        "Convert each field value to concise Chinese while preserving all facts, numbers, names, and uncertainty markers. "
        "Do not add new claims. Return strict JSON only with the same keys. "
        "For crucial terms you may keep first-mention English(Chinese); non-crucial terms prefer Chinese."
    )
    user = {
        "task": "Polish language to Chinese",
        "fields": field_values,
        "rules": {
            "preserve_facts": "must keep all numbers, benchmark names, model names, and uncertainty",
            "keep_terms": "keep necessary English technical terms and add concise Chinese context when helpful",
            "json_style_cleanup": "if a field value is a JSON-like object string, rewrite it as readable Chinese plain text (not JSON literal)",
            "no_new_information": True,
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
        raise RuntimeError("Unknown provider. Please set AI_BASE_URL.")
    if not model:
        raise RuntimeError("Unknown provider. Please set AI_MODEL.")

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

    # Global fallback: auto-extract key figure when PDF is available.
    if resolved_pdf_path and value_is_empty(data.get("framework_image_path")):
        repo_root = Path(__file__).resolve().parent.parent
        assets_root = repo_root / "assets"
        item_key = str(data.get("zotero_item_key") or "").strip()
        if not item_key or item_key.lower() == DEFAULT_VALUE:
            item_key = sanitize_stem(data.get("title") or resolved_pdf_path.stem)
        rel_path, source_or_error, used_fallback = auto_extract_framework_image(
            pdf_path=resolved_pdf_path,
            item_key=item_key,
            assets_root=assets_root,
            max_pages=8,
        )
        if rel_path:
            data["framework_image_path"] = rel_path
            if value_is_empty(data.get("framework_source")):
                data["framework_source"] = source_or_error
            if value_is_empty(data.get("framework_type")):
                data["framework_type"] = "figure / table / framework (needs-check)"
            data["framework_needs_check"] = (
                "已使用页面渲染兜底，建议人工确认是否为关键图表。"
                if used_fallback
                else "否"
            )
        elif value_is_empty(data.get("framework_needs_check")):
            data["framework_needs_check"] = source_or_error
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
            value = sanitize_generated_value(field, value, data.get("paper_type", DEFAULT_VALUE))
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
            value = sanitize_generated_value(field, value, data.get("paper_type", DEFAULT_VALUE))
            data[field] = value

    fields_to_polish = [
        field
        for field in set(fields_to_fill) | CHINESE_POLISH_FIELDS
        if field in data and needs_chinese_polish(field, data.get(field))
    ]
    if fields_to_polish:
        polish_payload = {field: data.get(field, DEFAULT_VALUE) for field in fields_to_polish}
        messages = build_polish_messages(polish_payload)
        content = post_chat(base_url, api_key, model, messages)
        polished = parse_model_json(content)
        for field in fields_to_polish:
            if field in polished and not value_is_empty(polished[field]):
                data[field] = polished[field]

    # Deterministic fallback for obvious equation snippets when model returns needs-check.
    try_fill_equation_fields_from_pdf(data, pdf_excerpt, resolved_pdf_path)

    postprocess_generated_data(data)
    return data, fields_to_fill


def main():
    args = parse_args()
    input_path = Path(args.input_json).expanduser().resolve()
    if not input_path.exists():
        raise RuntimeError(f"Input file does not exist: {input_path}")

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
        print("No fields need filling: target fields already have values.")
        return

    output_path = Path(args.output).expanduser().resolve() if args.output else input_path.with_name(input_path.stem + "_enriched.json")
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated enriched JSON: {output_path}")
    print("Filled fields: " + ", ".join(filled))
    print(f"Next step: python scripts/generate_note.py {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)

