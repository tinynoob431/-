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

## 核心简介
> 先写清“问题链”：要解决什么关键问题、瓶颈在哪里、本文方法与贡献是什么。每条都尽量绑定证据来源（section / table / figure / page）。

| 维度 | 内容 | 证据 |
| --- | --- | --- |
| 关键问题 | {{core_problem}} | {{evidence_core_problem}} |
| 核心瓶颈 | {{core_bottleneck}} | {{evidence_core_bottleneck}} |
| 其他做法 | {{other_methods}} | {{evidence_other_methods}} |
| 本文方法 | {{method_one_liner}} | {{evidence_method}} |
| 主要贡献 | {{main_contributions}} | {{evidence_contributions}} |
| 关键结果 | {{headline_results}} | {{evidence_results}} |
| 适用场景 | {{application_scenarios}} | {{evidence_scenarios}} |
| 主要限制 | {{main_limitations}} | {{evidence_limitations}} |

## 一句话定位
{{one_sentence_summary}}

## 方法主图 / Framework
![[{{framework_image_path}}]]

| 项目 | 内容 |
| --- | --- |
| 图来源 | {{framework_source}} |
| 图类型 | {{framework_type}} |
| 核心模块 | {{core_modules}} |
| 数据流 / 推理流 | {{pipeline_flow}} |
| 这张图说明了什么 | {{framework_explanation}} |
| 需要回查 | {{framework_needs_check}} |

## 方法速写

### 任务设定
- 输入 / 环境 / 数据：{{task_input}}
- 输出 / 目标：{{task_output}}
- 约束 / 假设：{{assumptions}}

### 核心机制
- 模块 1：{{module_1}}
- 模块 2：{{module_2}}
- 训练流程：{{training_strategy}}
- 推理流程：{{inference_pipeline}}

### 公式 / 算法
{{key_equations}}

- 符号说明：{{equation_symbols}}
- 这一部分解决的问题：{{equation_role}}
- 与 baseline 的关键差异：{{equation_vs_baseline}}

## 实验与结果
| 项目 | 内容 | 证据 |
| --- | --- | --- |
| 数据集 / Benchmark | {{datasets}} | {{evidence_datasets}} |
| 模型 / Backbone | {{backbone}} | {{evidence_backbone}} |
| Baselines | {{baselines}} | {{evidence_baselines}} |
| Metrics | {{metrics}} | {{evidence_metrics}} |
| 主结果 | {{main_results_table_or_text}} | {{evidence_main_results}} |
| 消融实验 | {{ablation_results}} | {{evidence_ablation}} |
| 效率 / 成本 | {{efficiency_cost}} | {{evidence_efficiency}} |
| 失败案例 / 局限 | {{error_analysis}} | {{evidence_failures}} |

## 复现与可信度检查
| 检查项 | 记录 |
| --- | --- |
| 数据划分是否清晰（train/val/test） | {{data_split}} |
| 随机种子与运行次数 | {{seeds}} |
| 超参数范围与选择策略 | {{hyperparameters}} |
| 训练硬件 / 软件环境 | {{infra}} |
| 统计显著性 / 方差报告 | {{significance_and_variance}} |
| 代码可用性 | {{code_availability}} |
| 数据可用性 | {{data_availability}} |
| 复现风险点 | {{repro_risks}} |

## 可引用材料
> 用于 related work / introduction / method comparison，尽量附来源。

| 用途 | 可引用内容 | 来源 |
| --- | --- | --- |
| 背景 | {{citable_background}} | {{citable_background_source}} |
| Gap | {{citable_gap}} | {{citable_gap_source}} |
| 方法比较 | {{citable_method_compare}} | {{citable_method_compare_source}} |
| 实验证据 | {{citable_experiment}} | {{citable_experiment_source}} |
| 局限 | {{citable_limitation}} | {{citable_limitation_source}} |

## Zotero 批注与原文证据
{{zotero_annotations_and_evidence}}

## 个人核心文献库维护
- 与我研究主线关系：{{research_relation}}
- 是否纳入核心库：{{core_library_decision}}
- 纳入/排除理由：{{core_library_reason}}
- 复核计划：{{core_library_review_plan}}

## 我的判断
{{my_assessment}}

## 待复核清单
- [ ] 关键结果是否来自完整实验表格而非 abstract 概述？
- [ ] Baseline 是否公平（同数据、同预算、同评测协议）？
- [ ] 公式 / 算法步骤是否已回看原文并可复现？
- [ ] 是否记录了至少一个失败案例或边界条件？
- [ ] 我是否明确写出该论文与当前课题的直接关系？

## 待复核问题
{{open_questions}}

## 后续行动
{{next_actions}}

## 元数据
| 项目 | 内容 |
| --- | --- |
| Authors | {{authors_text}} |
| Year | {{year}} |
| Venue | {{venue}} |
| DOI | {{doi}} |
| Zotero item key | {{zotero_item_key}} |
| PDF key | {{pdf_key}} |
| Zotero collections | {{zotero_collections_text}} |
| Zotero tags | {{zotero_tags_text}} |
