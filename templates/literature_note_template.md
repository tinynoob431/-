---
title: "{{title}}"
aliases: {{aliases_yaml}}
tags: {{tags_yaml}}

zotero_item_key: "{{zotero_item_key}}"
pdf_key: "{{pdf_key}}"
doi: "{{doi}}"
year: "{{year}}"
venue: "{{venue}}"
authors: {{authors_yaml}}
paper_type: "{{paper_type}}"
paper_subtype: "{{paper_subtype}}" # survey/method/system/benchmark/dataset/empirical/theory/application
status: "{{status}}" # seed / skimmed / read / cited

zotero_collections: {{zotero_collections_yaml}}
zotero_tags: {{zotero_tags_yaml}}
canonical_tags: {{canonical_tags_yaml}}
candidate_tags: {{candidate_tags_yaml}}

core_library_decision: "{{core_library_decision}}" # candidate / include / exclude
core_library_reason: "{{core_library_reason}}"
research_relation: "{{research_relation}}"
---

# {{title}}

## 0. 先看这里
> [!abstract]
> **一句话定位**：{{one_sentence_summary}}  
> **论文类型**：{{paper_subtype}}  
> **问题**：{{core_problem}}  
> **方法**：{{method_one_liner}}  
> **结果**：{{headline_results}}  
> **是否纳入核心库**：`{{core_library_decision}}`  
> **理由**：{{core_library_reason}}  
> **为什么读**：{{why_read}}

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：{{core_problem}}
- 核心瓶颈：{{core_bottleneck}}
- 相比已有方法：{{other_methods}}

**主要贡献：**
{{main_contributions_numbered}}

**主要局限：**  
{{main_limitations}}

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：{{method_idea}}
- 关键设计：
{{core_modules_bulleted}}
- 流程概览：
{{pipeline_flow_indented}}
- 输入 / 数据来源：{{task_input}}
- 输出 / 评估对象：{{task_output}}

### 1.3 实验结论
- 数据集 / Benchmark：{{datasets}}
- Baselines：{{baselines}}
- Metrics：{{metrics}}
- 主结果：{{main_results_table_or_text}}
- 可信度判断：{{result_reliability}}
- 最关键图/表：{{most_important_figure_or_table}}
- 它说明了什么：{{figure_table_takeaway}}
- 效率 / 成本：{{efficiency_cost}}

### 1.4 我的判断与行动
- 值不值得细读：{{worth_deep_reading}}
- 对我当前研究的价值：{{value_for_my_research}}
- 可以借鉴的点：{{what_to_reuse}}
- 暂时不用管的点：{{what_to_ignore}}

**下一步行动：**
{{next_actions}}

## 2. 关键图表（可选）
{{framework_section}}

## 3. 进阶细节（按需展开）
{{advanced_details_block}}

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
{{evidence_quote_block}}

> [!note]- 我的批注 / Zotero 批注
{{zotero_note_block}}

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：{{canonical_tags_text}}
> - 候选标签：{{candidate_tags_text}}
> - 当前标签：{{tags_text}}
> - 研究关系：{{research_relation}}

## 6. 元数据（仅保留一份）
| 项目 | 内容 |
| --- | --- |
| Authors | {{authors_text}} |
| Year | {{year}} |
| Venue | {{meta_venue}} |
| DOI | {{meta_doi}} |
| Zotero item key | {{zotero_item_key}} |
| PDF key | {{meta_pdf_key}} |
| Zotero collections | {{meta_zotero_collections}} |
| Zotero tags | {{meta_zotero_tags}} |

## 7. 待复核问题
### 高优先级待复核
{{high_priority_checks}}

### 其他待复核问题
{{open_questions}}
