---
title: "VOYAGER: An Open-Ended Embodied Agent with Large Language Models"
authors: ["Guanzhi Wang", "Yuqi Xie", "Yunfan Jiang", "Ajay Mandlekar", "Chaowei Xiao", "Yuke Zhu", "Anima Anandkumar"]
year: "needs-check"
venue: "needs-check"
doi: "needs-check"
paper_type: "method"
zotero_item_key: "7ERPHPWY"
pdf_key: "29YDZHW3"
tags: ["method"]
one_sentence_summary: "VOYAGER 是首个在 Minecraft 中利用 GPT-4 实现无需微调的终身学习具身智能体，通过自动课程、技能库和迭代提示机制持续探索并获取多样技能。"
research_relation: "本文提出了一种基于大语言模型的具身智能体方法，属于将 LLM 用于开放世界任务规划与执行的典型工作，与我的研究兴趣（LLM 驱动的自主智能体）高度相关。"
core_library_decision: "候选"
core_library_reason: "该工作是 LLM 驱动具身智能体的里程碑式方法，展示了终身学习、技能组合与泛化能力，对后续研究有重要参考价值。"
---

# VOYAGER: An Open-Ended Embodied Agent with Large Language Models

## 一句话定位
VOYAGER 是首个在 Minecraft 中利用 GPT-4 实现无需微调的终身学习具身智能体，通过自动课程、技能库和迭代提示机制持续探索并获取多样技能。

## 为什么要读这篇
学习如何利用 LLM 实现开放世界中的持续探索、技能积累与零样本泛化，以及自动课程与迭代提示机制的设计。

## 核心问题
如何让具身智能体在开放世界（如 Minecraft）中无需人类干预地持续探索、学习新技能并泛化到新任务。

## Survey 专用（综述 / taxonomy）

### 覆盖范围
本文聚焦于 LLM 在具身智能体中的应用，特别是基于代码作为动作空间的方法，以及终身学习与技能库的构建。

### Taxonomy（分类框架）
按方法分类：基于 LLM 的规划（如 SayCan）、基于代码的智能体（如 Code as Policies）、技能库方法（如 Skill Library）。

### 关键论文池
- needs-check
- needs-check
- needs-check

### 研究空白与机会
现有方法通常需要人类设计课程或微调模型，缺乏自动探索与技能积累机制；且难以处理长时域任务和灾难性遗忘。

## 普通方法论文专用（非方法论文可写 N/A）

### 方法思路
利用 GPT-4 作为核心决策模块，通过自动课程生成探索任务，技能库存储可执行代码，迭代提示机制结合环境反馈改进程序。

### Framework / Pipeline
三个组件：1）自动课程：基于当前技能与状态生成下一个探索任务；2）技能库：存储已验证的技能代码，支持检索与组合；3）迭代提示：将环境反馈、错误信息和自我验证结果输入 GPT-4 以优化代码。

### 实验结果（不确定则写 needs-check）
VOYAGER 在 Minecraft 中收集 3.3 倍更多独特物品，旅行距离长 2.3 倍，解锁科技树里程碑快 15.3 倍；在新世界中零样本解决新任务，而基线方法失败。

## Zotero 批注与原文证据
- Zotero item key: 7ERPHPWY
- PDF key: 29YDZHW3
- 批注摘录:
- VOYAGER consists of three key components: an automatic curriculum for open-ended exploration, a skill library for increasingly complex behaviors, and an iterative prompting mechanism that uses code as action space. | 页码: 2
- Hallucinations. The automatic curriculum occasionally proposes unachievable tasks. | 页码: 10
- Inaccuracies. Despite the iterative prompting mechanism, there are still cases where the agent gets stuck and fails to generate the correct skill. | 页码: 10
- The GPT-4 API incurs significant costs. | 页码: 10
- Cost. | 页码: 10

## 可引用材料（写作可直接复用）
- 自动课程与技能库设计
- 迭代提示机制
- 代码作为动作空间
- 终身学习与灾难性遗忘缓解

## 个人核心文献库维护

### 与我研究主线关系
本文提出了一种基于大语言模型的具身智能体方法，属于将 LLM 用于开放世界任务规划与执行的典型工作，与我的研究兴趣（LLM 驱动的自主智能体）高度相关。

### 是否纳入核心文献库
候选

### 纳入/暂缓理由
该工作是 LLM 驱动具身智能体的里程碑式方法，展示了终身学习、技能组合与泛化能力，对后续研究有重要参考价值。

### 复核计划（时间/触发条件）
纳入核心库，后续需对比其他 LLM 智能体方法（如 Ghost in the Minecraft）并分析其局限性。

## 我的判断
方法创新性强，实验充分，但存在幻觉、成本高、复杂任务失败等问题，且依赖 GPT-4 黑盒。

## 待复核问题
- 如何减少自动课程中的不可达任务？
- 如何降低 GPT-4 API 成本？
- 技能库如何扩展到更复杂的组合任务？
- 能否用开源模型替代 GPT-4？

## 后续行动
1. 复现 VOYAGER 的核心机制，验证其在其他环境中的效果。
2. 探索更高效的技能检索与组合方法。
3. 研究如何结合视觉语言模型减少对文本描述的依赖。
