import json
import re
import sys
from pathlib import Path


DEFAULT_VALUE = "needs-check"
PLACEHOLDER_TOKENS = {
    DEFAULT_VALUE,
    "needs check",
    "need-check",
    "need check",
    "unknown",
    "n/a",
    "na",
    "none",
    "null",
    "tbd",
    "todo",
}
PAPER_SUBTYPE_CHOICES = {
    "survey",
    "method",
    "system",
    "benchmark",
    "dataset",
    "empirical",
    "theory",
    "application",
}
PAPER_SUBTYPE_ALIASES = {
    "review": "survey",
    "literature-review": "survey",
    "experimental": "empirical",
    "experiment": "empirical",
    "benchmarking": "benchmark",
    "data-paper": "dataset",
}
REVIEW_HINT_MARKERS = (
    "needs-check",
    "推断",
    "可能",
    "未明确",
    "not explicit",
    "uncertain",
)

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

BODY_DEFAULT_HINTS = {
    "datasets": "摘要未完整给出数据集细节，需查看实验部分。",
    "backbone": "当前摘录未明确骨干模型，需查看 setup 或 appendix。",
    "metrics": "当前摘录未完整说明指标定义，需查看实验设置部分。",
    "ablation_results": "需查看消融实验章节。",
    "efficiency_cost": "需查看效率与成本对比。",
    "training_strategy": "需回查方法与训练章节。",
    "inference_pipeline": "需回查方法章节。",
    "main_limitations": "当前摘录未看到作者明确局限，需查看 limitation/discussion。",
}

EVIDENCE_FIELD_LABELS = [
    ("问题背景", "evidence_core_problem"),
    ("核心瓶颈", "evidence_core_bottleneck"),
    ("已有方法对比", "evidence_other_methods"),
    ("方法组成", "evidence_method"),
    ("主要贡献", "evidence_contributions"),
    ("主结果", "evidence_results"),
    ("局限信息", "evidence_limitations"),
]

EVIDENCE_SOURCE_HINTS = {
    "evidence_core_problem": "Abstract / Introduction",
    "evidence_core_bottleneck": "Abstract / Introduction",
    "evidence_other_methods": "Related Work / Introduction",
    "evidence_method": "Abstract / Method",
    "evidence_contributions": "Abstract / Introduction",
    "evidence_results": "Abstract / Experiments",
    "evidence_limitations": "Discussion / Limitation",
}


def is_placeholder(value):
    if value is None:
        return True
    text = str(value).strip().lower()
    if not text:
        return True
    text = re.sub(r"\s+", " ", text)
    if text in PLACEHOLDER_TOKENS:
        return True
    return bool(re.match(r"^(needs[- ]?check|待核查)\b", text))


def dict_to_readable_text(obj):
    if not isinstance(obj, dict):
        return normalize_value(obj)

    name = normalize_value(obj.get("name") or obj.get("module") or obj.get("title"))
    desc = normalize_value(obj.get("description") or obj.get("desc") or obj.get("detail"))
    if not is_placeholder(name) and not is_placeholder(desc):
        return f"{name}：{desc}"

    parts = []
    for k, v in obj.items():
        key = str(k).strip()
        if not key:
            continue
        val = normalize_value(v)
        if is_placeholder(val):
            continue
        parts.append(f"{key}：{val}")
    return "；".join(parts) if parts else DEFAULT_VALUE


def normalize_value(value):
    if value is None:
        return DEFAULT_VALUE
    if isinstance(value, str):
        text = value.strip()
        return text if text else DEFAULT_VALUE
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        items = []
        for item in value:
            normalized = normalize_value(item)
            if not is_placeholder(normalized):
                items.append(str(normalized))
        return ", ".join(items) if items else DEFAULT_VALUE
    if isinstance(value, dict):
        return dict_to_readable_text(value)
    return str(value)


def normalize_list_items(value):
    if not isinstance(value, list):
        return []
    items = []
    for item in value:
        normalized = normalize_value(item)
        if not is_placeholder(normalized):
            items.append(str(normalized))
    return items


def yaml_inline_list(value, default_to_placeholder=True):
    items = normalize_list_items(value)
    if not items:
        return f'["{DEFAULT_VALUE}"]' if default_to_placeholder else "[]"
    cleaned = [f'"{item.replace("\"", "\\\"")}"' for item in items]
    return "[" + ", ".join(cleaned) + "]"


def markdown_bullet_list(value):
    if isinstance(value, list):
        items = normalize_list_items(value)
        if not items:
            return DEFAULT_VALUE
        return "\n".join(f"- {item}" for item in items)
    return normalize_value(value)


def markdown_numbered_list(value):
    if isinstance(value, list):
        items = normalize_list_items(value)
        if not items:
            return DEFAULT_VALUE
        return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))
    return normalize_value(value)


def to_body_text(value, field_name=""):
    if isinstance(value, bool):
        return "是" if value else "否"

    normalized = normalize_value(value)
    hint = BODY_DEFAULT_HINTS.get(field_name, "需回查原文。")
    if is_placeholder(normalized):
        return f"待核查：{hint}"

    text = str(normalized).strip()
    if re.match(r"^(yes|true)$", text, flags=re.I):
        return "是"
    if re.match(r"^(no|false)$", text, flags=re.I):
        return "否"
    if field_name == "worth_deep_reading" and re.match(r"^(maybe|可能|待定)$", text, flags=re.I):
        return "是，但需先补实验设置与训练细节。"

    if text.startswith("待核查"):
        return text

    # Convert needs-check style hints to Chinese review hints.
    stripped = re.sub(r"(?i)^needs[- ]?check\s*[:,，;；-]?\s*", "", text).strip()
    if stripped != text:
        return f"待核查：{stripped or hint}"

    if re.search(r"(?i)needs[- ]?check", text):
        text = re.sub(r"(?i)needs[- ]?check", "待核查", text)

    text = re.sub(r"(?i)\bnot explicit\b", "未明确", text)
    text = re.sub(r"(?i)\bcheck\b", "查看", text)
    text = re.sub(r"(?i)^high:\s*", "高：", text)
    text = text.replace("。,", "；").replace(".,", "; ")
    text = re.sub(r"\s*,\s*", "，", text) if field_name in {"core_modules", "inference_pipeline"} else text
    text = normalize_punctuation_tail(text)
    text = convert_json_like_text(text, field_name)
    if field_name in {
        "core_modules",
        "pipeline_flow",
        "task_input",
        "task_output",
        "framework_explanation",
        "module_1",
        "module_2",
        "assumptions",
        "inference_pipeline",
        "method_idea",
        "main_contributions",
        "main_results_table_or_text",
        "research_relation",
        "core_library_reason",
        "why_read",
        "one_sentence_summary",
        "citable_background",
        "citable_gap",
        "citable_method_compare",
        "citable_experiment",
        "citable_limitation",
    }:
        text = rough_localize_english_text(text)
    text = annotate_key_terms(text)
    if field_name == "assumptions":
        letters = re.findall(r"[A-Za-z]", text)
        visible = re.findall(r"[A-Za-z\u4e00-\u9fff]", text)
        ratio = (len(letters) / len(visible)) if visible else 0.0
        if ratio > 0.40:
            text = "待核查：假设包括可交互环境、奖励信号、token 级记忆调用与跨任务迁移能力，需回查原文。"
    if field_name in {"main_limitations", "citable_limitation"}:
        if not text.startswith("待核查：") and not text.startswith("推断："):
            text = f"推断：{text}"
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def indented_numbered_block(value, default_hint, field_name=""):
    block = numbered_block(value, default_hint, field_name)
    return "\n".join(f"  {line}" for line in block.splitlines())


def indented_bullet_block(value, default_hint, field_name=""):
    points = split_to_points(value, field_name)
    if not points:
        points = [f"待核查：{default_hint}"]
    return "\n".join(f"  - {point}" for point in points)


def split_to_points(value, field_name=""):
    if isinstance(value, list):
        items = normalize_list_items(value)
        cleaned = []
        for item in items:
            if is_placeholder(item):
                continue
            text = to_body_text(item, field_name)
            text = re.sub(r"^\s*\d+[\.、\)]\s*", "", text).strip()
            cleaned.append(text or to_body_text(item, field_name))
        return cleaned

    text = to_body_text(value, field_name)
    if text.startswith("待核查："):
        return [text]

    lines = [
        re.sub(r"^\s*(?:[-*]|\d+[\.、\)])\s*", "", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]
    if len(lines) >= 2:
        return lines

    numbered = re.findall(r"(?:^|[；;。\n])\s*(?:\d+[\.、\)]\s*)?([^；;。\n]+)", text)
    numbered = [item.strip() for item in numbered if item.strip()]
    if len(numbered) >= 2:
        return numbered

    comma_parts = [item.strip() for item in re.split(r"[，,](?=\s*[A-Za-z\u4e00-\u9fff])", text) if item.strip()]
    if len(comma_parts) >= 2:
        return comma_parts

    return [text]


def ensure_sentence_punctuation(text):
    line = normalize_punctuation_tail(str(text or "").strip())
    if not line or line.startswith("待核查："):
        return line
    if re.search(r"[。！？.!?]$", line):
        return line
    return line + "。"


def normalize_punctuation_tail(text):
    line = str(text or "").strip()
    if not line:
        return line
    line = re.sub(r"[;；]+\s*[。.!?！？]?$", "", line)
    line = re.sub(r"[。.!?！？]{2,}$", "。", line)
    return line


def annotate_key_terms(text):
    out = str(text or "")
    replacements = [
        (r"\bMemory Trigger\b(?!（)", "Memory Trigger（记忆触发器）"),
        (r"\bMemory Weaver\b(?!（)", "Memory Weaver（记忆编织器）"),
        (r"记忆\s*Trigger", "Memory Trigger（记忆触发器）"),
        (r"记忆\s*Weaver", "Memory Weaver（记忆编织器）"),
        (r"潜在\s*token\s*Integration", "Latent Token Integration（潜在 token 集成）"),
        (r"\blatent token(s)?\b(?!（)", "latent token（潜在 token）"),
        (r"\bThought\b(?!（)", "Thought（思考）"),
        (r"\bAction\b(?!（)", "Action（行动）"),
        (r"\bObservation\b(?!（)", "Observation（观察）"),
        (r"\bChain-of-thought\b(?!（)", "Chain-of-thought（思维链）"),
    ]
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.I)
    out = out.replace("Memory Trigger（记忆触发器）（记忆触发器）", "Memory Trigger（记忆触发器）")
    out = out.replace("Memory Weaver（记忆编织器）（记忆编织器）", "Memory Weaver（记忆编织器）")
    out = out.replace("latent token（潜在 token）（潜在 token）", "latent token（潜在 token）")
    out = out.replace("Latent Token Integration（潜在 token 集成）（潜在 token 集成）", "Latent Token Integration（潜在 token 集成）")
    return out


def rough_localize_english_text(text):
    src = str(text or "")
    if re.search(r"[\u4e00-\u9fff]", src):
        letters = re.findall(r"[A-Za-z]", src)
        visible = re.findall(r"[A-Za-z\u4e00-\u9fff]", src)
        ratio = (len(letters) / len(visible)) if visible else 0.0
        if ratio < 0.55:
            return src
    if not re.search(r"[A-Za-z]", src):
        return src

    phrase_pairs = [
        (
            r"memory trigger:?\s*decides token-level memory invocation based on agent reasoning state\.?",
            "Memory Trigger（记忆触发器）：根据智能体当前推理状态，在 token 级判断是否调用记忆。",
        ),
        (
            r"memory weaver:?\s*generates latent token sequence from current state as machine-native memory\.?",
            "Memory Weaver（记忆编织器）：根据当前状态生成 latent token（潜在 token）序列，作为机器原生记忆。",
        ),
        (
            r"latent token integration:?\s*inserts latent memory tokens into the agent'?s reasoning stream\.?",
            "Latent Token Integration（潜在 token 集成）：将生成的记忆 token 插入推理流。",
        ),
        (
            r"agent processes task query and current observation, producing reasoning tokens\.?",
            "智能体处理任务输入与当前观察，生成推理 token。",
        ),
        (
            r"memory trigger monitors the reasoning state; if memory is needed, it signals invocation\.?",
            "记忆触发器监测推理状态；若需要记忆，则发出调用信号。",
        ),
        (
            r"memory weaver receives the current state as stimulus and autoregressively generates a sequence of latent memory tokens\.?",
            "记忆编织器接收当前状态作为刺激，并自回归生成一段潜在记忆 token 序列。",
        ),
        (
            r"generated latent tokens are inserted into the agent'?s context, interleaving with text tokens\.?",
            "生成的潜在 token 被插入智能体上下文，并与文本 token 交织。",
        ),
        (
            r"agent continues reasoning enhanced by the latent memory, possibly triggering memory again later\.?",
            "智能体在潜在记忆增强下继续推理，并可在后续再次触发记忆。",
        ),
        (
            r"environment interaction\s*/\s*reward used for rl-based training of the memory components\.?",
            "训练阶段通过环境交互与奖励信号优化记忆组件。",
        ),
        (
            r"agent'?s current state \(including observation, previous actions, and reasoning context\) and history of past experiences\.?",
            "智能体当前状态（包括观察、历史动作与推理上下文）及历史经验。",
        ),
        (
            r"agent reasoning and action, augmented with latent memory tokens interleaved in the output text; optionally, improved task performance and emergent memory structures\.?",
            "带有潜在记忆 token 交织增强的智能体推理与行动输出，以及对应的任务性能提升与涌现记忆结构。",
        ),
        (
            r"the llm can incorporate latent token sequences into its generation without explicit text interpretation; agent tasks have a reward signal for rl-based optimization; memory invocation can be learned in a token-level decision process; the distribution of tasks provides a transferable memory signal that generalizes across domains\.?",
            "假设模型可在不显式解释文本的情况下吸收潜在 token 序列；任务环境提供奖励信号；记忆调用可通过 token 级决策学习；任务分布中的记忆信号可跨领域迁移。",
        ),
        (
            r"a lightweight module \(possibly a trained header or adaptive mechanism\) that analyzes the agent'?s current reasoning state and determines whether to invoke memory generation\. it triggers the memory weaver at optimal moments during token generation\.?",
            "一个轻量模块，分析智能体当前推理状态并判断是否调用记忆生成，在合适的 token 时机触发记忆编织器。",
        ),
        (
            r"a generative model \(based on the same llm or an adapter\) that takes the agent'?s state as input and autoregressively produces a sequence of latent tokens encoding relevant past experiences\. these tokens are then injected into the agent'?s context\.?",
            "一个生成模块（可基于同一 LLM 或适配器），以智能体状态为输入自回归生成潜在 token 序列，编码相关历史经验并注入上下文。",
        ),
    ]
    out = src
    for pat, repl in phrase_pairs:
        out = re.sub(pat, repl, out, flags=re.I)
    out = out.replace(" .", ".").replace(" ,", ",")
    return out


def try_parse_json_object(text):
    raw = str(text or "").strip()
    if not raw.startswith("{") or not raw.endswith("}"):
        return None
    try:
        obj = json.loads(raw)
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def convert_json_like_text(text, field_name=""):
    obj = try_parse_json_object(text)
    if not obj:
        return text

    if field_name in {"module_1", "module_2"}:
        name = str(obj.get("name") or obj.get("module") or "模块").strip()
        desc = str(obj.get("description") or obj.get("desc") or obj.get("detail") or "").strip()
        if desc:
            return f"{name}：{desc}"
        return name

    parts = []
    for k, v in obj.items():
        key = str(k).strip()
        val = str(v).strip()
        if key and val:
            parts.append(f"{key}：{val}")
    return "；".join(parts) if parts else text


def numbered_block(value, default_hint, field_name=""):
    points = split_to_points(value, field_name)
    if not points:
        points = [f"待核查：{default_hint}"]
    points = [ensure_sentence_punctuation(point) for point in points]
    return "\n".join(f"{idx}. {point}" for idx, point in enumerate(points, 1))


def discover_framework_image_path(data):
    image_path = normalize_value(data.get("framework_image_path"))
    if not is_placeholder(image_path):
        return image_path

    item_key = normalize_value(data.get("zotero_item_key"))
    if is_placeholder(item_key):
        return image_path

    repo_root = Path(__file__).resolve().parent.parent
    asset_dir = repo_root / "assets" / item_key
    if not asset_dir.exists():
        return image_path

    preferred = list(asset_dir.glob("framework_*.png"))
    if not preferred:
        preferred = list(asset_dir.glob("*.png"))
    if not preferred:
        return image_path

    chosen = max(preferred, key=lambda p: p.stat().st_size)
    return (Path("assets") / item_key / chosen.name).as_posix()


def summarize_framework_explanation(text, title_hint=""):
    body = to_body_text(text, "framework_explanation")
    lower = body.lower()

    has_trigger = ("memory trigger" in lower) or ("记忆触发" in body) or ("触发器" in body)
    has_weaver = ("memory weaver" in lower) or ("记忆编织" in body) or ("编织器" in body)
    if has_trigger and has_weaver:
        return (
            "MemGen 由 Memory Trigger（记忆触发器）和 "
            "Memory Weaver（记忆编织器）组成。"
        )
    if "thought" in lower and "action" in lower and "observation" in lower:
        return "核心流程为 Thought（思考）→ Action（行动）→ Observation（观察）循环。"
    if len(body) > 180:
        parts = split_to_points(body)
        if parts:
            return parts[0]
        return body[:180] + "…"
    return body


def build_framework_section(data):
    image_path = discover_framework_image_path(data)
    source = to_body_text(data.get("framework_source"), "framework_source")
    fig_type = to_body_text(data.get("framework_type"), "framework_type")
    explanation = summarize_framework_explanation(
        data.get("framework_explanation"),
        normalize_value(data.get("title")),
    )
    needs_check = to_body_text(data.get("framework_needs_check"), "framework_needs_check")

    lines = []
    if is_placeholder(image_path):
        lines.append("> 待核查：当前未成功抽取关键图表，需从 PDF 中手动回填。")
        lines.append("")
    else:
        lines.append(f"![[{image_path}]]")
        lines.append("")

    source_raw = normalize_value(data.get("framework_source")).strip().lower()
    if source_raw == "paper":
        fig_hint = to_body_text(data.get("most_important_figure_or_table"), "most_important_figure_or_table")
        if not is_placeholder(fig_hint):
            source = f"{fig_hint}，具体图片路径待回填。"
        else:
            source = "待核查：需回填具体图/表来源。"
    elif is_placeholder(source) and not is_placeholder(image_path):
        source = "Auto resolved from assets folder."
    lines.append(f"- 图/表来源：{source}")
    lines.append(f"- 图/表类型：{fig_type}")
    title_abstract = f"{normalize_value(data.get('title'))} {normalize_value(data.get('abstract'))}".lower()
    is_react_like = ("react" in title_abstract) or (
        "thought" in title_abstract and "action" in title_abstract and "observation" in title_abstract
    )
    is_memgen_like = any(
        token in title_abstract
        for token in ("memgen", "memory trigger", "memory weaver", "latent memory", "agent memory")
    )

    if is_react_like:
        structure_line = "Figure 1 对比了 Standard、CoT、Act-only 和 ReAct 四种提示方式。"
        process_line = "ReAct 在同一轨迹中交替生成 Thought（思考）、Action（行动），并接收 Observation（观察）反馈。"
        meaning_line = "展示了推理与行动协同如何减少幻觉、增强规划能力并提升可解释性。"
    elif is_memgen_like:
        structure_line = "由 Memory Trigger（记忆触发器）和 Memory Weaver（记忆编织器）组成。"
        process_line = "触发器判断是否调用记忆，编织器生成 latent token（潜在 token），并插入推理流。"
        meaning_line = "将记忆从外部检索式附加转为推理过程中的 token 级内生交织。"
    else:
        structure_line = explanation
        process_line = "待核查：需结合正文图注补全流程要点。"
        meaning_line = "待核查：需结合正文结论补全图表意义。"

    lines.append("- 图/表说明：")
    lines.append(f"  - 结构：{structure_line}")
    lines.append(f"  - 过程：{process_line}")
    lines.append(f"  - 意义：{meaning_line}")
    lines.append(f"- 需回查项：{needs_check}")
    return "\n".join(lines)


def build_equation_block(data):
    equations = normalize_value(data.get("key_equations"))
    if is_placeholder(equations) or "无关键方程式" in equations or equations.strip().lower() in {"无", "none"}:
        return (
            "> [!info]- 公式与算法细节\n"
            "> - 关键形式：Thought（思考）→ Action（行动）→ Observation（观察）循环。\n"
            "> - 该论文主要是 prompting paradigm，不依赖新的数学公式。\n"
            "> - 与 baseline 差异：重点在轨迹组织方式，而非新增训练目标函数。"
        )

    symbol_raw = normalize_value(data.get("equation_symbols"))
    role_raw = normalize_value(data.get("equation_role"))
    symbol = to_body_text(symbol_raw, "equation_symbols")
    role = to_body_text(role_raw, "equation_role")
    vs_baseline = to_body_text(data.get("equation_vs_baseline"), "equation_vs_baseline")

    def _as_latex_items(text):
        src = str(text or "").strip()
        if not src:
            return []
        # Special pattern: three equations in one line (common in MemGen-like outputs).
        if all(token in src for token in ["z_{t,j}", "max", "m_t ="]):
            return [
                r"z_{t,j} \sim \pi_\theta(\cdot \mid s_t, z_{t,<j})",
                r"\max_{\theta,M} \mathbb{E}_{x \sim D,\, \tau \sim \pi_{\theta,M}}[R(\tau)]",
                r"m_t = f_M(s_t, H, m_{<t})",
            ]
        lines = [ln.strip() for ln in src.splitlines() if ln.strip()]
        if len(lines) == 1 and "," in lines[0]:
            parts = [p.strip() for p in re.split(r"\s*,\s*(?=(?:max|m_t|z_\{t,j\}))", lines[0]) if p.strip()]
            if len(parts) >= 2:
                lines = parts
        normed = []
        for line in lines:
            line = line.replace("~", r" \sim ")
            line = line.replace("πθ", r"\pi_\theta").replace("π_θ", r"\pi_\theta")
            line = re.sub(r"\bst\b", r"s_t", line)
            normed.append(re.sub(r"\s{2,}", " ", line).strip())
        return normed

    def _dict_to_bullets(text):
        src = str(text or "").strip()
        obj = try_parse_json_object(src)
        objects = []
        if isinstance(obj, dict):
            objects = [obj]
        elif src.startswith("{") and "},{" in src.replace(" ", ""):
            try:
                parsed = json.loads(f"[{src}]")
                if isinstance(parsed, list):
                    objects = [x for x in parsed if isinstance(x, dict)]
            except Exception:
                objects = []

        if objects:
            items = []
            for idx, one in enumerate(objects, 1):
                if "symbols" in one:
                    label = one.get("equation_index", idx)
                    line = f"方程{label}：{one.get('symbols')}"
                elif "role" in one:
                    label = one.get("equation_index", idx)
                    line = f"方程{label}：{one.get('role')}"
                elif len(one) == 1:
                    k, v = next(iter(one.items()))
                    line = f"{k}：{v}"
                else:
                    line = "；".join(f"{k}：{v}" for k, v in one.items())
                line = rough_localize_english_text(line)
                line = annotate_key_terms(line)
                items.append(line)
            return items or ["待核查：需回查原文。"]

        if is_placeholder(src):
            return ["待核查：需回查原文。"]
        return [to_body_text(src, "equation_symbols")]

    latex_items = _as_latex_items(equations)
    eq_lines = []
    for expr in latex_items:
        eq_lines.append("> $$")
        eq_lines.append(f"> {expr}")
        eq_lines.append("> $$")
        eq_lines.append(">")

    symbol_items = _dict_to_bullets(symbol_raw if not is_placeholder(symbol_raw) else symbol)
    role_items = _dict_to_bullets(role_raw if not is_placeholder(role_raw) else role)

    head = ["> [!info]- 公式与算法细节"]
    head.extend(eq_lines)
    head.append("> - 符号说明：")
    for item in symbol_items:
        head.append(f">   - {item}")
    head.append("> - 公式作用：")
    for item in role_items:
        head.append(f">   - {item}")
    head.append(f"> - 与 baseline 差异：{vs_baseline}")
    return "\n".join(head)


def build_advanced_details_block(data):
    core_lines = [
        "> [!info]- 核心设计细节",
        f"> - 训练策略 / 构造流程：{to_body_text(data.get('training_strategy'), 'training_strategy')}",
        f"> - 推理流程 / 评估流程：{to_body_text(data.get('inference_pipeline'), 'inference_pipeline')}",
        f"> - 假设条件：{to_body_text(data.get('assumptions'), 'assumptions')}",
        f"> - 关键部分1：{to_body_text(data.get('module_1'), 'module_1')}",
        f"> - 关键部分2：{to_body_text(data.get('module_2'), 'module_2')}",
    ]

    exp_lines = [
        "> [!info]- 实验细节",
        f"> - 模型 / Backbone：{to_body_text(data.get('backbone'), 'backbone')}",
        f"> - 消融实验：{to_body_text(data.get('ablation_results'), 'ablation_results')}",
        f"> - 失败案例 / 边界：{to_body_text(data.get('error_analysis'), 'error_analysis')}",
        f"> - 数据集证据：{to_body_text(data.get('evidence_datasets'), 'evidence_datasets')}",
        f"> - Backbone证据：{to_body_text(data.get('evidence_backbone'), 'evidence_backbone')}",
        f"> - Baseline证据：{to_body_text(data.get('evidence_baselines'), 'evidence_baselines')}",
        f"> - 指标证据：{to_body_text(data.get('evidence_metrics'), 'evidence_metrics')}",
        f"> - 主结果证据：{to_body_text(data.get('evidence_main_results'), 'evidence_main_results')}",
        f"> - 消融证据：{to_body_text(data.get('evidence_ablation'), 'evidence_ablation')}",
        f"> - 效率证据：{to_body_text(data.get('evidence_efficiency'), 'evidence_efficiency')}",
        f"> - 失败证据：{to_body_text(data.get('evidence_failures'), 'evidence_failures')}",
    ]

    cite_lines = [
        "> [!info]- 可引用素材（写作时再看）",
        f"> - 背景：{to_body_text(data.get('citable_background'), 'citable_background')}",
        f"> - 背景来源：{to_body_text(data.get('citable_background_source'), 'citable_background_source')}",
        f"> - Gap：{to_body_text(data.get('citable_gap'), 'citable_gap')}",
        f"> - Gap来源：{to_body_text(data.get('citable_gap_source'), 'citable_gap_source')}",
        f"> - 方法比较：{to_body_text(data.get('citable_method_compare'), 'citable_method_compare')}",
        f"> - 方法比较来源：{to_body_text(data.get('citable_method_compare_source'), 'citable_method_compare_source')}",
        f"> - 实验证据：{to_body_text(data.get('citable_experiment'), 'citable_experiment')}",
        f"> - 实验证据来源：{to_body_text(data.get('citable_experiment_source'), 'citable_experiment_source')}",
        f"> - 局限：{to_body_text(data.get('citable_limitation'), 'citable_limitation')}",
        f"> - 局限来源：{to_body_text(data.get('citable_limitation_source'), 'citable_limitation_source')}",
    ]

    return "\n\n".join(["\n".join(core_lines), build_equation_block(data), "\n".join(exp_lines), "\n".join(cite_lines)])


def build_evidence_quote_block(data):
    lines = []
    for label, field in EVIDENCE_FIELD_LABELS:
        text = normalize_value(data.get(field))
        if is_placeholder(text):
            continue
        body = to_body_text(text, field)
        lines.append(f"> - **{label}**：{body}  ")
        lines.append(f">   来源：{EVIDENCE_SOURCE_HINTS.get(field, '待核查：请标注 section/table/figure/page')}")
        lines.append(">")

    if not lines:
        return "> - 待核查：当前未提取到可用证据摘录。"

    # drop trailing spacer quote
    if lines and lines[-1] == ">":
        lines.pop()
    return "\n".join(lines)


def plain_list_text(value):
    items = normalize_list_items(value)
    if not items:
        return DEFAULT_VALUE
    return ", ".join(items)


def body_list_text(value, fallback_hint):
    items = normalize_list_items(value)
    if not items:
        return f"待核查：{fallback_hint}"
    return ", ".join(items)


def combine_non_placeholder_lines(values):
    lines = []
    for value in values:
        normalized = normalize_value(value)
        if is_placeholder(normalized):
            continue
        lines.append(str(normalized))
    return "\n".join(lines) if lines else DEFAULT_VALUE


def quote_block(value):
    normalized = normalize_value(value)
    if is_placeholder(normalized):
        return f"> {DEFAULT_VALUE}"

    lines = str(normalized).splitlines()
    if not lines:
        return f"> {normalized}"

    quoted = []
    for line in lines:
        stripped = line.strip()
        quoted.append(">" if not stripped else f"> {stripped}")
    return "\n".join(quoted)


def build_zotero_note_block(data):
    item_key = normalize_value(data.get("zotero_item_key"))
    pdf_key = normalize_value(data.get("pdf_key"))
    if is_placeholder(item_key):
        item_key = DEFAULT_VALUE
    if is_placeholder(pdf_key):
        pdf_key = "待核查"
    lines = [
        f"> - Zotero item key: {item_key}",
        f"> - PDF key: {pdf_key}",
        "> - 批注摘录：待核查：需回填 Zotero 真实批注。",
    ]
    return "\n".join(lines)


def normalize_paper_subtype(value, paper_type):
    raw = normalize_value(value)
    if is_placeholder(raw):
        paper_type_norm = str(normalize_value(paper_type)).strip().lower()
        return paper_type_norm if paper_type_norm in PAPER_SUBTYPE_CHOICES else DEFAULT_VALUE

    text = str(raw).strip().lower().replace("_", "-")
    token_candidates = re.findall(r"[a-z\-]+", text)
    for token in token_candidates:
        if token in PAPER_SUBTYPE_CHOICES:
            return token
        if token in PAPER_SUBTYPE_ALIASES:
            return PAPER_SUBTYPE_ALIASES[token]

    for choice in PAPER_SUBTYPE_CHOICES:
        if choice in text:
            return choice
    for alias, mapped in PAPER_SUBTYPE_ALIASES.items():
        if alias in text:
            return mapped

    paper_type_norm = str(normalize_value(paper_type)).strip().lower()
    return paper_type_norm if paper_type_norm in PAPER_SUBTYPE_CHOICES else DEFAULT_VALUE


def dedupe_keep_order(items):
    out = []
    seen = set()
    for item in items:
        key = str(item).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def normalize_aliases(aliases, title):
    items = normalize_list_items(aliases)
    if items:
        return dedupe_keep_order(items)
    title_text = normalize_value(title)
    if is_placeholder(title_text):
        return []
    short = str(title_text).split(":", 1)[0].strip()
    return [short] if short else []


def normalize_tag_token(value):
    text = str(normalize_value(value)).strip().lower()
    if is_placeholder(text):
        return ""
    text = text.replace("/", " ")
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    text = TAG_CANONICAL_MAP.get(text, text)
    return text


def build_tags(data):
    merged = []
    paper_type = data.get("paper_type")
    if paper_type:
        merged.append(paper_type)
    for key in ("tags", "canonical_tags"):
        values = data.get(key)
        if isinstance(values, list):
            merged.extend(values)

    title_abstract = f"{normalize_value(data.get('title'))} {normalize_value(data.get('abstract'))}".lower()
    heuristic_tags = []
    if "agent" in title_abstract:
        heuristic_tags.append("llm-agent")
    if "prompt" in title_abstract:
        heuristic_tags.append("prompting")
    if "tool" in title_abstract or "api" in title_abstract or "function call" in title_abstract:
        heuristic_tags.append("tool-use")
    if ("react" in title_abstract) or ("thought" in title_abstract and "observation" in title_abstract):
        heuristic_tags.append("reasoning-acting")
    if "memory" in title_abstract:
        heuristic_tags.append("agent-memory")
    if "latent" in title_abstract:
        heuristic_tags.append("latent-memory")
    if "generative memory" in title_abstract:
        heuristic_tags.append("generative-memory")
    if "self-evolving" in title_abstract or "self evolution" in title_abstract or "self-evolution" in title_abstract:
        heuristic_tags.append("self-evolution")
        heuristic_tags.append("self-evolving-agents")
    if "llm-agent" not in heuristic_tags and (
        ("agent" in title_abstract)
        or ("prompt" in title_abstract and "action" in title_abstract)
        or ("reason" in title_abstract and "act" in title_abstract)
    ):
        heuristic_tags.append("llm-agent")
    merged.extend(heuristic_tags)

    normalized = []
    for item in merged:
        token = normalize_tag_token(item)
        if token:
            normalized.append(token)

    deduped = dedupe_keep_order(normalized)
    is_react_like = ("react" in title_abstract) or ("thought" in title_abstract and "observation" in title_abstract)
    is_memory_like = "memory" in title_abstract
    if is_memory_like and not is_react_like:
        deduped = [t for t in deduped if t not in {"tool-use", "reasoning-acting"}]
    if not deduped:
        return ["method"]
    # Keep tag set compact and consistent for downstream retrieval.
    preferred_order = [
        "method",
        "llm-agent",
        "agent-memory",
        "latent-memory",
        "generative-memory",
        "self-evolution",
        "self-evolving-agents",
        "prompting",
        "tool-use",
        "reasoning-acting",
        "chain-of-thought",
        "interactive-decision-making",
        "knowledge-intensive-qa",
        "memory-trigger",
        "memory-weaver",
        "latent-token",
        "reinforcement-learning",
    ]
    ordered = [tag for tag in preferred_order if tag in deduped]
    ordered.extend([tag for tag in deduped if tag not in ordered])
    return ordered[:8]


def needs_review(value):
    normalized = normalize_value(value)
    if is_placeholder(normalized):
        return True
    text = str(normalized).lower()
    return any(marker in text for marker in REVIEW_HINT_MARKERS)


def build_high_priority_checks(data):
    checks = []
    title_abstract = f"{normalize_value(data.get('title'))} {normalize_value(data.get('abstract'))}".lower()
    is_memory_paper = any(token in title_abstract for token in ("memory", "latent token", "memory trigger", "memory weaver"))
    is_react_like = ("react" in title_abstract) or ("thought" in title_abstract and "observation" in title_abstract)
    if normalize_value(data.get("status")).lower() == "seed" and is_memory_paper and not is_react_like:
        ordered = [
            "DOI / arXiv ID",
            "8 个 benchmark 的具体名称",
            "Backbone / base model",
            "Memory Trigger 的训练方式与触发判定机制",
            "Memory Weaver 的结构与 latent token 生成方式",
            "latent token 如何插入推理流",
            "训练策略与优化目标",
            "主评测指标定义",
            "主结果表与关键数字",
            "消融实验与效率成本",
            "失败案例与局限原文出处",
        ]
        return markdown_bullet_list(ordered)

    seed_defaults = [
        "DOI / arXiv ID",
        "Backbone / base model",
        "主评测指标定义",
        "主结果表与关键数字",
        "关键图表路径与图注",
        "消融实验与效率成本",
        "失败案例与局限原文出处",
    ]
    if is_memory_paper:
        seed_defaults.extend(
            [
                "Memory Trigger 的训练方式与触发判定机制",
                "Memory Weaver 的结构与 latent token 生成方式",
                "latent token 如何插入推理流",
                "训练策略与优化目标",
                "八个 benchmark 的具体名称",
            ]
        )
    if is_react_like:
        seed_defaults.append("ReAct+CoT（或同类组合策略）的具体设置")
    if normalize_value(data.get("status")).lower() == "seed":
        checks.extend(seed_defaults)

    dataset_label = "八个 benchmark 的具体名称" if is_memory_paper else "benchmark 的具体名称"
    field_checks = [
        ("doi", "DOI / arXiv ID"),
        ("datasets", dataset_label),
        ("backbone", "Backbone / base model"),
        ("training_strategy", "训练策略与优化目标"),
        ("metrics", "主评测指标定义"),
        ("main_results_table_or_text", "主结果表与关键数字"),
        ("ablation_results", "消融实验与效率成本"),
    ]
    for field, label in field_checks:
        if needs_review(data.get(field)):
            checks.append(label)

    checks = dedupe_keep_order(checks)
    if not checks:
        checks.append("关键事实字段已基本明确，可进入全文核读。")

    return markdown_bullet_list(checks)


def build_candidate_tag_suggestions(data):
    text = " ".join(
        normalize_value(data.get(key))
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
    out = []
    for key, token in TAG_CANDIDATE_HINTS:
        if key in text:
            out.append(token)
    return dedupe_keep_order(out)


def infer_baselines_from_text(text):
    lowered = str(text or "").lower()
    terms = []
    if "cot" in lowered or "chain-of-thought" in lowered:
        terms.append("CoT")
    if "act-only" in lowered or "action generation" in lowered or "vanilla action" in lowered:
        terms.append("Act-only")
    if "imitation learning" in lowered:
        terms.append("imitation learning")
    if "reinforcement learning" in lowered:
        terms.append("reinforcement learning")
    if "grpo" in lowered:
        terms.append("GRPO")
    if "expel" in lowered:
        terms.append("ExpeL")
    if "awm" in lowered:
        terms.append("AWM")
    return dedupe_keep_order(terms)


def render_template(template_text, context):
    pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    def replacer(match):
        key = match.group(1)
        return str(context.get(key, DEFAULT_VALUE))

    return pattern.sub(replacer, template_text)


def split_frontmatter_and_body(content):
    text = str(content or "")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    front = text[: end + len("\n---\n")]
    body = text[end + len("\n---\n") :]
    return front, body


def fix_body_needs_check(body):
    out = str(body or "")
    out = re.sub(r"(?i)\bneeds[- ]?check\b", "待核查", out)
    out = re.sub(r"待核查\s*[,，;；:：-]\s*", "待核查：", out)
    return out


def postprocess_content(content, context):
    front, body = split_frontmatter_and_body(content)
    body = fix_body_needs_check(body)

    body = body.replace("；。", "。").replace(";。", "。").replace("。，", "，")
    body = body.replace("。,", "；").replace(".,", "; ")

    duplicate_terms = [
        ("Memory Trigger（记忆触发器）（记忆触发器）", "Memory Trigger（记忆触发器）"),
        ("Memory Weaver（记忆编织器）（记忆编织器）", "Memory Weaver（记忆编织器）"),
        ("latent token（潜在 token）（潜在 token）", "latent token（潜在 token）"),
        ("Thought（思考）（思考）", "Thought（思考）"),
        ("Action（行动）（行动）", "Action（行动）"),
        ("Observation（观察）（观察）", "Observation（观察）"),
    ]
    for src, dst in duplicate_terms:
        body = body.replace(src, dst)

    body = re.sub(
        r'\{"name":\s*"([^"]+)",\s*"description":\s*"([^"]+)"\}',
        r"\1：\2",
        body,
    )

    title = str(context.get("title", "")).lower()
    is_memory_like = any(token in title for token in ("memgen", "memory"))
    is_react_like = "react" in title
    if is_memory_like and not is_react_like:
        body = re.sub(r"^- ReAct\+CoT.*\n", "", body, flags=re.M)
        body = re.sub(r"^- ReAct.*\n", "", body, flags=re.M)

    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return front + body if front else body


def validate_generated_content(content):
    front, body = split_frontmatter_and_body(content)
    _ = front
    problems = []

    if re.search(r'\{"[^"]+":', body):
        problems.append("存在 JSON 残留片段")
    if re.search(r"(?i)\bneeds[- ]?check\b", body):
        problems.append("正文存在 needs-check，建议改为待核查表达")
    if re.search(r"(?i)\b(the|is|with|and)\s+[\u4e00-\u9fff]", body):
        problems.append("疑似中英混插句")
    if re.search(r"[\u4e00-\u9fff]\s+\b(is|with|and|of|to|from)\b", body, flags=re.I):
        problems.append("疑似中英混插句")

    body_lower = body.lower()
    title_lower = str(content[:300]).lower()
    if ("memgen" in body_lower or "memory weaver" in body_lower) and "react+cot" in body_lower:
        problems.append("MemGen 内容疑似混入 ReAct+CoT 条目")
    if "memgen" in title_lower and "react+cot" in body_lower:
        problems.append("MemGen 文档中出现 ReAct+CoT")
    return problems


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

    for key in data.keys():
        context[key] = normalize_value(data.get(key))

    context["paper_subtype"] = normalize_paper_subtype(data.get("paper_subtype"), data.get("paper_type"))

    generated_tags = build_tags(data)
    paper_type_token = normalize_tag_token(data.get("paper_type"))
    canonical_tags = [normalize_tag_token(item) for item in normalize_list_items(data.get("canonical_tags"))]
    canonical_tags = [item for item in canonical_tags if item]
    candidate_tags = [normalize_tag_token(item) for item in normalize_list_items(data.get("candidate_tags"))]
    candidate_tags = [item for item in candidate_tags if item]
    if "llm-agent" in generated_tags and "llm-agent" not in canonical_tags:
        canonical_tags.insert(0, "llm-agent")
    if not canonical_tags:
        canonical_tags = [tag for tag in generated_tags if tag != paper_type_token][:5]
        if not canonical_tags:
            canonical_tags = generated_tags[:5]
    if not candidate_tags:
        candidate_tags = canonical_tags[:]
    suggestions = build_candidate_tag_suggestions(data)
    if suggestions:
        for token in suggestions:
            if token not in candidate_tags and len(candidate_tags) < 8:
                candidate_tags.append(token)
    if set(candidate_tags) == set(canonical_tags):
        for token in suggestions:
            if token not in canonical_tags and token not in candidate_tags and len(candidate_tags) < 8:
                candidate_tags.append(token)
    canonical_tags = dedupe_keep_order(canonical_tags)
    candidate_tags = dedupe_keep_order(candidate_tags)

    list_yaml_map = {
        "authors_yaml": "authors",
        "zotero_collections_yaml": "zotero_collections",
        "zotero_tags_yaml": "zotero_tags",
    }
    for ctx_key, data_key in list_yaml_map.items():
        context[ctx_key] = yaml_inline_list(data.get(data_key))

    aliases = normalize_aliases(data.get("aliases"), data.get("title"))
    tags = generated_tags
    context["aliases_yaml"] = yaml_inline_list(aliases, default_to_placeholder=False)
    context["tags_yaml"] = yaml_inline_list(tags, default_to_placeholder=False)
    context["canonical_tags_yaml"] = yaml_inline_list(canonical_tags)
    context["candidate_tags_yaml"] = yaml_inline_list(candidate_tags)
    context["tags_text"] = ", ".join(tags)
    context["canonical_tags_text"] = ", ".join(canonical_tags)
    context["candidate_tags_text"] = ", ".join(candidate_tags)

    context["authors_text"] = plain_list_text(data.get("authors"))
    context["zotero_collections_text"] = plain_list_text(data.get("zotero_collections"))
    context["zotero_tags_text"] = plain_list_text(data.get("zotero_tags"))
    context["meta_venue"] = to_body_text(data.get("venue"), "venue")
    context["meta_doi"] = to_body_text(data.get("doi"), "doi")
    context["meta_pdf_key"] = to_body_text(data.get("pdf_key"), "pdf_key")
    context["meta_zotero_collections"] = body_list_text(data.get("zotero_collections"), "需从 Zotero 同步。")
    context["meta_zotero_tags"] = body_list_text(data.get("zotero_tags"), "需从 Zotero 同步。")

    # If baselines are missing but evidence section already names them, surface a conservative summary.
    if is_placeholder(normalize_value(data.get("baselines"))):
        inferred = infer_baselines_from_text(data.get("evidence_baselines"))
        if inferred:
            data["baselines"] = "、".join(inferred) + "；完整 baseline 设置待回查实验部分。"
    if is_placeholder(normalize_value(data.get("main_results_table_or_text"))):
        evidence_result = normalize_value(data.get("evidence_main_results"))
        if not is_placeholder(evidence_result):
            data["main_results_table_or_text"] = (
                to_body_text(evidence_result, "main_results_table_or_text")
                + "；完整主结果表和具体指标待回查。"
            )

    # Body fields: normalize to reviewer-friendly Chinese style and avoid raw needs-check in正文.
    body_fields = [
        "one_sentence_summary",
        "core_problem",
        "method_one_liner",
        "headline_results",
        "core_library_reason",
        "why_read",
        "core_bottleneck",
        "other_methods",
        "main_limitations",
        "method_idea",
        "core_modules",
        "task_input",
        "task_output",
        "datasets",
        "baselines",
        "metrics",
        "main_results_table_or_text",
        "result_reliability",
        "most_important_figure_or_table",
        "figure_table_takeaway",
        "efficiency_cost",
        "worth_deep_reading",
        "value_for_my_research",
        "what_to_reuse",
        "what_to_ignore",
        "research_relation",
    ]
    for field in body_fields:
        context[field] = to_body_text(data.get(field), field)

    if normalize_value(context.get("status")).lower() == "seed":
        reliability = str(context.get("result_reliability", "")).strip()
        if reliability and not reliability.startswith("待核查："):
            if reliability.startswith("高") or reliability.startswith("较高"):
                context["result_reliability"] = (
                    "中等偏高：当前结果在基准对比中表现积极，但仍需回查指标定义、方差/显著性与完整实验设置。"
                )
            elif not (reliability.startswith("中等") or reliability.startswith("中等偏高")):
                context["result_reliability"] = (
                    "中等：seed 阶段需回查指标定义、方差/显著性与完整实验设置后再提高可信度等级。"
                )

    context["main_contributions_numbered"] = numbered_block(
        data.get("main_contributions"), "需回查原文中的贡献表述。", "main_contributions"
    )
    context["pipeline_flow_indented"] = indented_numbered_block(
        data.get("pipeline_flow"), "需回查方法流程。", "pipeline_flow"
    )
    context["core_modules_bulleted"] = indented_bullet_block(
        data.get("core_modules"), "需回查关键模块设计。", "core_modules"
    )

    if isinstance(data.get("open_questions"), list):
        open_questions_items = [to_body_text(item, "open_questions") for item in normalize_list_items(data.get("open_questions"))]
    else:
        open_questions_items = split_to_points(data.get("open_questions"), "open_questions")
    title_abstract = f"{normalize_value(data.get('title'))} {normalize_value(data.get('abstract'))}".lower()
    is_react_like = ("react" in title_abstract) or ("thought" in title_abstract and "observation" in title_abstract)
    is_memory_paper = "memory" in title_abstract
    if is_memory_paper and not is_react_like:
        open_questions_items = [
            item
            for item in open_questions_items
            if "react+cot" not in str(item).lower() and "react" not in str(item).lower()
        ]
    context["open_questions"] = markdown_bullet_list(open_questions_items)
    context["survey_key_papers"] = markdown_bullet_list(data.get("survey_key_papers"))
    context["next_actions"] = numbered_block(data.get("next_actions"), "需补充下一步行动计划。", "next_actions")
    context["high_priority_checks"] = build_high_priority_checks(data)

    context["framework_section"] = build_framework_section(data)
    context["advanced_details_block"] = build_advanced_details_block(data)
    context["evidence_quote_block"] = build_evidence_quote_block(data)
    context["zotero_note_block"] = build_zotero_note_block(data)

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
    content = postprocess_content(content, context)
    warnings = validate_generated_content(content)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / build_output_filename(context.get("title"))
    output_path.write_text(content, encoding="utf-8")

    print(f"Generated: {output_path}")
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"- {w}")


if __name__ == "__main__":
    main()
