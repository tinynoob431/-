# 科研论文阅读管理工作流（Zotero + AI + Obsidian，最小可用版）

这是一个面向中文科研用户的最小可用工作流原型，目标是把论文阅读从“单次总结”升级为“可持续维护的知识系统”。

## 这个项目解决什么问题

常见问题：
- 论文 PDF、批注、总结分散在不同工具里，后续复用困难。
- 读 survey 时容易“看过很多，沉淀很少”，缺少统一结构。
- 个人核心文献库没有清晰入库标准，后续写作和复盘效率低。

本项目通过“固定模板 + 自动生成脚本”把文献笔记结构化，方便长期维护。

## 三个组件各自负责什么

- Zotero：管理 PDF、元数据、标签、批注，作为原始证据层。
- AI：把论文信息填入模板，生成结构化 Markdown 笔记初稿。
- Obsidian：维护 survey 地图、关键论文池、个人核心文献库，并通过双链持续迭代。

## 工作流（从 PDF 到 Obsidian）

1. 在 Zotero 中整理条目与标签，保留批注证据。
2. 把论文信息整理成 `input/*.json`（示例：`input/graph_agent_memory.json`）。
3. 运行脚本读取 JSON 与模板，自动生成笔记：
   - 模板：`templates/literature_note_template.md`
   - 脚本：`scripts/generate_note.py`
4. 输出 Markdown 到 `output/`，再放入 Obsidian Vault 管理。

## 如何同时支持两类目标

### 1) Survey 阅读
模板内置 survey 区块，覆盖：
- 覆盖范围
- taxonomy（分类框架）
- 关键论文池
- 研究空白与机会

用于快速形成“领域地图”。

### 2) 个人核心文献库维护
模板内置核心库维护区块，覆盖：
- 与本人研究关系
- 是否纳入核心库
- 纳入/暂缓理由
- 复核计划与后续行动

用于形成“可追踪、可复盘”的个人文献资产。

## 目录结构

```text
templates/
  literature_note_template.md
input/
  graph_agent_memory.json
scripts/
  generate_note.py
examples/
  graph_agent_memory.md
output/
```

## 运行脚本

在仓库根目录执行：

```bash
python scripts/generate_note.py input/graph_agent_memory.json
```

默认会生成：

```text
output/Graph-based Agent Memory.md
```

说明：
- 缺失字段统一填充为 `needs-check`，便于后续人工复核。
- 模板和示例笔记均为中文结构，适合直接放入中文 Obsidian 工作流。
