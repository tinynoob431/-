---
title: "MemGen: Weaving Generative Latent Memory for Self-Evolving Agents"
aliases: ["MemGen"]
tags: ["latent-memory", "generative-memory", "agent-memory", "llm-agent", "self-evolving"]

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
canonical_tags: ["latent-memory", "generative-memory", "agent-memory", "llm-agent"]
candidate_tags: ["memory-trigger", "memory-weaver", "self-evolving", "latent-computation", "reinforcement-learning", "cognitive-architecture", "latent-token", "self-evolution"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "该论文提出了一种新颖的生成式潜在记忆方法，实验表现显著优于现有方法，且展示了自发记忆分化的有趣现象，对智能体记忆研究有较大启发。"
research_relation: "本文聚焦于 LLM 智能体的记忆机制，提出潜在记忆范式，与参数记忆和检索记忆形成对比。"
---

# MemGen: Weaving Generative Latent Memory for Self-Evolving Agents

## 0. 先看这里
> [!abstract]
> **一句话定位**：MemGen 提出一种动态生成式潜在记忆框架，通过记忆触发器与记忆编织器实现推理与记忆的紧密交织，使 LLM 智能体自发演化出类似人类的规划、程序和工作记忆能力。
> **论文类型**：method
> **问题**：现有参数记忆面临灾难性遗忘，检索记忆难以实现记忆与推理的深度融合，缺乏类似人类的认知记忆交织。
> **方法**：MemGen是一个动态生成式记忆框架，通过记忆触发器和记忆编织器在LLM智能体推理过程中动态生成潜在token序列作为记忆，实现推理与记忆的紧密交织。
> **结果**：在8个基准上，MemGen超越ExpeL和AWM最高38.22%，超越GRPO最高13.44%，并展现出强跨域泛化能力。
> **是否纳入核心库**：`candidate`
> **理由**：该论文提出了一种新颖的生成式潜在记忆方法，实验表现显著优于现有方法，且展示了自发记忆分化的有趣现象，对智能体记忆研究有较大启发。
> **为什么读**：了解如何通过潜在记忆实现推理与记忆的动态交织，以及智能体无需显式监督即可分化出多种人类样记忆。

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：现有参数记忆面临灾难性遗忘，检索记忆难以实现记忆与推理的深度融合，缺乏类似人类的认知记忆交织。
- 核心瓶颈：生成式潜在记忆的训练与推理效率，以及如何确保记忆触发的时机和内容对智能体有帮助。
- 相比已有方法：ExpeL, AWM, GRPO, FireAct, AgentLumos, Coconut, SoftCoT, LaRS, LatentSeek 等。

**主要贡献：**
1. 提出MemGen框架，包含记忆触发器和记忆编织器，实现推理与记忆的动态交织。
2. 在8个基准测试上超越现有外部记忆系统（ExpeL、AWM）最高38.22%，超越GRPO最高13.44%。
3. 无需显式监督，自发演化出规划记忆、程序记忆和工作记忆等类人记忆能力。

**主要局限：**
推断：未明确讨论，但可推测latent memory的计算开销和可解释性有待研究，且依赖LLM架构。

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：通过记忆触发器和记忆编织器，在推理过程中动态生成潜在记忆token并插入，实现记忆与推理的紧密交织，模拟人类认知过程。
- 关键设计：
  - 记忆触发器（memory trigger）、记忆编织器（memory weaver）
- 流程概览：
  1. 接收当前智能体状态（任务查询、历史、环境观测等）。
  2. 记忆触发器监控推理状态，决策是否调用记忆。
  3. 若触发，记忆编织器生成潜在记忆token序列。
  4. 将记忆token插入当前推理序列。
  5. 智能体继续推理并输出动作。
- 输入 / 数据来源：当前智能体状态（包括任务查询、历史轨迹、环境观测等）。
- 输出 / 评估对象：动作序列（如工具调用、API请求、最终答案）。

### 1.3 实验结论
- 数据集 / Benchmark：待核查：摘要未完整给出数据集细节，需查看实验部分。
- Baselines：ExpeL, AWM, GRPO
- Metrics：待核查：当前摘录未完整说明指标定义，需查看实验设置部分。
- 主结果：待核查：需回查原文。
- 可信度判断：需要查看实验部分确认结果可靠性，摘要显示显著提升
- 最关键图/表：待核查：需回查原文。
- 它说明了什么：图2展示MemGen架构，包括Memory Trigger和Memory Weaver模块，以及latent memory tokens的生成与插入，体现推理与记忆的交织。
- 效率 / 成本：待核查：需查看效率与成本对比。

### 1.4 我的判断与行动
- 值不值得细读：是
- 对我当前研究的价值：如果研究LLM智能体记忆或自我进化机制，MemGen的触发-编织架构和潜在记忆序列设计有直接参考价值。
- 可以借鉴的点：记忆触发器和编织器的设计理念、潜在记忆插入策略、以及实验评估框架的构建。
- 暂时不用管的点：部分特定基线实现细节（如ExpeL、AWM）若与当前研究无关可跳过。

**下一步行动：**
1. 详细阅读方法部分（第4节），理解触发器和编织器的具体实现。
2. 查看开源代码（GitHub链接），尝试复现关键实验。
3. 评估该框架与自身研究问题的契合度，考虑是否借鉴架构。

## 2. 关键图表（可选）
![[assets/2DJECDW9/framework_p08_n044.png]]

- 图/表来源：Auto extracted from PDF page 8 image 44
- 图/表类型：framework / architecture / pipeline (待核查)
- 图/表说明：
  - 结构：MemGen通过一个触发器在推理过程中动态决定何时插入潜在记忆，并由编织器生成记忆，实现记忆与推理的紧密交织。
  - 过程：接收当前智能体状态（任务查询、历史、环境观测等）；记忆触发器监控推理状态，决策是否调用记忆；若触发，记忆编织器生成潜在记忆token序列。
  - 意义：图2展示MemGen架构，包括Memory Trigger和Memory Weaver模块，以及latent memory tokens的生成与插入，体现推理与记忆的交织。
- 需回查项：否

## 3. 进阶细节（按需展开）
> [!info]- 核心设计细节
> - 训练策略 / 构造流程：待核查：需回查方法与训练章节。
> - 推理流程 / 评估流程：Memory Trigger 监控 agent 推理状态，Memory Weaver 根据当前状态构造潜在 token 序列作为记忆，将潜在记忆 token 插入到当前推理 token 序列中，agent 继续生成并执行动作，环境反馈更新状态和记忆
> - 假设条件：基础LLM具备足够推理能力；潜在记忆token能有效编码经验知识。
> - 关键部分1：Memory Trigger - 监控代理推理状态并决策显式记忆调用的模块。
> - 关键部分2：Memory Weaver - 以当前状态为刺激生成潜在token序列作为记忆的模块。

> [!info]- 公式与算法细节
> $$
> z_{t,j} \sim \pi_\theta(\cdot | s_t, z_{t,<j})
> $$
>
> $$
> \max_{\theta, M} \mathbb{E}_{x \sim D, \tau \sim \pi_{\theta,M}}[R(\tau)]
> $$
>
> $$
> m_t = f_M(s_t, H, m_{<t})
> $$
>
> - 符号说明:
>   - s_t:当前状态, z_t,j:第j个潜在记忆token, π_θ:策略, τ:轨迹, R(τ):奖励, H:历史经验, m_t:记忆, f_M:记忆生成函数
> - 公式作用:
>   - 公式(1)定义潜在记忆token的生成过程; 公式(2)形式化优化目标; 公式(3)定义记忆生成函数
> - 与 baseline 差异: 与参记忆（直接调参）和检索记忆（外部数据库）不同，MemGen 通过动态潜在记忆内插实现推理与记忆的紧密交织

> [!info]- 实验细节
> - 模型 / Backbone：待核查：当前摘录未明确骨干模型，需查看 setup 或 appendix。
> - 消融实验：待核查：需查看消融实验章节。
> - 失败案例 / 边界：待核查：需回查原文。
> - 数据集证据：待核查：需回查原文。
> - Backbone证据：待核查：需回查原文。
> - Baseline证据：ExpeL, AWM, GRPO
> - 指标证据：待核查：需回查原文。
> - 主结果证据：待核查：需回查原文。
> - 消融证据：待核查：需回查原文。
> - 效率证据：待核查：需回查原文。
> - 失败证据：待核查：需回查原文。

> [!info]- 可引用素材（写作时再看）
> - 背景：现有LLM智能体的记忆机制主要分为参数化记忆（通过微调内化经验，但存在灾难性遗忘）和检索式记忆（将经验外部化为结构化数据库，但集成不自然）。
> - 背景来源：引言及第1节，引用论文相关段落。
> - Gap：现有方法缺乏推理与记忆的紧密交织，且大多基于检索而非生成，无法像人类认知那样动态融合。
> - Gap来源：引言及第1节，直接指出现有方法的两大缺陷。
> - 方法比较：MemGen在8个基准上超越ExpeL和AWM达38.22%，超越GRPO达13.44%，并展现强跨域泛化能力。
> - 方法比较来源：摘要及实验部分（第5节）。
> - 实验证据：在8个基准（如PopQA, TriviaQA等）上评估，比较对象包括ExpeL、AWM、GRPO等，结果显示MemGen显著领先且自发演化出规划、程序性和工作记忆等类人记忆能力。
> - 实验证据来源：摘要及第5节。
> - 局限：待核查：需回查原文。
> - 局限来源：待核查：需回查原文。

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
> - **问题背景**：现有参数记忆和检索记忆范式未能实现推理与记忆的动态交织，缺乏类人认知的流畅融合。
>   来源：Abstract / Introduction
>
> - **核心瓶颈**：记忆与推理的静态分离，无法实现动态交织。
>   来源：Abstract / Introduction
>
> - **已有方法对比**：ExpeL, AWM, GRPO, FireAct, AgentLumos, Coconut, CODI, LaRS, LatentSeek, SoftCoT等。
>   来源：Related Work / Introduction
>
> - **方法组成**：MemGen由记忆触发器和记忆编织器组成；触发器监控推理状态决定何时调用记忆，编织器根据当前状态生成潜在token序列作为记忆。
>   来源：Abstract / Method
>
> - **主要贡献**：（1）提出动态生成记忆框架MemGen；（2）在8个基准上超越现有方法；（3）自发演化出规划、程序和工作记忆能力；（4）展示强跨域泛化能力。
>   来源：Abstract / Introduction
>
> - **主结果**：在8个基准上，MemGen超越ExpeL和AWM最高38.22%，超越GRPO最高13.44%，并展现出强跨域泛化。
>   来源：Abstract / Experiments

> [!note]- 我的批注 / Zotero 批注
> - Zotero item key: 2DJECDW9
> - PDF key: 待核查
> - 批注摘录：待核查：需回填 Zotero 真实批注。

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：latent-memory, generative-memory, agent-memory, llm-agent
> - 候选标签：memory-trigger, memory-weaver, self-evolving, latent-computation, reinforcement-learning, cognitive-architecture, latent-token, self-evolution
> - 当前标签：latent-memory, generative-memory, agent-memory, llm-agent, self-evolving
> - 研究关系：本文聚焦于 LLM 智能体的记忆机制，提出潜在记忆范式，与参数记忆和检索记忆形成对比。

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
- 数据集 / benchmark 列表
- Backbone / base model
- 训练策略与优化目标
- 主评测指标定义
- 主结果表与关键数字
- 关键图表路径与图注
- 消融实验与效率成本
- 失败案例与局限原文出处

### 其他待复核问题
- 触发器的决策机制如何学习？是否依赖启发式规则？
- 潜在记忆序列的可解释性如何？能否可视化其语义？
- 该方法在更复杂、非结构化环境中的泛化能力如何？
- 计算开销与现有检索式记忆相比如何？
