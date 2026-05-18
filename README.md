# Zotero + AI + Obsidian 科研论文阅读管理工作流（MVP）

这是一个最小可用（MVP）的论文阅读管理原型，目标是把流程跑通：

1. Zotero 管理论文 PDF、元数据与批注（可云同步）  
2. 脚本抽取信息（可选 AI 自动总结）  
3. 生成结构化 Markdown 文献笔记并放入 Obsidian 长期维护

---

## 当前已实现能力

- PDF -> JSON（基础抽取）
- JSON -> Markdown（模板生成）
- 可选 AI 总结（OpenAI / DeepSeek 兼容接口）
- Zotero API -> JSON（可直接用条目 key 拉元数据）

---

## 目录结构

```text
templates/
  literature_note_template.md
input/
  *.json
scripts/
  pdf_to_json.py
  zotero_to_json.py
  ai_enrich_json.py
  generate_note.py
output/
  *.md
examples/
  graph_agent_memory.md
```

---

## 使用方式总览

你有两条入口：

1. 从 PDF 开始（最常用）
2. 从 Zotero 条目 key 开始（元数据更稳）

每条入口都支持：
- 不用 AI（只抽取可抓到的信息）
- 用 AI（自动补全总结字段，或全部模块）

---

## 方式 A：从 PDF 开始

### A1. 不用 AI（纯脚本抽取）

```powershell
python scripts/pdf_to_json.py "你的论文.pdf" --output input\paper.json
python scripts/generate_note.py input\paper.json
```

生成文件：
- `input/paper.json`
- `output/<标题>.md`

### A2. 使用 AI 自动补全

先设置 AI 环境变量（以 DeepSeek 为例）：

```powershell
$env:AI_PROVIDER="deepseek"
$env:AI_API_KEY="你的API_KEY"
$env:AI_MODEL="deepseek-chat"
# 可选：
# $env:AI_BASE_URL="https://api.deepseek.com"
```

然后执行：

```powershell
python scripts/pdf_to_json.py "你的论文.pdf" --ai-summary --ai-fill-mode all --output input\paper_ai.json
python scripts/generate_note.py input\paper_ai.json
```

说明：
- `--ai-summary`：开启 AI
- `--ai-fill-mode all`：尽量填满 JSON 全部模块字段
- 若想只填关键字段，可改为 `--ai-fill-mode key`

---

## 方式 B：从 Zotero 条目 key 开始

### B1. 配置 Zotero API 环境变量

```powershell
$env:ZOTERO_USER_ID="你的Zotero用户ID"
$env:ZOTERO_API_KEY="你的Zotero API Key"
$env:ZOTERO_LIBRARY_TYPE="user"   # 或 group
```

### B2. 拉取元数据生成 JSON

```powershell
python scripts/zotero_to_json.py --item-key 该论文的条目key --include-annotations --output input\该论文的条目key.json
```

### B3. 直接生成笔记（不走 AI）

```powershell
python scripts/generate_note.py input\该论文的条目key.json
```

### B4. 先走 AI 再生成笔记（可选）

```powershell
python scripts/ai_enrich_json.py input\该论文的条目key.json --fill-mode all --overwrite
python scripts/generate_note.py input\该论文的条目key_enriched.json
```

### B5. 将之前生成的json变为md文件

```powershell
python scripts/generate_note.py input\文件名.json
```

---

## AI 配置说明

支持 OpenAI / DeepSeek（OpenAI 兼容接口）：

- `AI_PROVIDER`：`openai` 或 `deepseek`
- `AI_API_KEY`：你的 API Key
- `AI_MODEL`：模型名
- `AI_BASE_URL`：可选（自定义兼容服务时需要）

OpenAI 示例：

```powershell
$env:AI_PROVIDER="openai"
$env:AI_API_KEY="你的API_KEY"
$env:AI_MODEL="gpt-4o-mini"
```

---

## Zotero 与 Obsidian 如何配合

- Zotero：放 PDF、做批注、做标签、云同步文献资产
- 本项目脚本：把元数据/文本转成结构化 JSON 与 Markdown
- Obsidian：长期维护 survey 地图、关键论文池、个人核心文献库

---

## 常见问题

### 1) 没有 Bash 怎么办？
Windows 直接用 PowerShell 就行，不需要 Bash。

### 2) 不用 AI 能跑吗？
可以。`pdf_to_json.py` 不加 `--ai-summary` 就是纯脚本模式。

### 3) Zotero 批注会自动进 Markdown 吗？
从 Zotero 入口 (`zotero_to_json.py --include-annotations`) 可把可获取的批注文本写入 JSON 证据字段，再由 `generate_note.py` 生成到 Markdown。

---

## 最短命令（新手先跑通）

```powershell
python scripts/pdf_to_json.py "你的论文.pdf" --output input\demo.json
python scripts/generate_note.py input\demo.json
```

跑通后再加 AI 或 Zotero API。
