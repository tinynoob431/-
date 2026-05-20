---
title: "ReAct: Synergizing Reasoning and Acting in Language Models"
aliases: ["ReAct"]
tags: ["method", "llm-agent", "prompting", "tool-use", "reasoning-acting"]

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
canonical_tags: ["llm-agent", "prompting", "tool-use", "reasoning-acting"]
candidate_tags: ["prompting", "tool-use", "reasoning-acting", "react", "chain-of-thought", "interactive-decision-making", "knowledge-intensive-qa", "reinforcement-learning"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "提出ReAct方法，将推理与行动结合，在问答和决策任务上取得显著提升，是提示工程领域的经典工作。"
research_relation: "提出一种将推理与行动交错提示语言模型的方法，实现协同增效。"
---

# ReAct: Synergizing Reasoning and Acting in Language Models

## 0. 先看这里
> [!abstract]
> **一句话定位**：提出ReAct范式，将推理与行动交错生成，使语言模型在问答与决策任务中结合思维链和外部信息交互，减少幻觉并提升可解释性。
> **论文类型**：method
> **问题**：现有语言模型推理（如思维链）与行动（如动作生成）缺乏协同，推理不接地气，容易产生幻觉。
> **方法**：ReAct通过交错生成推理步骤和动作，使LLM能够动态推理并与外部环境交互，从而解决复杂任务。
> **结果**：在 ALFWorld 和 WebShop 上，ReAct 的成功率分别较模仿学习与强化学习方法绝对提升 34% 和 10%；在 HotpotQA 和 Fever 上，通过 Wikipedia API 交互，克服了 CoT 的幻觉与错误传播问题。
> **是否纳入核心库**：`candidate`
> **理由**：提出ReAct方法，将推理与行动结合，在问答和决策任务上取得显著提升，是提示工程领域的经典工作。
> **为什么读**：了解如何通过交错生成推理和动作来增强LLM的推理能力和可解释性，对构建智能体有借鉴意义。

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：现有语言模型推理（如思维链）与行动（如动作生成）缺乏协同，推理不接地气，容易产生幻觉。
- 核心瓶颈：推理与行动分离，推理是静态黑箱，无法从外部世界更新信息；行动方法缺乏高层推理和记忆。
- 相比已有方法：思维链提示（CoT）、动作生成（动作计划生成）、模仿学习和强化学习等方法。

**主要贡献：**
1. 提出 ReAct 范式，将推理（Thought（思考））与行动（Action（行动））交错生成于 LLM 中，实现二者的协同。
2. 在知识推理（HotpotQA、Fever）和交互决策（ALFWorld、WebShop）任务上验证了 ReAct 的有效性，并展现了其可解释性。
3. 揭示了结合外部信息获取（act）与内部推理（reason）的互补优势，ReAct+CoT 组合达到最佳效果。

**主要局限：**
推断：单独 ReAct 在部分知识密集型任务上可能不如结合内部知识的 CoT；需要精心设计少量示例；动作空间受限于预定义 API。

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：ReAct提出在语言模型中交替生成推理轨迹（Thought（思考））和与任务相关的动作（Action（行动）），实现“推理指导行动”与“行动辅助推理”的协同：推理帮助规划、跟踪、调整高层行动策略并处理异常，行动通过外部环境（如Wikipedia API、交互式环境）获取额外信息支撑推理。
- 关键设计：
  - 基于提示的 Thought（思考）-Action（行动） 交错生成模块
  - 外部环境交互与观察(Obs)集成模块。
- 流程概览：
  1. 输入问题或环境观察。
  2. LLM 生成 Thought（推理痕迹）。
  3. 基于 Thought（思考） 生成 Action（如 Search、Click 等）。
  4. 执行 Action（行动），从环境获取 Observation（观察）。
  5. 循环以上步骤，直至生成最终答案或任务完成。
- 输入 / 数据来源：自然语言形式的问题描述或环境状态文本。
- 输出 / 评估对象：自然语言答案或任务完成状态。

### 1.3 实验结论
- 数据集 / Benchmark：HotpotQA, Fever, ALFWorld, WebShop
- Baselines：Standard, CoT, Act-only, imitation learning方法, reinforcement learning方法
- Metrics：待核查：当前摘录未完整说明指标定义，需查看实验设置部分。
- 主结果：在HotpotQA和Fever上，ReAct克服了CoT中的幻觉和错误传播问题，与纯动作生成方法相比更优，与CoT竞争；最佳方案是ReAct与CoT结合。在ALFWorld和WebShop上，ReAct分别以34%和10%的绝对成功率提升超越模仿学习和强化学习方法。
- 可信度判断：中等：seed 阶段需回查指标定义、方差/显著性与完整实验设置后再提高可信度等级。
- 最关键图/表：Figure 1
- 它说明了什么：Figure 1对比了Standard、CoT、Act-only和ReAct四种提示方法在HotpotQA和ALFWorld上的推理-行动轨迹。ReAct通过交替推理与行动，能够在发现错误时调整策略（如搜索正确信息），而CoT仅依赖内部知识时可能产生幻觉且无法恢复。
- 效率 / 成本：待核查：需查看效率与成本对比。

### 1.4 我的判断与行动
- 值不值得细读：是
- 对我当前研究的价值：直接相关：为语言模型中的推理与行动协同提供通用范式，可应用于构建能调用工具的智能体。
- 可以借鉴的点：交替生成思维-动作的提示模板、HotpotQA/Fever基准上的Wikipedia API交互设定、少样本示例设计思路；官方代码库（https://react-lm.github.io）。
- 暂时不用管的点：简单的Wikipedia API交互细节如改用其他工具可以忽略，但思想保留。

**下一步行动：**
1. 克隆官方仓库，在自定义任务上测试ReAct提示。
2. 精读错误分析部分，了解失败模式。
3. 探索将ReAct与搜索、代码执行等其他工具结合。

## 2. 关键图表（可选）
![[assets/9VJ5DNEQ/framework_page_05_render.png]]

- 图/表来源：Auto resolved from assets folder.
- 图/表类型：figure / table / framework (待核查)
- 图/表说明：
  - 结构：Figure 1 对比了 Standard、CoT、Act-only 和 ReAct 四种提示方式。
  - 过程：ReAct 在同一轨迹中交替生成 Thought（思考）、Action（行动），并接收 Observation（观察）反馈。
  - 意义：展示了推理与行动协同如何减少幻觉、增强规划能力并提升可解释性。
- 需回查项：已使用页面渲染兜底，建议人工确认是否为关键图表。

## 3. 进阶细节（按需展开）
> [!info]- 核心设计细节
> - 训练策略 / 构造流程：无需额外训练，仅通过少量示例（1-2个上下文示例）进行提示（few-shot prompting）。
> - 推理流程 / 评估流程：给定输入，模型交替生成Thought（推理文本）和Action（可执行动作），环境返回Observation（观察），循环直至生成最终答案。
> - 假设条件：LLM 具备通过提示生成合理推理和动作的能力；外部环境（如 Wikipedia API）可交互且返回文本观察。
> - 关键部分1：推理模块（Reasoning）：生成 Thought（思考），负责规划、追踪进度、处理异常。
> - 关键部分2：行动模块（Acting）：生成 Action（行动） 并与外部环境交互，获取 Observation（观察）。

> [!info]- 公式与算法细节
> - 关键形式：Thought（思考）→ Action（行动）→ Observation（观察）循环。
> - 该论文主要是 prompting paradigm，不依赖新的数学公式。
> - 与 baseline 差异：重点在轨迹组织方式，而非新增训练目标函数。

> [!info]- 实验细节
> - 模型 / Backbone：待核查：当前摘录未明确骨干模型，需查看 setup 或 appendix。
> - 消融实验：摘要指出ReAct与CoT的组合整体效果最佳；其他消融（如上下文示例数量、推理与行动分离）需查看完整实验。
> - 失败案例 / 边界：ReAct通过与环境交互，有效缓解了CoT推理中常见的事实幻觉和错误传播问题，在轨迹中展示了模型如何根据观察调整后续推理和动作。
> - 数据集证据：摘要原文："on question answering (HotpotQA) and fact verification (Fever)... on two interactive decision making benchmarks (ALFWorld and WebShop)"
> - Backbone证据：待核查：需回查原文。
> - Baseline证据：图1说明："Comparison of 4 prompting methods, (a) Standard, (b) Chain-of-Thought（思考） (CoT, Reason Only), (c) Act-only, and (d) ReAct (Reason+Act)"；摘要："ReAct outperforms imitation and reinforcement learning methods"
> - 指标证据：待核查：需回查原文。
> - 主结果证据：摘要："on question answering (HotpotQA) and fact verification (Fever), ReAct overcomes prevalent issues of hallucination and error propagation... Furthermore, on two interactive decision making benchmarks (ALFWorld and WebShop), ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively."
> - 消融证据：摘要："The best approach overall is a combination of ReAct and CoT..."
> - 效率证据：待核查：需回查原文。
> - 失败证据：待核查：需回查原文。

> [!info]- 可引用素材（写作时再看）
> - 背景：Prior work has explored LLMs for reasoning (e.g; chain-of-Thought（思考） prompting) and acting (e.g; Action（行动） plan generation) separately, but CoT is a static black box prone to hallucination and error propagation, while Action（行动）-only models lack high-level reasoning and working memory.
> - 背景来源：Introduction, paragraphs 2-3
> - Gap：There have not been studies on how reasoning and acting can be combined in a synergistic manner for general task solving, and if such a combination can bring systematic benefits compared to reasoning or acting alone.
> - Gap来源：Introduction, last paragraph
> - 方法比较：On interactive decision making benchmarks (ALFWorld and WebShop), ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively. On QA and fact verification, ReAct overcomes hallucination and error propagation in chain-of-Thought（思考） reasoning by interacting with a Wikipedia API, and the best approach combines ReAct and CoT.
> - 方法比较来源：Abstract
> - 实验证据：Evaluated on four diverse benchmarks: question answering (HotpotQA), fact verification (Fever), text-based game (ALFWorld), and webpage navigation (WebShop). ReAct + CoT achieves best results on QA/Fever; ReAct alone surpasses RL methods on ALFWorld and WebShop by large margins.
> - 实验证据来源：Abstract
> - 局限：推断：ReAct 依赖外部环境交互（如 Wikipedia API），当外部知识源不可用或信息不足时，推理和决策能力受限。
> - 局限来源：待核查：需回查原文。

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
> - **问题背景**：现有 LLM 的推理（如 Chain-of-Thought（思考））与行动（如动作规划）被孤立研究，推理不能交互获取外部信息，导致事实幻觉与错误传播，行动则缺少高层抽象推理。
>   来源：Abstract / Introduction
>
> - **核心瓶颈**：Chain-of-Thought（思考） 推理是静态的，模型仅使用内部表征，无法基于外部世界动态更新知识。
>   来源：Abstract / Introduction
>
> - **已有方法对比**：Chain-of-Thought（思考） (CoT) 仅推理，Act-only 仅行动，以及模仿学习、强化学习方法（如 Ahn et al; 2022; Nakano et al; 2021）。
>   来源：Related Work / Introduction
>
> - **方法组成**：ReAct 提示 LLM 交错生成 Thought（推理痕迹）和 Action（可执行动作），通过环境返回 Observation（观察） 实现推理与行动的协同。
>   来源：Abstract / Method
>
> - **主要贡献**：提出 ReAct 范式，验证其在多种任务上的有效性；首次系统展示交错推理与行动能同时提升性能与可解释性。
>   来源：Abstract / Introduction
>
> - **主结果**：在 ALFWorld 上 ReAct 成功率比模仿/强化学习高 34%；在 WebShop 上高 10%；在 HotpotQA 和 Fever 上优于 Act-only，与 CoT 竞争，ReAct+CoT 最佳。
>   来源：Abstract / Experiments

> [!note]- 我的批注 / Zotero 批注
> - Zotero item key: 9VJ5DNEQ
> - PDF key: HLT7JUCB
> - 批注摘录：待核查：需回填 Zotero 真实批注。

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：llm-agent, prompting, tool-use, reasoning-acting
> - 候选标签：prompting, tool-use, reasoning-acting, react, chain-of-thought, interactive-decision-making, knowledge-intensive-qa, reinforcement-learning
> - 当前标签：method, llm-agent, prompting, tool-use, reasoning-acting
> - 研究关系：提出一种将推理与行动交错提示语言模型的方法，实现协同增效。

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
- DOI / arXiv ID
- Backbone / base model
- 主评测指标定义
- 主结果表与关键数字
- 关键图表路径与图注
- 消融实验与效率成本
- 失败案例与局限原文出处
- ReAct+CoT（或同类组合策略）的具体设置

### 其他待复核问题
- ReAct在需要大量工具调用的复杂多步任务上如何扩展？
- 在提示中推理与动作的最佳平衡点如何确定？
- 能否结合微调进一步提高效率或减少幻觉？
- 处理模糊或冲突信息时的鲁棒性如何？
