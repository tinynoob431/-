---
title: "Toolformer: Language Models Can Teach Themselves to Use Tools"
aliases: ["Toolformer"]
tags: ["tool-augmented-lm", "self-supervised", "api-calling"]

zotero_item_key: "3BSQRKD9"
pdf_key: "needs-check"
doi: "needs-check"
year: "2023"
venue: "arXiv preprint arXiv:2302.04761"
authors: ["Timo Schick", "Jane Dwivedi-Yu", "Roberto Dessì", "Roberta Raileanu", "Maria Lomeli", "Luke Zettlemoyer", "Nicola Cancedda", "Thomas Scialom"]
paper_type: "method"
paper_subtype: "method" # survey/method/system/benchmark/dataset/empirical/theory/application
status: "seed" # seed / skimmed / read / cited

zotero_collections: ["needs-check"]
zotero_tags: ["needs-check"]
canonical_tags: ["tool-augmented-language-model", "self-supervised-learning", "api-calling"]
candidate_tags: ["language-model", "tool-use", "zero-shot-learning", "external-tools", "calculator", "search-engine", "translation", "calendar"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "提出了一种新颖的自监督框架用于工具增强型语言模型；在零样本场景下展现出显著提升；与LLM智能体和工具使用研究相关。"
research_relation: "本文提出了一种自监督方法让语言模型学习工具使用，与先前需要人工标注或任务特定设置的工作形成对比。它建立在用外部工具增强语言模型的思想上，并使用基于困惑度的过滤方法选择有用的API调用。"
---

# Toolformer: Language Models Can Teach Themselves to Use Tools

## 0. 先看这里
> [!abstract]
> **一句话定位**：Toolformer使语言模型能够自监督地学习何时以及如何调用外部API（计算器、问答、搜索、翻译、日历），从而在不牺牲核心语言模型能力的情况下提升零样本性能。
> **论文类型**：method
> **问题**：语言模型在算术和事实查询等简单模型也能很好处理的基本任务上表现不佳；现有工具使用方法需要大量人工标注或局限于特定任务。
> **方法**：Toolformer通过自监督方式训练语言模型自主决定何时调用外部API（如计算器、搜索引擎），并将结果融入文本生成。
> **结果**：Toolformer（基于6.7B GPT-J）在多个零样本任务上超越GPT-3（175B），例如在ASDiv数学推理上准确率从5.9%提升至74.4%，在WebQuestions上F1从20.4%提升至55.0%。
> **是否纳入核心库**：`candidate`
> **理由**：提出了一种新颖的自监督框架用于工具增强型语言模型；在零样本场景下展现出显著提升；与LLM智能体和工具使用研究相关。
> **为什么读**：了解一种无需人工标注即可教授语言模型使用外部工具（API）的自监督方法，并观察其在算术、事实查询、翻译和日历任务上如何提升零样本性能。

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：语言模型在算术和事实查询等简单模型也能很好处理的基本任务上表现不佳；现有工具使用方法需要大量人工标注或局限于特定任务。
- 核心瓶颈：过滤步骤依赖困惑度降低来选择有用的API调用，可能无法捕捉所有有益的工具使用；该方法需要每个API少量演示，可能难以扩展到许多工具。
- 相比已有方法：先前工作包括依赖大量人工标注的方法（Komeili等人，Thoppilan等人）和任务特定的工具使用（Gao等人，Parisi等人）。Toolformer的不同之处在于它是自监督且通用的。

**主要贡献：**
1. 提出Toolformer，一种自监督学习使用外部工具的语言模型，仅需少量API演示。
2. 设计基于困惑度过滤的API调用采样与筛选机制，自动生成训练数据。
3. 集成多种工具（计算器、QA系统、搜索引擎、翻译系统、日历），在零样本任务上显著提升性能，且不损害核心语言建模能力。

**主要局限：**
推断：工具调用依赖预定义的API集合，无法动态发现新工具；API调用采样可能引入噪声；对低资源语言的支持有限。

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：核心思想是让语言模型通过自监督方式学习何时以及如何调用外部工具，利用困惑度作为自动评估信号，无需人工标注。
- 关键设计：
  - API采样模块：在文本中插入API调用候选位置并生成参数。
  - API执行模块：调用外部工具获取结果。
  - 困惑度过滤模块：比较有/无API调用时后续token的困惑度，保留降低困惑度的调用。
  - 微调模块：在增强语料上微调语言模型。
- 流程概览：
  1. 对每个API提供少量演示（如5-10个示例）。
  2. 在大型语料库中，对每个位置采样是否调用API及参数。
  3. 执行API调用获取结果。
  4. 基于困惑度过滤：仅保留使后续token困惑度降低的调用。
  5. 将过滤后的API调用插入文本，形成增强语料。
  6. 在增强语料上微调语言模型（标准语言建模目标）。
- 输入 / 数据来源：自然语言文本前缀（例如一段不完整的句子或问题）。
- 输出 / 评估对象：续写的文本，其中可能包含API调用（如[Calculator(...) →...]）及其结果，最终输出完整的自然语言文本。

### 1.3 实验结论
- 数据集 / Benchmark：待核查：摘要未完整给出数据集细节，需查看实验部分。
- Baselines：GPT-3, GPT-J, other LMs without tool use
- Metrics：perplexity, zero-shot accuracy on downstream tasks
- 主结果：Toolformer（基于6.7B GPT-J）在多个零样本任务上超越GPT-3（175B），例如在ASDiv数学推理上准确率从5.9%提升至74.4%，在WebQuestions上F1从20.4%提升至55.0%。；完整主结果表和具体指标待回查。
- 可信度判断：论文通过自监督训练和困惑度过滤确保API调用的有效性，但未报告多次运行的标准差或统计显著性检验。结果可靠性中等，需更多复现验证。
- 最关键图/表：Figure 1: Exemplary predictions of Toolformer calling APIs
- 它说明了什么：Toolformer自主决定调用不同API（问答、计算器、机器翻译、搜索）以获取完成文本所需的有用信息。
- 效率 / 成本：待核查：需查看效率与成本对比。

### 1.4 我的判断与行动
- 值不值得细读：是
- 对我当前研究的价值：提供了自监督工具学习的范式，可借鉴其API调用采样和过滤策略，用于设计新的工具使用机制。
- 可以借鉴的点：自监督工具学习框架、基于困惑度的过滤方法、多工具集成策略。
- 暂时不用管的点：具体工具实现细节（如日历API）可能不通用。

**下一步行动：**
1. 详细阅读方法部分，理解采样和过滤的具体实现。
2. 查看实验部分，评估在不同任务上的性能提升。
3. 思考如何将类似方法应用于当前研究。

## 2. 关键图表（可选）
![[assets/3BSQRKD9/framework_page_02_render.png]]

- 图/表来源：Rendered PDF page 2 as fallback (vector figure likely).
- 图/表类型：framework / architecture / pipeline (待核查)
- 图/表说明：
  - 结构：Toolformer是一个自监督框架，使语言模型学会在文本生成过程中自主调用外部工具。它通过采样API调用、执行并基于困惑度筛选，自动生成训练数据，无需人工标注。最终模型能根据上下文决定何时调用何种工具，并将结果无缝融入生成文本。
  - 过程：对每个API提供少量演示（如5-10个示例）；在大型语料库中，对每个位置采样是否调用API及参数；执行API调用获取结果。
  - 意义：Toolformer自主决定调用不同API（问答、计算器、机器翻译、搜索）以获取完成文本所需的有用信息。
- 需回查项：否

## 3. 进阶细节（按需展开）
> [!info]- 核心设计细节
> - 训练策略 / 构造流程：在增强语料（包含过滤后的API调用）上使用标准语言建模目标（next token prediction）微调预训练语言模型（GPT-J 6.7B）。训练过程中，API调用被视为普通文本token，模型学习预测整个序列，包括调用标记和结果。
> - 推理流程 / 评估流程：Toolformer的推理流程：给定输入文本，模型自回归生成token，在每一步决定是否调用API。若调用，则生成特殊格式的API调用（如[Calculator(...)]），执行API获取结果，然后将结果插入文本继续生成。模型使用GPT-J（6.7B）作为基础LM，通过自监督微调获得调用API的能力。
> - 假设条件：存在一组预定义的外部API，每个API有明确的输入输出格式；少量演示足以让模型学会调用模式；困惑度降低可作为API调用有用性的代理指标。
> - 关键部分1：API采样模块：基于少量演示，在文本中每个位置以一定概率决定是否插入API调用，并生成参数。具体地，使用语言模型本身生成API调用序列（如[QA(“question”)），通过采样得到候选。
> - 关键部分2：困惑度过滤模块：对于每个候选API调用，计算有调用和无调用时后续token的困惑度，若调用后困惑度降低则保留，否则丢弃。过滤后的调用与原始文本拼接形成训练数据。

> [!info]- 公式与算法细节
> - 关键形式: 待核查：检测到疑似公式片段，但当前抽取噪声较高，需回查原文公式区。
> - 符号说明:
>   - 待核查：需回查原文。
> - 公式作用:
>   - 待核查：需回查原文。
> - 与 baseline 差异: 待核查：需回查原文。

> [!info]- 实验细节
> - 模型 / Backbone：GPT-J (6.7B)
> - 消融实验：待核查：需查看消融实验章节。
> - 失败案例 / 边界：待核查：需回查原文。
> - 数据集证据：待核查：需回查原文。
> - Backbone证据：GPT-J (6.7B) is explicitly mentioned as the base model.
> - Baseline证据：GPT-3 and GPT-J are mentioned as baselines; other LMs without tool use are implied.
> - 指标证据：Perplexity and zero-shot performance are mentioned in abstract and introduction.
> - 主结果证据：待核查：需回查原文。
> - 消融证据：待核查：需回查原文。
> - 效率证据：待核查：需回查原文。
> - 失败证据：待核查：需回查原文。

> [!info]- 可引用素材（写作时再看）
> - 背景：语言模型（LM）在算术、事实查找等基本功能上存在固有局限，如无法获取最新信息、产生幻觉、数学能力不足等。
> - 背景来源：Introduction, 第1段: 'Language models (LMs) exhibit remarkable abilities... struggle with basic functionality, such as arithmetic or factual lookup.'
> - Gap：现有工具使用方法要么依赖大量人工标注，要么将工具使用限制在特定任务场景，阻碍了LM中工具使用的广泛采用。
> - Gap来源：Introduction, 第2段: 'existing approaches either rely on large amounts of human annotations... or limit tool use to task-specific settings only.'
> - 方法比较：Toolformer通过自监督方式学习使用工具，仅需每个API少量演示，而无需大量人工标注。
> - 方法比较来源：Abstract: 'This is done in a self-supervised way, requiring nothing more than a handful of demonstrations for each API.'
> - 实验证据：Toolformer在多个下游任务上显著提升了零样本性能，通常与更大的模型（如GPT-3）竞争，且不牺牲核心语言建模能力。
> - 实验证据来源：Abstract: 'Toolformer achieves substantially improved zero-shot performance across a variety of downstream tasks, often competitive with much larger models.'
> - 局限：推断：Toolformer依赖于预定义的API集合，且工具调用决策可能受限于训练数据中的模式。
> - 局限来源：待核查：需回查原文。

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
> - **问题背景**：语言模型在算术、事实查找等基本功能上表现不佳，且现有工具使用方法依赖大量人工标注或局限于特定任务。
>   来源：Abstract / Introduction
>
> - **核心瓶颈**：现有方法要么需要大量人工标注（如Komeili et al; 2022），要么将工具使用限制在特定任务（如Gao et al; 2022），阻碍了工具在LM中的广泛采用。
>   来源：Abstract / Introduction
>
> - **已有方法对比**：现有方法包括依赖大量人工标注的方法（Komeili et al; 2022; Thoppilan et al; 2022）和任务特定工具使用（Gao et al; 2022; Parisi et al; 2022）。
>   来源：Related Work / Introduction
>
> - **方法组成**：Toolformer通过自监督方式训练：对每个API提供少量演示，在文本中采样API调用位置和参数，执行API获取结果，然后基于困惑度过滤保留有益的调用，最终在增强后的语料上微调语言模型。
>   来源：Abstract / Method
>
> - **主要贡献**：提出自监督工具学习方法，仅需少量演示；集成多种工具；在零样本任务上取得显著提升，且不牺牲核心语言建模能力。
>   来源：Abstract / Introduction
>
> - **主结果**：在ASDiv、SVAMP、WebQuestions、TriviaQA等数据集上，Toolformer（6.7B）零样本性能优于GPT-3（175B）和GPT-J（6.7B）基线，且困惑度与原始GPT-J相当。
>   来源：Abstract / Experiments
>
> - **局限信息**：工具集固定，无法学习新工具；采样过程可能产生噪声；未探索低资源语言场景。
>   来源：Discussion / Limitation

> [!note]- 我的批注 / Zotero 批注
> - Zotero item key: 3BSQRKD9
> - PDF key: 待核查
> - 批注摘录：待核查：需回填 Zotero 真实批注。

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：tool-augmented-language-model, self-supervised-learning, api-calling
> - 候选标签：language-model, tool-use, zero-shot-learning, external-tools, calculator, search-engine, translation, calendar
> - 当前标签：tool-augmented-lm, self-supervised, api-calling
> - 研究关系：本文提出了一种自监督方法让语言模型学习工具使用，与先前需要人工标注或任务特定设置的工作形成对比。它建立在用外部工具增强语言模型的思想上，并使用基于困惑度的过滤方法选择有用的API调用。

## 6. 元数据（仅保留一份）
| 项目 | 内容 |
| --- | --- |
| Authors | Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom |
| Year | 2023 |
| Venue | arXiv preprint arXiv:2302.04761 |
| DOI | 待核查：需回查原文。 |
| Zotero item key | 3BSQRKD9 |
| PDF key | 待核查：需回查原文。 |
| Zotero collections | 待核查：需从 Zotero 同步。 |
| Zotero tags | 待核查：需从 Zotero 同步。 |

## 7. 待复核问题
### 高优先级待复核
- DOI / arXiv ID
- 数据集 / benchmark 列表
- 消融实验与效率成本
- 失败案例与局限原文出处

### 其他待复核问题
- Toolformer如何处理工具调用失败或错误结果？
- 如何扩展到更复杂的工具链或组合使用？
- 自监督训练是否可能引入偏见？
