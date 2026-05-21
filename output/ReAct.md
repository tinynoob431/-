---
title: "ReAct: Synergizing Reasoning and Acting in Language Models"
aliases: ["ReAct"]
tags: ["reasoning-acting", "llm-prompting", "interactive-reasoning"]

zotero_item_key: "9VJ5DNEQ"
pdf_key: "HLT7JUCB"
doi: "10.48550/arXiv.2210.03629"
year: "2023"
venue: "ICLR 2023"
authors: ["Shunyu Yao", "Jeffrey Zhao", "Dian Yu", "Nan Du", "Izhak Shafran", "Karthik Narasimhan", "Yuan Cao"]
paper_type: "method"
paper_subtype: "method" # survey/method/system/benchmark/dataset/empirical/theory/application
status: "seed" # seed / skimmed / read / cited

zotero_collections: ["needs-check"]
zotero_tags: ["Computer Science - Artificial Intelligence", "Computer Science - Computation and Language", "Computer Science - Machine Learning"]
canonical_tags: ["react", "reasoning-acting", "prompting"]
candidate_tags: ["llm", "chain-of-thought", "decision-making", "question-answering", "fact-verification", "interactive-agents", "react", "interactive-decision-making"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "ReAct是结合推理与行动的经典工作，启发了后续许多LLM agent研究，具有重要参考价值。"
research_relation: "ReAct将之前分开研究的思维链推理和行动规划统一到一个交织框架中，与仅推理或仅行动的方法相比展现出更优的性能和可解释性。"
---

# ReAct: Synergizing Reasoning and Acting in Language Models

## 0. 先看这里
> [!abstract]
> **一句话定位**：提出ReAct方法，通过交替生成推理轨迹和行动，实现语言模型中推理与行动的协同，以提升多种语言理解和决策任务的性能。
> **论文类型**：method
> **问题**：大型语言模型的推理能力（如思维链）和行动能力（如计划生成）被分开研究，缺乏协同机制，导致推理脱离外部知识、行动缺乏抽象推理支持。
> **方法**：ReAct通过交织推理轨迹和行动步骤来驱使LLM协同运用内部知识和外部反馈解决问题。
> **结果**：HotpotQA/Fever上ReAct优于仅行动模式，与CoT竞争力强，组合CoT+ReAct最佳；ALFWorld绝对成功率提升34%，WebShop提升10%
> **是否纳入核心库**：`candidate`
> **理由**：ReAct是结合推理与行动的经典工作，启发了后续许多LLM agent研究，具有重要参考价值。
> **为什么读**：演示如何通过prompting让LLM同时进行推理和行动，解决思维链的幻觉和错误传播问题，并在问答和交互决策任务上显著提升表现。

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：大型语言模型的推理能力（如思维链）和行动能力（如计划生成）被分开研究，缺乏协同机制，导致推理脱离外部知识、行动缺乏抽象推理支持。
- 核心瓶颈：思维链推理是静态黑箱，无法利用外部信息更新知识；纯行动方法缺乏高层次的推理和记忆来支持动态决策。
- 相比已有方法：思维链(CoT)、仅行动(Act-only)、标准提示、模仿学习、强化学习

**主要贡献：**
1. 提出ReAct范式，将LLM的推理轨迹和任务相关行动交织生成，实现推理与行动的协同。
2. 在问答、事实验证、文本游戏、网页导航四个任务上超越现有基线，展现有效性。
3. 提高模型可解释性和可信度，通过外部交互减轻幻觉和错误传播。
4. 在交互决策任务上仅用一到两个上下文示例即超越经过大量训练的模仿/强化学习方法。

**主要局限：**
推断：需依赖外部环境API，可能受限, 推理轨迹可能引入额外提示长度和成本, 在纯推理任务上可能不如单独CoT, 对LLM基础能力有较高要求

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：将推理和行动交织，使推理指导行动，行动结果反馈优化推理，从而利用外部知识克服内部知识局限
- 关键设计：
  - 推理轨迹生成模块（Thought）
  - 行动生成模块（Act）
  - 环境交互接口（Obs）
- 流程概览：
  1. 任务输入（问题或描述）。
  2. 重复以下步骤直到结束：。
  3. 生成推理轨迹（Thought）。
  4. 生成行动（Act）。
  5. 执行行动并获取观察（Obs）。
  6. 将观察纳入上下文。
  7. 输出最终答案或动作序列。
- 输入 / 数据来源：问题或任务描述（如QA问题、游戏状态）
- 输出 / 评估对象：最终答案（QA）或行动序列（决策）

### 1.3 实验结论
- 数据集 / Benchmark：HotpotQA, Fever, ALFWorld, WebShop
- Baselines：Standard prompting, Chain-of-thought (CoT), Act-only, Imitation learning, Reinforcement learning
- Metrics：EM (Exact Match) and F1 on HotpotQA; accuracy on Fever; success rate on ALFWorld and WebShop
- 主结果：在ALFWorld和WebShop上，ReAct的绝对成功率分别比模仿学习和强化学习方法高出34%和10%。在HotpotQA和Fever上，ReAct与CoT性能相当，而ReAct+CoT组合取得最佳效果。
- 可信度判断：待核查：需回查原文。
- 最关键图/表：Figure 1 (comparison of prompting methods on HotpotQA and ALFWorld)
- 它说明了什么：图1显示，ReAct交错进行推理（思考）和行动（行动）相比CoT（仅推理）或仅行动模式，能产生更准确且可解释的轨迹。
- 效率 / 成本：ReAct requires only 1-2 in-context examples, but no discussion of inference time or compute cost.

### 1.4 我的判断与行动
- 值不值得细读：是
- 对我当前研究的价值：ReAct为LLM智能体提供了简单有效的推理+行动循环框架，可借鉴其prompt模板和交互思路，适用于需要外部知识交互的问答和决策任务。
- 可以借鉴的点：ReAct的prompt模板（思考-行动-观察交替格式）、结合外部知识（如Wikipedia API）的方式、少样本提示策略。
- 暂时不用管的点：具体任务环境（ALFWorld、WebShop）的实现细节，如果与自己研究无关可忽略。

**下一步行动：**
1. 阅读ReAct官方代码库（https://react-lm.github.io/）。
2. 在自己的任务上尝试ReAct风格提示，对比纯CoT和仅行动模式。
3. 探索ReAct与其他智能体框架（如Toolformer、AutoGPT）的结合。

## 2. 关键图表（可选）
![[assets/9VJ5DNEQ/framework_page_02_render.png]]

- 图/表来源：Rendered PDF page 2 as fallback (vector figure likely).
- 图/表类型：framework / architecture / pipeline (待核查)
- 图/表说明：
  - 结构：ReAct（Reasoning+Acting）通过提示LLM交替产出自然语言推理和具体行动，推理辅助规划、跟踪和异常处理，行动从外部获取信息反馈给推理，形成闭环
  - 过程：任务输入（问题或描述）；重复以下步骤直到结束：；生成推理轨迹（Thought）。
  - 意义：图1显示，ReAct交错进行推理（思考）和行动（行动）相比CoT（仅推理）或仅行动模式，能产生更准确且可解释的轨迹。
- 需回查项：否

## 3. 进阶细节（按需展开）
> [!info]- 核心设计细节
> - 训练策略 / 构造流程：少样本提示（上下文学习）
> - 推理流程 / 评估流程：待核查：需回查方法章节。
> - 假设条件：LLM具备基础推理和生成行动能力, 外部环境（如Wikipedia API、模拟环境）可交互并提供观察
> - 关键部分1：推理模块（Thought）：生成思考轨迹，用于规划、跟踪进度、处理异常、决定下一步行动
> - 关键部分2：行动模块（Act）：生成具体动作（如搜索、导航指令），与环境交互获取新信息

> [!info]- 公式与算法细节
> - 关键形式: Thought(思考) -> Action(行动) -> Observation(观察) 循环。
> - 该论文主要是 prompting paradigm，不依赖新的数学公式。
> - 与 baseline 差异: 重点在轨迹组织方式，而非新增训练目标函数。

> [!info]- 实验细节
> - 模型 / Backbone：PaLM-540B
> - 消融实验：待核查：需查看消融实验章节。
> - 失败案例 / 边界：待核查：需回查原文。
> - 数据集证据：HotpotQA, Fever, ALFWorld, WebShop
> - Backbone证据：待核查：需回查原文。
> - Baseline证据：For HotpotQA/Fever: Standard, CoT, Act-only. For ALFWorld/WebShop: imitation and reinforcement learning methods.
> - 指标证据：待核查：需回查原文。
> - 主结果证据：ReAct improves absolute success rate by 34% on ALFWorld and 10% on WebShop; competitive with CoT on QA tasks.
> - 消融证据：待核查：需回查原文。
> - 效率证据：Uses one or two in-context examples.
> - 失败证据：待核查：需回查原文。

> [!info]- 可引用素材（写作时再看）
> - 背景：Vygotsky, 1987 - inner speech and self-regulation, Wei et al; 2022 - chain-of-thought prompting, Ahn et al; 2022 - language models for planning, Yao et al; 2022 - WebShop benchmark, Shridhar et al; 2020b - ALFWorld benchmark, Yang et al; 2018 - HotpotQA, Thorne et al; 2018 - FEVER
> - 背景来源：人类认知理论（Alderson-Day & Fernyhough, 2015; Vygotsky, 1987; Luria, 1965; Fernyhough, 2010; Baddeley, 1992）；LLM推理（Wei et al; 2022）；LLM行动（Ahn et al; 2022; Nakano et al; 2021; Yao et al; 2020; Huang et al; 2022a,b）
> - Gap：缺乏将推理与行动动态协同的通用方法，先前工作分别研究推理或行动，未将二者结合用于通用任务解决。
> - Gap来源："Beyond such simple embodied tasks to interact with a few blocks, there have not been studies on how reasoning and acting can be combined in a synergistic manner for general task solving" (Section 1)
> - 方法比较：与Standard、CoT（Reason Only）、Act-only对比，以及与模仿学习和强化学习方法对比。
> - 方法比较来源：Figure 1展示四种方法对比；Section 3报告与强化学习/模仿学习的比较。
> - 实验证据：在HotpotQA、Fever、ALFWorld、WebShop上实验。ReAct在HotpotQA/Fever上优于Act-only，与CoT竞争，ReAct+CoT最好；在ALFWorld上绝对成功率提升34%，WebShop上提升10%。
> - 实验证据来源："ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively" (Abstract); "The best approach overall is a combination of ReAct and CoT" (Section 3).
> - 局限：推断：ReAct may produce redundant or repetitive thoughts/actions; performance depends on prompt quality; may struggle with tasks requiring long-horizon planning without external feedback.
> - 局限来源：待核查：需回查原文。

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
> - **问题背景**：当前LLM推理（如CoT）是静态黑盒，无法与外部世界交互，导致事实幻觉和错误传播；而行动生成缺乏抽象推理和工作记忆，二者分离
>   来源：Abstract / Introduction
>
> - **核心瓶颈**：推理和行动被独立研究，缺乏协同机制，限制模型动态更新知识和规划能力
>   来源：Abstract / Introduction
>
> - **已有方法对比**：CoT（推理单独）、Act-only（行动单独）、模仿学习、强化学习方法
>   来源：Related Work / Introduction
>
> - **方法组成**：通过提示LLM交替生成推理轨迹（Thought）和行动（Act），行动后接收环境观察（Obs），迭代推进任务
>   来源：Abstract / Method
>
> - **主要贡献**：提出了ReAct通用范式，在四项基准上采用一到两个上下文示例即超越或接近SOTA，并提升可解释性
>   来源：Abstract / Introduction
>
> - **主结果**：HotpotQA/Fever上ReAct+CoT组合最优；ALFWorld成功率绝对提升34%（ReAct vs 模仿学习），WebShop提升10%
>   来源：Abstract / Experiments
>
> - **局限信息**：在推理密集型任务（如GSM8K）可能不如纯CoT；依赖API环境；prompt设计需精心
>   来源：Discussion / Limitation

> [!note]- 我的批注 / Zotero 批注
> - Zotero item key: 9VJ5DNEQ
> - PDF key: HLT7JUCB
> - 批注摘录：待核查：需回填 Zotero 真实批注。

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：react, reasoning-acting, prompting
> - 候选标签：llm, chain-of-thought, decision-making, question-answering, fact-verification, interactive-agents, react, interactive-decision-making
> - 当前标签：reasoning-acting, llm-prompting, interactive-reasoning
> - 研究关系：ReAct将之前分开研究的思维链推理和行动规划统一到一个交织框架中，与仅推理或仅行动的方法相比展现出更优的性能和可解释性。

## 6. 元数据（仅保留一份）
| 项目 | 内容 |
| --- | --- |
| Authors | Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao |
| Year | 2023 |
| Venue | ICLR 2023 |
| DOI | 10.48550/arXiv.2210.03629 |
| Zotero item key | 9VJ5DNEQ |
| PDF key | HLT7JUCB |
| Zotero collections | 待核查：需从 Zotero 同步。 |
| Zotero tags | Computer Science - Artificial Intelligence, Computer Science - Computation and Language, Computer Science - Machine Learning |

## 7. 待复核问题
### 高优先级待复核
- 消融实验与效率成本
- 失败案例与局限原文出处

### 其他待复核问题
- 如何优化推理与行动的平衡，避免过长的轨迹？
- ReAct在更复杂、开放领域任务中的扩展性如何？
- 如何减少对LLM内部知识的依赖，提高事实准确性？
