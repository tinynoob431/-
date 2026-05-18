---
title: "MemGen: Weaving Generative Latent Memory for Self-Evolving Agents"
aliases: ["MemGen"]
tags: ["method"]

zotero_item_key: "2DJECDW9"
pdf_key: "needs-check"
doi: "needs-check"
year: "2025"
venue: "arXiv preprint"
authors: ["Guibin Zhang", "Muxin Fu", "Shuicheng Yan"]
paper_type: "method"
status: "seed" # seed / skimmed / read / cited

zotero_collections: ["needs-check"]
zotero_tags: ["needs-check"]
canonical_tags: ["needs-check"]
candidate_tags: ["needs-check"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "提出新型生成式潜在记忆机制，性能超越现有方法，展现出人类认知特征，对智能体自我进化研究有重要启发。"
research_relation: "与研究方向高度相关，都关注LLM智能体的记忆增强和自我进化。"
---

# MemGen: Weaving Generative Latent Memory for Self-Evolving Agents

## 核心简介
> 先写清“问题链”：要解决什么关键问题、瓶颈在哪里、本文方法与贡献是什么。每条都尽量绑定证据来源（section / table / figure / page）。

| 维度 | 内容 | 证据 |
| --- | --- | --- |
| 关键问题 | 现有智能体记忆方法无法实现类似人类的记忆与推理的紧密交织，限制自我进化能力。 | Existing paradigms remain constrained: parametric memory forcibly adjusts model parameters, and retrieval-based memory externalizes experience into structured databases, yet neither captures the fluid interweaving of reasoning and memory that underlies human cognition. |
| 核心瓶颈 | 参数记忆导致灾难性遗忘，检索记忆受限于上下文工程，缺乏认知流畅性。 | 参数记忆导致灾难性遗忘（‘catastrophic forgetting, i.e., the erosion of general knowledge’），检索记忆依赖上下文工程，无法实现无缝内部融合（‘its efficacy is fundamentally tethered to context engineering... without achieving the fluid, seamless integration characteristic of truly internalized memory’）。 |
| 其他做法 | 参数记忆（FireAct, AgentLumos等），检索记忆（ExpeL, AWM等），潜在记忆（Coconut, CoDI等）。 | 对比方法包括外部记忆系统ExpeL和AWM，以及RL方法GRPO（参见摘要：‘surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%’）；参数记忆方法如FireAct、AgentLumos（引言及相关工作）；检索记忆方法如存储原始轨迹、高级经验、压缩技能等。 |
| 本文方法 | MemGen通过在推理过程中动态插入生成式潜在token序列作为记忆，实现记忆与认知的深度交织。 | It consists of a memory trigger, which monitors the agent’s reasoning state to decide explicit memory invocation, and a memory weaver, which takes the agent’s current state as stimulus to construct a latent token sequence as machine-native memory to enrich its reasoning. |
| 主要贡献 | 提出MemGen，一种动态生成式潜在记忆框架，实现了推理与记忆的紧密交织；在8个基准上显著超越外部记忆系统和GRPO；无需显式监督，自发演化出类似人类的规划记忆、程序记忆和工作记忆能力。 | More importantly, we find that without explicit supervision, MemGen spontaneously evolves distinct human-like memory faculties, including planning memory, procedural memory, and working memory, suggesting an emergent trajectory toward more naturalistic forms of machine cognition. |
| 关键结果 | 在八个基准上，MemGen超越ExpeL和AWM最高38.22%，超过GRPO最高13.44%，并展现强跨领域泛化能力。 | MemGen surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%, and exhibits strong cross-domain generalization ability. |
| 适用场景 | 基于当前信息推断：适用于需要从环境交互中自我进化的LLM代理任务，如工具调用、规划、问答、多步推理等。 | needs-check |
| 主要限制 | 基于当前信息推断：潜在记忆可解释性不足；可能需要额外训练记忆模块，增加计算开销；仅在特定基准上验证，泛化到其他任务的鲁棒性未知。 | needs-check |

## 一句话定位
MemGen提出一种动态生成式潜在记忆框架，通过记忆触发器和编织器实现推理与记忆的流畅交织，显著提升智能体性能并涌现出人类般的记忆功能。

## 方法主图 / Framework
![[assets/2DJECDW9/framework_p08_n044.png]]

| 项目 | 内容 |
| --- | --- |
| 图来源 | Auto extracted from PDF page 8 image 44 |
| 图类型 | framework / architecture / pipeline (needs-check) |
| 核心模块 | memory trigger, memory weaver |
| 数据流 / 推理流 | 1. Agent接收当前状态st和任务。2. Memory Trigger监控推理状态，决定是否调用记忆。3. 若触发，Memory Weaver以st为刺激，生成潜在记忆token序列mt。4. 将mt插入到agent的推理上下文中（作为额外的输入token）。5. Agent基于增强的状态生成动作at。6. 执行at，环境更新到st+1。7. 重复直到任务完成。 |
| 这张图说明了什么 | MemGen是一个生成式记忆框架，让LLM代理在推理过程中动态生成潜在记忆token，模拟人类认知中记忆与推理的紧密交织。它包含一个记忆触发器来决定何时调用记忆，以及一个记忆编织器来生成机器原生的潜在记忆序列，这些记忆插入到推理过程中以丰富认知。 |
| 需要回查 | False |

## 方法速写

### 任务设定
- 输入 / 环境 / 数据：当前状态st（文本描述），可能包含任务查询、历史交互和上下文。
- 输出 / 目标：代理生成的动作序列at，以及潜在记忆token序列（作为中间输出），最终输出为任务结果或答案。
- 约束 / 假设：LLM能够利用潜在token作为记忆载体；记忆触发基于推理状态有效；潜在记忆空间可以编码可迁移的通用经验；环境提供奖励信号用于优化。

### 核心机制
- 模块 1：Memory Trigger
- 模块 2：Memory Weaver
- 训练流程：基于当前信息推断：使用强化学习（可能基于GRPO）联合优化代理策略πθ和记忆系统M，最大化期望奖励。记忆系统自发进化，无需显式监督信号。
- 推理流程：加载训练好的Memory Weaver和代理模型。推理时，代理逐步处理输入状态，Memory Trigger根据模型隐藏状态或输出决定是否调用记忆；若调用，Memory Weaver生成潜在token，插入到代理的上下文中；代理基于增强的上下文继续生成动作。此过程可重复多次。

### 公式 / 算法
1. \(z_{t,j} \sim \pi_\theta(\cdot | s_t, z_{t,<j})\); 2. \(\max_{\theta,M} \mathbb{E}_{x\sim D, \tau\sim\pi_\theta,M} [R(\tau)]\); 3. \(m_t = f_M(s_t, H, m_{<t})\)

- 符号说明：\(z_{t,j}\)：第t步的第j个潜在记忆token；\(s_t\)：智能体状态；\(\pi_\theta\)：策略网络；\(R(\tau)\)：轨迹奖励；\(m_t\)：记忆表示；\(f_M\)：记忆生成函数；\(H\)：历史经验
- 这一部分解决的问题：方程(1)定义潜在记忆token的生成过程；方程(2)为联合优化策略和记忆系统的最大化期望奖励目标；方程(3)定义了动态记忆生成的通用形式。
- 与 baseline 的关键差异：与基线方法相比，MemGen在token级别动态生成和插入记忆，而ExpeL等任务级别或步骤级别记忆调用。方程(3)的粒度更细。

## 实验与结果
| 项目 | 内容 | 证据 |
| --- | --- | --- |
| 数据集 / Benchmark | 基于当前信息推断：八个基准测试，但片段未列出具体名称。 | needs-check |
| 模型 / Backbone | 基于当前信息推断：使用预训练LLM作为智能体主干，但未指定具体模型。 | needs-check |
| Baselines | ExpeL, AWM, GRPO | 论文摘要明确提及：'surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%'。 |
| Metrics | 基于当前信息推断：可能使用任务成功率或奖励，具体指标未明确。 | needs-check |
| 主结果 | MemGen surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%, and exhibits strong cross-domain generalization ability. | 摘要中的结果陈述：'MemGen surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%'。 |
| 消融实验 | 基于当前信息推断：未在片段中提供消融实验细节。 | needs-check |
| 效率 / 成本 | 基于当前信息推断：未在片段中提供效率或成本信息。 | needs-check |
| 失败案例 / 局限 | 基于当前信息推断：未在片段中提供错误分析。 | needs-check |

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
| 背景 | Existing paradigms remain constrained: parametric memory forcibly adjusts model parameters, and retrieval-based memory externalizes experience into structured databases, yet neither captures the fluid interweaving of reasoning and memory that underlies human cognition. | 论文摘要 |
| Gap | Existing memory paradigms fail to capture the fluid interweaving of reasoning and memory that underlies human cognition. | 论文摘要 |
| 方法比较 | MemGen 是一种动态生成式记忆框架，通过记忆触发器和记忆编织器在推理过程中交织生成潜在记忆 tokens，与外部记忆系统（如 ExpeL 和 AWM）相比性能提升最高 38.22%，超过 GRPO 达 13.44%，并展现跨域泛化能力。 | 摘要中明确提到 'MemGen surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%' |
| 实验证据 | 在 8 个基准上进行广泛实验，与 ExpeL、AWM、GRPO 等对比，性能显著提升；MemGen 还自发涌现计划记忆、程序记忆和工作记忆等类人记忆能力。 | 摘要及正文中描述了8个基准上的实验比较及涌现出的人类记忆类型 |
| 局限 | 基于当前信息推断：潜在记忆的可解释性有限，未明确讨论计算开销和对模型架构的依赖；论文未提及局限性。 | needs-check |

## Zotero 批注与原文证据
- Zotero item key: 2DJECDW9
- PDF key: needs-check
- 批注摘录: needs-check

## 个人核心文献库维护
- 与我研究主线关系：与研究方向高度相关，都关注LLM智能体的记忆增强和自我进化。
- 是否纳入核心库：candidate
- 纳入/排除理由：提出新型生成式潜在记忆机制，性能超越现有方法，展现出人类认知特征，对智能体自我进化研究有重要启发。
- 复核计划：include

## 我的判断
论文创新性地将潜在记忆与推理过程交织，模拟人类认知，性能提升显著，且有开放代码，值得纳入核心库；但缺乏理论分析和局限性讨论。

## 待复核清单
- [ ] 关键结果是否来自完整实验表格而非 abstract 概述？
- [ ] Baseline 是否公平（同数据、同预算、同评测协议）？
- [ ] 公式 / 算法步骤是否已回看原文并可复现？
- [ ] 是否记录了至少一个失败案例或边界条件？
- [ ] 我是否明确写出该论文与当前课题的直接关系？

## 待复核问题
- 潜在记忆的生成是否特定于某些 LLM 架构？
- 跨域泛化的具体边界是什么？
- 计算开销与推理延迟是否可接受？
- 记忆触发机制如何避免错误触发或遗漏？
- 涌现的记忆类型是否稳定可复现？
- 如何与持续性参数记忆结合？

## 后续行动
1. 查阅 MemGen 代码仓库以验证实现细节。
2. 对比其他潜在记忆方法（如 Coconut）深入理解差异。
3. 关注实验结果中的具体基准名称和设置。
4. 评估是否适用于我的研究场景。

## 元数据
| 项目 | 内容 |
| --- | --- |
| Authors | Guibin Zhang, Muxin Fu, Shuicheng Yan |
| Year | 2025 |
| Venue | arXiv preprint |
| DOI | needs-check |
| Zotero item key | 2DJECDW9 |
| PDF key | needs-check |
| Zotero collections | needs-check |
| Zotero tags | needs-check |
