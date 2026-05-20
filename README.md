# Paper Reading Workflow (Zotero + AI + Obsidian)

这是一个面向**非综述论文（method/experiment）**的最小可用工作流：

1. Zotero 管理 PDF、元数据、批注  
2. 脚本生成结构化 JSON（可选 AI 自动补全）  
3. 输出 Markdown 文献笔记到 Obsidian 维护

---

## 当前功能

- `run_workflow.py`：交互式一条龙入口（选择流程 -> 输入参数 -> 自动生成 JSON/抽图/Markdown）
- `pdf_to_json.py`：从 PDF 抽取基础字段（标题、作者、摘要等）
- `zotero_to_json.py`：用 Zotero item key 拉取元数据（可拉批注）
- `ai_enrich_json.py`：用 OpenAI/DeepSeek 兼容 API 回填笔记字段
- `generate_note.py`：将 JSON 渲染成非综述论文模板 Markdown

---

## 目录

```text
templates/
  literature_note_template.md
scripts/
  run_workflow.py
  pdf_to_json.py
  zotero_to_json.py
  ai_enrich_json.py
  generate_note.py
input/
output/
```

## 模板说明

- `templates/literature_note_template.md`：当前默认模板（新版，强调“先看关键内容，细节按需展开”）
- `generate_note.py` 默认读取该模板生成 Markdown

## 模板结构（定稿）

当前模板采用“先判断价值，再按需看细节”的阅读流：

1. `0. 先看这里`：一句话定位 + 问题/方法/结果 + 是否纳入核心库  
2. `1. 核心内容（默认只读这里）`：问题与贡献 / 核心思路或构造方式 / 实验结论 / 我的判断与行动  
3. `2. 关键图表（可选）`：图表来源、类型、说明、回查项  
4. `3. 进阶细节（按需展开）`：核心设计细节、公式细节、实验细节、可引用素材  
5. `4. 证据区（按需展开）`：原文证据摘录 + 我的批注/Zotero 批注  
6. `5. 管理信息（可选）`：标签与文献库信息  
7. `6. 元数据（仅保留一份）`  
8. `7. 待复核问题`

## 新增关键字段（相对早期版本）

- `paper_subtype`：论文子类型（survey/method/system/benchmark/dataset/empirical/theory/application；其中实验类统一用 `empirical`）
- `paper_subtype` 会在 `ai_enrich_json.py` 与 `generate_note.py` 中自动归一化到上述枚举
- `result_reliability`：实验结论可信度判断
- `most_important_figure_or_table`：最关键图/表
- `figure_table_takeaway`：该图/表说明的核心结论
- `worth_deep_reading`：是否值得细读
- `value_for_my_research`：对当前研究的价值
- `what_to_reuse`：可直接借鉴的点
- `what_to_ignore`：可暂时忽略的点

说明：以上字段已接入 `pdf_to_json.py` / `zotero_to_json.py` 的默认 JSON 结构，并可由 `ai_enrich_json.py` 回填。

## 示例：按定稿模板生成 MemGen

```powershell
python scripts/generate_note.py input\2DJECDW9_enriched.json
```

## 生成可靠性规则（已启用）

- `ai_enrich_json.py` 对 `datasets/backbone/baselines/metrics/training_strategy` 等严格事实字段启用“禁止猜测”规则。
- 严格事实字段若出现“可能/推断/likely/maybe”这类措辞，会自动回退为 `needs-check`。
- `ai_enrich_json.py` 会优先把 `main_contributions`、`pipeline_flow` 生成成结构化列表，减少“一段话挤满”的问题。
- 模板中的证据区标题改为“证据摘录 / 原文转述”，避免把转述误标成逐字原文。
- `generate_note.py` 会自动生成“高优先级待复核”清单，优先提示 DOI、benchmark、backbone、训练策略、主结果表等关键核验项。
- `generate_note.py` 会自动做格式规范化（主要贡献编号、流程编号、关键图表缺失兜底、进阶细节折叠块、证据短条目），并将正文中的 `needs-check` 统一渲染为“待核查：...”。
- `generate_note.py` 会自动规整标签风格（如 `llm-agents` -> `llm-agent`）并给出 seed 阶段默认高优先级复核清单，避免漏查关键项。
- `ai_enrich_json.py` 新增中文化润色后处理：当关键字段英文占比过高时，会二次规范为中文表述（保留实体名与数字，不新增事实）。

## 一条龙交互模式（推荐）

只需一条命令：

```powershell
python scripts/run_workflow.py
```

它会按提示让你选择：
- 第一个问题：是否使用 AI（若是，会立即提示配置 AI 环境）
- 从本地 PDF 开始，或从 Zotero item key 开始
- 若选 Zotero，会提示确认/输入 Zotero 环境（`ZOTERO_USER_ID` / `ZOTERO_API_KEY` / `ZOTERO_LIBRARY_TYPE`）
- 是否抽图（framework image）
- 若启用 AI：自动按“全字段覆盖回填”执行
- 是否最终自动生成 Markdown

---

## 用法 A：从 PDF 开始

### A1. 不用 AI（纯脚本）

```powershell
python scripts/pdf_to_json.py "你的论文.pdf" --output input\paper.json
python scripts/generate_note.py input\paper.json
```

### A2. 使用 AI 自动补全

先配置 AI 环境变量（DeepSeek 示例）：

```powershell
$env:AI_PROVIDER="deepseek"
$env:AI_API_KEY="你的API_KEY"
$env:AI_MODEL="deepseek-chat"
# 可选：$env:AI_BASE_URL="https://api.deepseek.com"
```

运行：

```powershell
python scripts/pdf_to_json.py "你的论文.pdf" --ai-summary --ai-fill-mode all --ai-overwrite --ai-all-fields --output input\paper_ai.json
python scripts/generate_note.py input\paper_ai.json
```

---

## 用法 B：从 Zotero item key 开始

先配置 Zotero 环境变量：

```powershell
$env:ZOTERO_USER_ID="你的Zotero用户ID"
$env:ZOTERO_API_KEY="你的Zotero API Key"
$env:ZOTERO_LIBRARY_TYPE="user"   # 或 group
```

### B1. 拉元数据（含批注）

```powershell
python scripts/zotero_to_json.py --item-key 你的条目key --include-annotations --output input\你的条目key.json
```

### B1+（可选）同时自动抽取主图

```powershell
python scripts/zotero_to_json.py --item-key 你的条目key --include-annotations --extract-framework-image --pdf-path "你的本地PDF路径.pdf" --output input\你的条目key.json
```

说明：
- 图片目录会自动使用 `assets/<item_key>/`（例如 `assets/7ERPHPWY/`）
- 抽到的主图路径会写入 `framework_image_path`
- 如果抽图失败，会把原因写到 `framework_needs_check`

### B2. 可选 AI 补全

```powershell
python scripts/ai_enrich_json.py input\你的条目key.json --fill-mode all --overwrite --all-fields --pdf-path "你的本地PDF路径.pdf"
```
说明：
- 建议始终传 `--pdf-path`，脚本会抽取正文片段喂给 AI，避免只靠元数据导致大量 `needs-check`。
- `--all-fields` 会让 AI 回填更多字段；高风险字段（如公式、证据链相关字段）仅在模型“确定正确”时填写，否则保持 `needs-check`。

### B3. 生成 Markdown

```powershell
python scripts/generate_note.py input\你的条目key_enriched.json
```

如果不走 AI，直接用 B1 产出的 JSON 生成：

```powershell
python scripts/generate_note.py input\你的条目key.json
```

---

## 说明

- 模板已切换为**非综述论文主模板**（方法/实验导向）。
- Zotero 批注会按页码排序写入 `zotero_annotations_and_evidence`。
- Windows 直接用 PowerShell 即可，不需要 Bash。
