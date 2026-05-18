---
title: "VOYAGER: An Open-Ended Embodied Agent with Large Language Models"
aliases: ["needs-check"]
tags: ["method"]

zotero_item_key: "7ERPHPWY"
pdf_key: "29YDZHW3"
doi: "needs-check"
year: "needs-check"
venue: "needs-check"
authors: ["Guanzhi Wang", "Yuqi Xie", "Yunfan Jiang", "Ajay Mandlekar", "Chaowei Xiao", "Yuke Zhu", "Anima Anandkumar"]
paper_type: "method"
status: "seed" # seed / skimmed / read / cited

zotero_collections: ["needs-check"]
zotero_tags: ["needs-check"]
canonical_tags: ["needs-check"]
candidate_tags: ["needs-check"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "作为首个利用 LLM 实现开放世界终身学习的具身智能体，具有创新性和影响力。"
research_relation: "可能与开放世界自主智能体、终身学习和 LLM 应用研究相关。"
---

# VOYAGER: An Open-Ended Embodied Agent with Large Language Models

## 核心简介
> 先写清“问题链”：要解决什么关键问题、瓶颈在哪里、本文方法与贡献是什么。每条都尽量绑定证据来源（section / table / figure / page）。

| 维度 | 内容 | 证据 |
| --- | --- | --- |
| 关键问题 | 在开放世界环境中实现真正自主的终身学习，智能体需不断探索、获取技能并避免灾难性遗忘。 | needs-check |
| 核心瓶颈 | 现有方法依赖人类提供任务或需要微调，无法有效扩展技能、缺乏可解释性和组合性，且难以进行长期探索。 | needs-check |
| 其他做法 | 之前的方法包括基于强化学习的智能体（如 Dreamer, Plan4MC）和基于 LLM 的智能体（如 ReAct, DEPS），但它们通常需要预定义任务或人类演示，缺乏自动课程和技能组合能力。 | needs-check |
| 本文方法 | VOYAGER 通过自动课程探索最大化的任务提议、可执行代码技能库的存储与检索、以及利用环境反馈和自验证的迭代提示机制来改进程序。 | needs-check |
| 主要贡献 | ['1. 自动课程：基于探索进度自动生成任务，最大化探索。', '2. 技能库：存储和组合可执行代码作为技能，实现技能复用和快速能力增长。', '3. 迭代提示机制：利用环境反馈、执行错误和自验证进行程序改进。'] | needs-check |
| 关键结果 | 在 Minecraft 中，VOYAGER 获得的独特物品数量是之前 SOTA 的 3.3 倍，旅行距离 2.3 倍，解锁关键科技树里程碑的速度提升 15.3 倍。 | needs-check |
| 适用场景 | Minecraft 中的开放世界探索与任务执行，可迁移至其他具身环境和需要终身学习的自主智能体场景。 | needs-check |
| 主要限制 | ['自动课程有时会提出无法实现的任务（幻觉）。', '迭代提示机制仍有部分情况无法生成正确技能（不准确）。', '使用 GPT-4 API 成本高昂。'] | needs-check |

## 一句话定位
VOYAGER 是一个由大型语言模型驱动的具身终身学习智能体，能在 Minecraft 中通过自动课程、技能库和迭代提示机制持续探索世界、获取多样技能并做出新发现，无需人类干预。

## 方法主图 / Framework
![[assets/7ERPHPWY/framework_p08_n086.png]]

| 项目 | 内容 |
| --- | --- |
| 图来源 | Auto extracted from PDF page 8 image 86 |
| 图类型 | framework / architecture / pipeline (needs-check) |
| 核心模块 | needs-check |
| 数据流 / 推理流 | needs-check |
| 这张图说明了什么 | needs-check |
| 需要回查 | needs-check |

## 方法速写

### 任务设定
- 输入 / 环境 / 数据：needs-check
- 输出 / 目标：needs-check
- 约束 / 假设：needs-check

### 核心机制
- 模块 1：needs-check
- 模块 2：needs-check
- 训练流程：无传统训练阶段，通过黑盒查询 GPT-4 进行上下文学习，不使用参数微调。
- 推理流程：在环境循环中：1) 自动课程根据当前进度提议新任务；2) 查询 GPT-4 生成代码；3) 执行代码并收集反馈；4) 若失败，通过迭代提示（加入错误信息和自验证）重新生成代码；5) 将成功的代码存入技能库，并在未来任务中检索组合。

### 公式 / 算法
needs-check

- 符号说明：needs-check
- 这一部分解决的问题：needs-check
- 与 baseline 的关键差异：needs-check

## 实验与结果
| 项目 | 内容 | 证据 |
| --- | --- | --- |
| 数据集 / Benchmark | Minecraft 环境（非传统数据集，是交互式模拟世界） | needs-check |
| 模型 / Backbone | GPT-4 | needs-check |
| Baselines | 先前的 SOTA 方法，如基于 RL 的方法和早期 LLM 智能体（具体名称未列出，可能包括 Plan4MC、DEPS 等）。 | needs-check |
| Metrics | 独特物品数量、旅行距离、解锁科技树里程碑的速度。 | needs-check |
| 主结果 | 摘要中报告：独特物品多 3.3 倍，旅行距离 2.3 倍，关键科技树解锁快 15.3 倍。在新世界中利用技能库从零解决新任务，其他技术难以泛化。 | needs-check |
| 消融实验 | 未知，但可能有消融实验分析各组件作用。 | needs-check |
| 效率 / 成本 | GPT-4 API 调用成本高，限制了实际部署的可行性。 | needs-check |
| 失败案例 / 局限 | 主要错误：1) 自动课程产生不切实际的任务（幻觉）；2) 尽管有迭代提示，仍然有时生成错误技能（不准确）。 | needs-check |

## 复现与可信度检查
| 检查项 | 记录 |
| --- | --- |
| 数据划分是否清晰（train/val/test） | needs-check |
| 随机种子与运行次数 | needs-check |
| 超参数范围与选择策略 | needs-check |
| 训练硬件 / 软件环境 | needs-check |
| 统计显著性 / 方差报告 | needs-check |
| 代码可用性 | needs-check |
| 数据可用性 | needs-check |
| 复现风险点 | needs-check |

## 可引用材料
> 用于 related work / introduction / method comparison，尽量附来源。

| 用途 | 可引用内容 | 来源 |
| --- | --- | --- |
| 背景 | 相关背景：LLM 具身智能体（如 ReAct, SayCan）；Minecraft 中的智能体（如 DreamerV3, Plan4MC）；终身学习和强化学习中的灾难性遗忘。 | needs-check |
| Gap | 先前工作缺乏能够自主探索、终身学习且技能可组合的智能体，通常依赖人类指定任务或需要大量环境交互进行微调。 | needs-check |
| 方法比较 | 与先前的 SOTA 方法相比，VOYAGER 在探索效率、技能习得和泛化能力上均显著领先，特别是能在新世界中利用已学技能。 | needs-check |
| 实验证据 | 在 Minecraft 中的对比实验，定量展示了在独特物品、旅行距离和里程碑解锁速度上的巨大优势，并在新世界展示了泛化能力。 | needs-check |
| 局限 | 自动课程的幻觉问题、技能生成的不精确性以及 GPT-4 API 成本，是当前方法的主要局限。 | needs-check |

## Zotero 批注与原文证据
- Zotero item key: 7ERPHPWY
- PDF key: 29YDZHW3
- 批注摘录:
- VOYAGER consists of three key components: an automatic curriculum for open-ended exploration, a skill library for increasingly complex behaviors, and an iterative prompting mechanism that uses code as action space. | 页码: 2
- Hallucinations. The automatic curriculum occasionally proposes unachievable tasks. | 页码: 10
- Inaccuracies. Despite the iterative prompting mechanism, there are still cases where the agent gets stuck and fails to generate the correct skill. | 页码: 10
- The GPT-4 API incurs significant costs. | 页码: 10
- Cost. | 页码: 10

## 个人核心文献库维护
- 与我研究主线关系：可能与开放世界自主智能体、终身学习和 LLM 应用研究相关。
- 是否纳入核心库：candidate
- 纳入/排除理由：作为首个利用 LLM 实现开放世界终身学习的具身智能体，具有创新性和影响力。
- 复核计划：纳入核心文献库，用于跟踪基于 LLM 的开放世界终身学习进展。

## 我的判断
工作具有创新性，巧妙利用 LLM 的代码生成和推理能力实现自主探索和技能增长，但受限于语言模型自身的可靠性和成本。

## 待复核清单
- [ ] 关键结果是否来自完整实验表格而非 abstract 概述？
- [ ] Baseline 是否公平（同数据、同预算、同评测协议）？
- [ ] 公式 / 算法步骤是否已回看原文并可复现？
- [ ] 是否记录了至少一个失败案例或边界条件？
- [ ] 我是否明确写出该论文与当前课题的直接关系？

## 待复核问题
- 如何减少自动课程中的幻觉？
- 能否将技能库迁移到其他环境或实体？
- 如何降低对昂贵 API 的依赖，实现本地化部署？
- 如何确保生成代码安全性？
- 长期探索中如何避免危险行为？

## 后续行动
1. 阅读论文全文，深入理解自动课程和迭代提示的具体实现。
2. 查看代码开源情况，尝试复现关键部分。
3. 思考将该方法应用到其他具身环境的可能。

## 元数据
| 项目 | 内容 |
| --- | --- |
| Authors | Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Anima Anandkumar |
| Year | needs-check |
| Venue | needs-check |
| DOI | needs-check |
| Zotero item key | 7ERPHPWY |
| PDF key | 29YDZHW3 |
| Zotero collections | needs-check |
| Zotero tags | needs-check |
