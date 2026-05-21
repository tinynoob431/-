---
title: "VOYAGER: An Open-Ended Embodied Agent with Large Language Models"
aliases: ["VOYAGER"]
tags: ["method", "llm-agent", "lifelong-learning", "embodied-agent", "minecraft", "skill-library"]

zotero_item_key: "7ERPHPWY"
pdf_key: "29YDZHW3"
doi: "needs-check"
year: "2023"
venue: "arXiv preprint arXiv:2305.16291"
authors: ["Guanzhi Wang", "Yuqi Xie", "Yunfan Jiang", "Ajay Mandlekar", "Chaowei Xiao", "Yuke Zhu", "Anima Anandkumar"]
paper_type: "method"
paper_subtype: "method" # survey/method/system/benchmark/dataset/empirical/theory/application
status: "seed" # seed / skimmed / read / cited

zotero_collections: ["needs-check"]
zotero_tags: ["needs-check"]
canonical_tags: ["llm-agent", "lifelong-learning", "embodied-agent", "minecraft", "skill-library"]
candidate_tags: ["open-ended-exploration", "automatic-curriculum", "iterative-prompting", "code-as-action", "gpt-4", "catastrophic-forgetting", "zero-shot-generalization", "react"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "提出技能库与迭代提示机制，对终身学习具身智能体设计有参考价值，但方法依赖GPT-4 API，成本较高。"
research_relation: "属于LLM驱动的具身智能体方向，聚焦终身学习与技能积累，与ReAct、Reflexion等基线对比，强调无需微调的黑盒查询方式。"
---

# VOYAGER: An Open-Ended Embodied Agent with Large Language Models

## 0. 先看这里
> [!abstract]
> **一句话定位**：提出VOYAGER，首个基于GPT-4的Minecraft终身学习智能体，通过自动课程、技能库和迭代提示机制实现开放世界探索与技能积累。
> **论文类型**：method
> **问题**：现有LLM智能体缺乏终身学习能力，无法在开放世界中持续探索、积累和迁移技能。
> **方法**：VOYAGER结合自动课程、可执行代码技能库与迭代提示机制，使智能体在Minecraft中持续探索并积累技能。
> **结果**：VOYAGER在Minecraft中获取3.3倍独特物品、旅行2.3倍距离、解锁科技树里程碑快15.3倍（相比先前SOTA），并能零样本泛化到新世界。
> **是否纳入核心库**：`candidate`
> **理由**：提出技能库与迭代提示机制，对终身学习具身智能体设计有参考价值，但方法依赖GPT-4 API，成本较高。
> **为什么读**：学习如何利用LLM构建开放世界终身学习智能体，特别是自动课程、技能库与迭代提示的设计。

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：现有LLM智能体缺乏终身学习能力，无法在开放世界中持续探索、积累和迁移技能。
- 核心瓶颈：自动课程偶尔提出不可达任务（幻觉）；迭代提示仍可能卡住；GPT-4 API成本高昂。
- 相比已有方法：ReAct、Reflexion、AutoGPT等基线方法在开放探索中表现不佳，无法有效积累技能。

**主要贡献：**
1. 提出VOYAGER，首个LLM驱动的具身终身学习智能体，在Minecraft中无需人工干预持续探索、获取技能并发现新知识。
2. 设计自动课程（automatic curriculum）最大化探索，技能库（skill library）存储可执行代码，迭代提示机制（iterative prompting mechanism）利用环境反馈改进程序。
3. 技能具有时间延展性、可解释性和组合性，缓解灾难性遗忘，实现快速技能积累。

**主要局限：**
推断：自动课程偶尔提出无法完成的任务（幻觉）； 迭代提示机制仍存在卡住无法生成正确技能的情况； GPT-4 API调用成本高昂。

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：利用LLM的常识和推理能力，通过自动课程、技能库和迭代提示机制，实现开放世界中的终身学习。
- 关键设计：
  - 自动课程
  - 技能库
  - 迭代提示机制
- 流程概览：
  1. 自动课程根据智能体状态和世界状态提出下一个任务。
  2. 从技能库中检索相关技能作为初始代码。
  3. 迭代提示机制执行代码，收集环境反馈、执行错误和自我验证结果。
  4. 根据反馈改进代码，直至任务成功。
  5. 成功技能被添加到技能库。
- 输入 / 数据来源：当前智能体状态（如位置、物品清单）和世界状态（如周围方块）。
- 输出 / 评估对象：可执行代码（如Minecraft动作序列）和技能库更新。

### 1.3 实验结论
- 数据集 / Benchmark：Minecraft
- Baselines：AutoGPT, ReAct, Reflexion
- Metrics：unique items discovered, distance traveled, tech tree milestones unlocked, zero-shot task success rate
- 主结果：VOYAGER获得3.3倍独特物品，旅行距离延长2.3倍，解锁关键技术树里程碑速度比先前SOTA快15.3倍。它是唯一解锁钻石等级的方法。零样本泛化结果见表2。
- 可信度判断：结果基于多次试验（零样本3次）。但仅一个种子世界？需检查统计显著性细节。
- 最关键图/表：Figure 1: Unique items discovered over prompting iterations; Table 2: Zero-shot generalization to unseen tasks.
- 它说明了什么：图1显示VOYAGER随时间持续发现更多物品。表2显示VOYAGER（无论有无技能库）在未见任务上成功，而基线完全失败。
- 效率 / 成本：GPT-4 API incurs significant costs (mentioned in limitations). No specific cost numbers provided.

### 1.4 我的判断与行动
- 值不值得细读：是，该方法在Minecraft开放世界中实现了持续学习，技能库和迭代提示机制设计精巧，对LLM智能体研究有重要参考价值。
- 对我当前研究的价值：高，VOYAGER的技能库和自动课程设计可借鉴用于其他开放世界持续学习任务，迭代提示机制对代码生成智能体有启发。
- 可以借鉴的点：技能库的存储与检索机制、自动课程设计、迭代提示中的自我验证与错误反馈循环。
- 暂时不用管的点：Minecraft特定实现细节（如具体API调用），除非研究场景相同。

**下一步行动：**
1. 深入阅读方法部分，理解技能库的向量检索和迭代提示的具体实现。
2. 对比其他持续学习方法（如RL-based）的优缺点。
3. 考虑在类似开放世界任务中复现或改进技能库机制。

## 2. 关键图表（可选）
![[assets/7ERPHPWY/framework_p08_n086.png]]

- 图/表来源：Auto extracted from PDF page 8 image 86
- 图/表类型：framework / architecture / pipeline (待核查)
- 图/表说明：
  - 结构：VOYAGER是一个LLM驱动的具身终身学习框架，通过自动课程生成探索任务，技能库存储可复用的代码技能，迭代提示机制利用环境反馈不断改进技能，实现持续学习和知识积累。
  - 过程：自动课程根据智能体状态和世界状态提出下一个任务；从技能库中检索相关技能作为初始代码；迭代提示机制执行代码，收集环境反馈、执行错误和自我验证结果。
  - 意义：图1显示VOYAGER随时间持续发现更多物品。表2显示VOYAGER（无论有无技能库）在未见任务上成功，而基线完全失败。
- 需回查项：否

## 3. 进阶细节（按需展开）
> [!info]- 核心设计细节
> - 训练策略 / 构造流程：无需微调模型参数，仅通过黑盒查询GPT-4进行上下文学习。
> - 推理流程 / 评估流程：自动课程提出任务 → 技能库检索初始代码 → 迭代提示机制执行并改进代码 → 任务成功则添加技能到库。
> - 假设条件：环境提供代码API；LLM（GPT-4）可通过黑盒查询调用；技能可表示为可执行代码。
> - 关键部分1：自动课程：基于当前技能水平和世界状态，使用LLM生成探索任务，最大化探索进度。
> - 关键部分2：技能库：存储可执行代码技能，支持检索和组合，避免灾难性遗忘。

> [!info]- 公式与算法细节
> - 关键形式: 待核查：当前摘录未提供统一数学公式或标准算法式，需回查方法 / 附录。
> - 该论文当前更偏框架 / 流程描述，公式细节需回查原文。
> - 与 baseline 差异: 待核查：需回查原文。

> [!info]- 实验细节
> - 模型 / Backbone：GPT-4
> - 消融实验：Ablation: VOYAGER without skill library still outperforms baselines but with fewer successes (e.g; Diamond Pickaxe 2/3 vs 1/3). AutoGPT with skill library improves but still lags.
> - 失败案例 / 边界：Hallucinations: automatic curriculum occasionally proposes unachievable tasks. Inaccuracies: iterative prompting still fails sometimes. Cost: GPT-4 API expensive.
> - 数据集证据：Minecraft (via MineDojo environment)
> - Backbone证据：GPT-4 (blackbox queries)
> - Baseline证据：AutoGPT, ReAct, Reflexion (explicitly named in paper)
> - 指标证据：Unique items discovered, distance traveled, tech tree milestones (wood/stone/iron/diamond), zero-shot success rate (fraction of trials)
> - 主结果证据：VOYAGER obtains 3.3× more unique items, travels 2.3× longer distances, unlocks wooden level 15.3× faster, stone 8.5× faster, iron 6.4× faster, and is only one to unlock diamond. Zero-shot: VOYAGER succeeds on 4 tasks; baselines fail all.
> - 消融证据：VOYAGER w/o skill library: Diamond Pickaxe 2/3, Golden Sword 3/3, Lava Bucket 3/3, Compass 26 iterations. AutoGPT w/ skill library: Diamond Pickaxe 1/3, Golden Sword 1/3, Lava Bucket 0/3, Compass 2/3.
> - 效率证据：GPT-4 API cost mentioned as limitation; no quantitative efficiency comparison.
> - 失败证据：Hallucinations in curriculum; iterative prompting sometimes fails; cost of GPT-4.

> [!info]- 可引用素材（写作时再看）
> - 背景：LLM-based agents (ReAct, Reflexion, AutoGPT), lifelong learning, Minecraft agents (VPT), code as action space.
> - 背景来源：待核查：需回查原文。
> - Gap：现有LLM驱动的智能体不具备持续学习能力，无法在长时间跨度内逐步获取、更新、积累和迁移知识。
> - Gap来源：引言部分：'However, these agents are not lifelong learners that can progressively acquire, update, accumulate, and transfer knowledge over extended time spans [31, 32].'
> - 方法比较：VOYAGER与ReAct、Reflexion、AutoGPT等基线方法在Minecraft环境中进行对比，在探索效率、科技树解锁速度、地图覆盖范围和零样本泛化能力上均显著领先。
> - 方法比较来源：第3.3节评估结果：'VOYAGER obtains 3.3× more unique items, travels 2.3× longer distances, and unlocks key tech tree milestones up to 15.3× faster than prior SOTA.'
> - 实验证据：在Minecraft中评估探索性能（发现独特物品数量）、科技树掌握（工具等级解锁速度）、地图遍历距离和零样本泛化到未见任务的能力。
> - 实验证据来源：第3.3节评估结果及表2零样本泛化结果。
> - 局限：推断：1. 自动课程偶尔提出无法完成的任务（幻觉）。2. 尽管有迭代提示机制，智能体仍可能卡住无法生成正确技能。3. GPT-4 API成本高昂。
> - 局限来源：第10页局限性部分：'Hallucinations. The automatic curriculum occasionally proposes unachievable tasks.' 'Inaccuracies. Despite the iterative prompting mechanism, there are still cases where the agent gets stuck and fails to generate the correct skill.' 'The GPT-4 API incurs significant costs.'

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
> - **问题背景**：现有LLM智能体不是终身学习者，无法在长时间跨度内逐步获取、更新、积累和迁移知识。
>   来源：Abstract / Introduction
>
> - **核心瓶颈**：缺乏自动课程导致探索效率低，技能无法持续积累，泛化能力差。
>   来源：Abstract / Introduction
>
> - **已有方法对比**：ReAct、Reflexion、AutoGPT等基线在开放探索中表现不佳，无法解锁高级科技树。
>   来源：Related Work / Introduction
>
> - **方法组成**：VOYAGER由三个组件组成：自动课程（根据当前技能和世界状态提出任务）、技能库（存储可执行代码技能）、迭代提示机制（结合环境反馈、执行错误和自我验证改进代码）。
>   来源：Abstract / Method
>
> - **主要贡献**：提出首个LLM驱动的具身终身学习智能体，实现持续探索、技能积累和零样本泛化。
>   来源：Abstract / Introduction
>
> - **主结果**：获取63种独特物品（3.3倍），旅行距离2.3倍，解锁木级快15.3倍、石级快8.5倍、铁级快6.4倍，唯一解锁钻石级。零样本泛化中成功完成钻石镐等任务。
>   来源：Abstract / Experiments
>
> - **局限信息**：自动课程幻觉、技能生成不准确、GPT-4 API成本高。
>   来源：Discussion / Limitation

> [!note]- 我的批注 / Zotero 批注
> - Zotero item key: 7ERPHPWY
> - PDF key: 29YDZHW3
> - 批注摘录：待核查：需回填 Zotero 真实批注。

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：llm-agent, lifelong-learning, embodied-agent, minecraft, skill-library
> - 候选标签：open-ended-exploration, automatic-curriculum, iterative-prompting, code-as-action, gpt-4, catastrophic-forgetting, zero-shot-generalization, react
> - 当前标签：method, llm-agent, lifelong-learning, embodied-agent, minecraft, skill-library
> - 研究关系：属于LLM驱动的具身智能体方向，聚焦终身学习与技能积累，与ReAct、Reflexion等基线对比，强调无需微调的黑盒查询方式。

## 6. 元数据（仅保留一份）
| 项目 | 内容 |
| --- | --- |
| Authors | Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Anima Anandkumar |
| Year | 2023 |
| Venue | arXiv preprint arXiv:2305.16291 |
| DOI | 待核查：需回查原文。 |
| Zotero item key | 7ERPHPWY |
| PDF key | 29YDZHW3 |
| Zotero collections | 待核查：需从 Zotero 同步。 |
| Zotero tags | 待核查：需从 Zotero 同步。 |

## 7. 待复核问题
### 高优先级待复核
- DOI / arXiv ID

### 其他待复核问题
- 如何降低对GPT-4等大模型的API成本依赖？
- 自动课程如何避免提出不可达任务？
- 技能库在更复杂环境（如机器人操作）中的可迁移性如何？
