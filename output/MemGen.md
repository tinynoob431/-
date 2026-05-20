---
title: "MemGen: Weaving Generative Latent Memory for Self-Evolving Agents"
aliases: ["MemGen"]
tags: ["method", "llm-agent", "agent-memory", "latent-memory", "generative-memory", "self-evolution", "self-evolving-agents"]

zotero_item_key: "2DJECDW9"
pdf_key: "needs-check"
doi: "needs-check"
year: "2025"
venue: "needs-check"
authors: ["Guibin Zhang", "Muxin Fu", "Shuicheng Yan"]
paper_type: "method"
paper_subtype: "method" # survey/method/system/benchmark/dataset/empirical/theory/application
status: "seed" # seed / skimmed / read / cited

zotero_collections: ["needs-check"]
zotero_tags: ["needs-check"]
canonical_tags: ["agent-memory", "latent-memory", "llm-agent", "self-evolving-agents", "generative-memory"]
candidate_tags: ["agent-memory", "latent-memory", "llm-agent", "self-evolving-agents", "generative-memory", "memory-trigger", "memory-weaver", "latent-token"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "提出新颖的生成式隐记忆范式，性能出色，并涌现出计划记忆、程序记忆等类人特质，潜力较大。"
research_relation: "拓展了隐式记忆研究，通过在推理中动态生成记忆令牌，弥合参数记忆与检索记忆的鸿沟。"
---

# MemGen: Weaving Generative Latent Memory for Self-Evolving Agents

## 0. 先看这里
> [!abstract]
> **一句话定位**：MemGen提出一种动态生成记忆框架，在LLM推理过程中穿插生成隐式记忆令牌，使智能体借助类人记忆能力自我进化。
> **论文类型**：method
> **问题**：现有参数记忆会灾难性遗忘，检索记忆依赖僵硬的上下文工程，均无法实现人类般与推理融为一体的记忆。
> **方法**：MemGen is a dynamic generative memory framework that interleaves latent memory tokens into LLM agent reasoning via a Memory Trigger（记忆触发器） and a Memory Weaver（记忆编织器）, enabling self-evolving problem-solving.
> **结果**：Surpasses leading external memory systems ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%, and exhibits strong cross-domain generalization across eight benchmarks.
> **是否纳入核心库**：`candidate`
> **理由**：提出新颖的生成式隐记忆范式，性能出色，并涌现出计划记忆、程序记忆等类人特质，潜力较大。
> **为什么读**：探索更贴近人类认知的智能体记忆机制，实现记忆与推理的深度交织，实验效果显著且记忆行为自发分化。

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：现有参数记忆会灾难性遗忘，检索记忆依赖僵硬的上下文工程，均无法实现人类般与推理融为一体的记忆。
- 核心瓶颈：参数记忆修改参数导致遗忘，检索记忆仅外部化经验，缺乏原生内化与推理的紧耦合。
- 相比已有方法：参数记忆（FireAct、AgentLumos等）、检索记忆（ExpeL、AWM、G-Memory）、隐记忆（Wang等、Hu等）及隐式计算（Coconut、CODI、LatentR3）。

**主要贡献：**
1. Identifies that existing parametric and retrieval-based memory paradigms fail to capture the fluid interweaving of reasoning and memory in human cognition.
2. Proposes MemGen with a Memory Trigger（记忆触发器） (for adaptive invocation) and a Memory Weaver（记忆编织器） (for generating latent memory tokens), achieving token-level memory integration.
3. Demonstrates significant performance improvements over baselines (up to 38.22% over ExpeL/AWM, 13.44% over GRPO) across eight benchmarks.
4. Shows emergent human-like memory faculties (planning, procedural, working memory) without explicit supervision, indicating a path toward more naturalistic machine cognition.

**主要局限：**
待核查：当前摘录未看到作者明确局限，需查看 limitation/discussion。

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：Integrate a generative latent memory into LLM agent reasoning at the token level, enabling dynamic, context-sensitive memory recall that weaves memory and cognition together, leading to emergent memory faculties.
- 关键设计：
  - Memory Trigger（记忆触发器）
  - Memory Weaver（记忆编织器）
  - and the base LLM agent.
- 流程概览：
  1. Agent begins generating a reasoning step tokens.
  2. Memory Trigger（记忆触发器） evaluates the current reasoning state to decide whether to invoke memory.
  3. If triggered, Memory Weaver（记忆编织器） generates a sequence of latent memory tokens conditioned on the state and past experiences.
  4. Generated latent token（潜在 token） are inserted into the token stream, enriching the context for subsequent reasoning.
  5. The agent continues reasoning with the augmented context; steps may repeat as needed.
  6. The process outputs the final Action（行动） or answer.
- 输入 / 数据来源：A task query and the agent's current context/state (e.g; previous reasoning steps, environment observations), along with access to a history of past experiences (trajectories) for memory generation.
- 输出 / 评估对象：The agent's actions or final answer, generated with interleaved latent memory tokens.

### 1.3 实验结论
- 数据集 / Benchmark：待核查：摘要未完整给出数据集细节，需查看实验部分。
- Baselines：ExpeL, AWM, GRPO
- Metrics：待核查：当前摘录未完整说明指标定义，需查看实验设置部分。
- 主结果：MemGen surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44% across eight benchmarks, and exhibits strong cross-domain generalization.
- 可信度判断：中等偏高：当前结果在基准对比中表现积极，但仍需回查指标定义、方差/显著性与完整实验设置。
- 最关键图/表：Figure 2 (overview of MemGen architecture)
- 它说明了什么：MemGen interleaves reasoning and memory via a Memory Trigger（记忆触发器） and weaver, generating latent token（潜在 token） sequences as dynamic memory at fine-grained, token-level granularity.
- 效率 / 成本：待核查：需查看效率与成本对比。

### 1.4 我的判断与行动
- 值不值得细读：是，但需先补实验设置与训练细节。
- 对我当前研究的价值：如果研究方向涉及LLM智能体的自适应记忆或认知机制，本文的动态生成式隐记忆思路有较高参考价值，尤其是记忆与推理交织的设计。
- 可以借鉴的点：记忆触发器与编织器的架构思想；隐记忆序列作为机器原生记忆的生成方式；自评估记忆调用策略；多层次记忆自发涌现的发现。
- 暂时不用管的点：具体的RL训练细节若与自身任务不相关可暂略；跨领域基准结果可仅关注通用趋势。

**下一步行动：**
1. 快速浏览方法图与算法伪代码，明确架构全貌。
2. 若决定深入，则精读第4章方法细节，并复现核心组件。
3. 调研隐空间计算与记忆的更多相关工作（如Coconut、LaRS等）。
4. 评估将MemGen应用于自身任务的可行性。

## 2. 关键图表（可选）
![[assets/2DJECDW9/framework_p08_n044.png]]

- 图/表来源：Auto extracted from PDF page 8 image 44
- 图/表类型：framework / architecture / pipeline (待核查)
- 图/表说明：
  - 结构：由 Memory Trigger（记忆触发器）和 Memory Weaver（记忆编织器）组成。
  - 过程：触发器判断是否调用记忆，编织器生成 latent token（潜在 token），并插入推理流。
  - 意义：将记忆从外部检索式附加转为推理过程中的 token 级内生交织。
- 需回查项：否

## 3. 进阶细节（按需展开）
> [!info]- 核心设计细节
> - 训练策略 / 构造流程：待核查：需回查方法与训练章节。
> - 推理流程 / 评估流程：The agent's reasoning is interleaved with memory: a Memory Trigger（记忆触发器） monitors the reasoning state and decides when to invoke memory; a Memory Weaver（记忆编织器） constructs a latent token（潜在 token） sequence from the current state，which is inserted into the reasoning process at fine-grained，token-level granularity. This yields a tightly interwoven cycle of memory and cognition.
> - 假设条件：待核查：假设包括可交互环境、奖励信号、token 级记忆调用与跨任务迁移能力，需回查原文。
> - 关键部分1：Memory Trigger（记忆触发器）: monitors the agent’s reasoning state and decides when to invoke latent memory.
> - 关键部分2：Memory Weaver（记忆编织器）: takes the agent’s current state and history to generate a latent token（潜在 token） sequence that augments the reasoning context.

> [!info]- 公式与算法细节
> $$
> z_{t,j} \sim \pi_\theta(\cdot \mid s_t, z_{t,<j})
> $$
>
> $$
> \max_{\theta,M} \mathbb{E}_{x \sim D,\, \tau \sim \pi_{\theta,M}}[R(\tau)]
> $$
>
> $$
> m_t = f_M(s_t, H, m_{<t})
> $$
>
> - 符号说明：
>   - equation_index：1；symbols：z_{t,j}: the j-th token of Action（行动） a_t; π_θ: policy; s_t: environment state at step t; z_{t,<j}: preceding tokens in the Action（行动）; equation_index：2；symbols：θ: policy parameters; M: memory system; D: task distribution; x: task; τ: trajectory; R: reward; equation_index：3；symbols：m_t: memory at step t; s_t: current state; H: history of past experiences; m_{<t}: previous memories.
> - 公式作用：
>   - equation_index：1；role：Defines the generation of Action（行动） tokens by the agent's policy; equation_index：2；role：Formalizes the overall optimization problem: jointly maximize expected reward by training policy and memory system; equation_index：3；role：Describes the general memory generation function, adaptable to different invocation granularities (task-level, step-level, token-level). MemGen's innovation is a more fine-grained, token-level invocation.
> - 与 baseline 差异：待核查：需回查原文。

> [!info]- 实验细节
> - 模型 / Backbone：待核查：当前摘录未明确骨干模型，需查看 setup 或 appendix。
> - 消融实验：待核查：需查看消融实验章节。
> - 失败案例 / 边界：Not provided in abstract or excerpt; paper may contain qualitative analysis of emergent memory faculties, but no explicit failure cases.
> - 数据集证据：待核查：需回查原文。
> - Backbone证据：待核查：需回查原文。
> - Baseline证据：Abstract: 'surpasses leading external memory systems such as ExpeL and AWM ... exceeds GRPO'
> - 指标证据：待核查：需回查原文。
> - 主结果证据：Abstract: 'up to 38.22% over ExpeL/AWM, 13.44% over GRPO'
> - 消融证据：待核查：需回查原文。
> - 效率证据：待核查：需回查原文。
> - 失败证据：待核查：需回查原文。

> [!info]- 可引用素材（写作时再看）
> - 背景：LLM驱动的智能体需要记忆机制，以从环境交互中逐步学习和进化。现有主要范式包括参数化记忆和检索式记忆。参数化记忆通过微调模型参数内化经验，但容易导致灾难性遗忘；检索式记忆将经验存储于外部数据库，但仅是上下文注入，缺乏推理与记忆的有机融合。
> - 背景来源：摘要和第1节：'Existing paradigms remain constrained: parametric memory forcibly adjusts model parameters, and retrieval-based memory externalizes experience into structured databases, yet neither captures the fluid interweaving of reasoning and memory that underlies human cognition.' 以及第1节对两种范式的详细描述。
> - Gap：现有记忆范式未能模拟人类认知中推理与记忆交织的流式过程，无法实现自然的内隐记忆生成与动态融合。
> - Gap来源：摘要中的gap陈述：'neither captures the fluid interweaving of reasoning and memory that underlies human cognition'
> - 方法比较：MemGen提出动态生成式隐记忆框架，包含记忆触发器与记忆编织器，在推理过程中逐token生成隐记忆序列，实现记忆与推理的紧密交织。相比ExpeL、AWM等检索式外部记忆系统，最高提升38.22%；比GRPO提升13.44%。
> - 方法比较来源：摘要：'...MemGen surpasses leading external memory systems such as ExpeL and AWM by up to 38.22%, exceeds GRPO by up to 13.44%...' 以及方法章节对记忆编织过程的描述。
> - 实验证据：在8个基准上评估，MemGen在多个领域表现出显著性能提升，并展现出跨领域泛化能力。无显式监督下，自发涌现出类似人类的规划记忆、程序记忆和工作记忆等多类记忆能力。
> - 实验证据来源：摘要：'Extensive experiments across eight benchmarks show that MemGen surpasses... More importantly, we find that without explicit supervision, MemGen spontaneously evolves distinct human-like memory faculties, including planning memory, procedural memory, and working memory...'
> - 局限：待核查：需回查原文。
> - 局限来源：待核查：需回查原文。

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
> - **问题背景**：Parametric memory (e.g; fine-tuning) leads to catastrophic forgetting; retrieval-based memory (e.g; ExpeL, AWM) externalizes experiences but fails to achieve fluid, seamless integration of memory and reasoning, as context is rigidly inserted.
>   来源：Abstract / Introduction
>
> - **核心瓶颈**：The core bottleneck is the lack of a memory mechanism that can be invoked dynamically and integratively during reasoning, akin to human cognition, to provide context without disrupting the reasoning flow.
>   来源：Abstract / Introduction
>
> - **已有方法对比**：Parametric memory approaches (FireAct, AgentLumos) update model parameters; retrieval-based memory systems store and retrieve experiences (ExpeL, AWM, G-Memory) or skills (AgentKB); prior latent memory methods exist but are not as tightly interwoven.
>   来源：Related Work / Introduction
>
> - **方法组成**：MemGen consists of a Memory Trigger（记忆触发器） that monitors the agent’s reasoning state to decide when to invoke memory, and a Memory Weaver（记忆编织器） that generates a latent token（潜在 token） sequence conditioned on the current state. These latent token（潜在 token） are inserted at the token level into the reasoning stream, creating a fine-grained interleaving of memory and cognition.
>   来源：Abstract / Method
>
> - **主要贡献**：The main contributions are (1) identifying the limitation of existing memory paradigms; (2) proposing MemGen with the trigger-weaver architecture and dynamic token-level integration; (3) comprehensive experiments showing state-of-the-art performance; (4) discovering emergent memory specializations analogous to human memory types.
>   来源：Abstract / Introduction
>
> - **主结果**：On eight benchmarks, MemGen outperforms ExpeL and AWM by up to 38.22% and GRPO by up to 13.44%. It demonstrates strong cross-domain generalization. Emergent analysis reveals spontaneous development of planning, procedural, and working memory without supervision.
>   来源：Abstract / Experiments

> [!note]- 我的批注 / Zotero 批注
> - Zotero item key: 2DJECDW9
> - PDF key: 待核查
> - 批注摘录：待核查：需回填 Zotero 真实批注。

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：agent-memory, latent-memory, llm-agent, self-evolving-agents, generative-memory
> - 候选标签：agent-memory, latent-memory, llm-agent, self-evolving-agents, generative-memory, memory-trigger, memory-weaver, latent-token
> - 当前标签：method, llm-agent, agent-memory, latent-memory, generative-memory, self-evolution, self-evolving-agents
> - 研究关系：拓展了隐式记忆研究，通过在推理中动态生成记忆令牌，弥合参数记忆与检索记忆的鸿沟。

## 6. 元数据（仅保留一份）
| 项目 | 内容 |
| --- | --- |
| Authors | Guibin Zhang, Muxin Fu, Shuicheng Yan |
| Year | 2025 |
| Venue | 待核查：需回查原文。 |
| DOI | 待核查：需回查原文。 |
| Zotero item key | 2DJECDW9 |
| PDF key | 待核查：需回查原文。 |
| Zotero collections | 待核查：需从 Zotero 同步。 |
| Zotero tags | 待核查：需从 Zotero 同步。 |

## 7. 待复核问题
### 高优先级待复核
- DOI / arXiv ID
- 8 个 benchmark 的具体名称
- Backbone / base model
- Memory Trigger 的训练方式与触发判定机制
- Memory Weaver 的结构与 latent token 生成方式
- latent token 如何插入推理流
- 训练策略与优化目标
- 主评测指标定义
- 主结果表与关键数字
- 消融实验与效率成本
- 失败案例与局限原文出处

### 其他待复核问题
- 隐记忆序列的生成如何避免噪声累积，是否影响推理稳定性？
- 在不同规模的LLM上，记忆编织器的迁移性如何？
- 隐记忆的实际可解释性如何，能否可视化或对齐到具体语义？
- 训练过程中如何平衡记忆与推理的联合优化？
