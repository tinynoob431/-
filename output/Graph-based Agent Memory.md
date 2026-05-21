---
title: "Graph-based Agent Memory: Taxonomy, Techniques, and Applications"
aliases: ["Graph-based Agent Memory"]
tags: ["graph-agent-memory", "llm-agent", "survey"]

zotero_item_key: "L9F6VJ65"
pdf_key: "MEANKNP3"
doi: "10.48550/ARXIV.2602.05665"
year: "2026"
venue: "arXiv preprint"
authors: ["Chang Yang", "Chuang Zhou", "Yilin Xiao", "Su Dong", "Luyao Zhuang", "Yujing Zhang", "Zhu Wang", "Zijin Hong", "Zheng Yuan", "Zhishang Xiang", "Shengyuan Chen", "Huachi Zhou", "Qinggang Zhang", "Ninghao Liu", "Jinsong Su", "Xinrun Wang", "Yi Chang", "Xiao Huang"]
paper_type: "survey"
paper_subtype: "survey" # survey/method/system/benchmark/dataset/empirical/theory/application
status: "seed" # seed / skimmed / read / cited

zotero_collections: ["needs-check"]
zotero_tags: ["Artificial Intelligence (cs.AI)", "FOS: Computer and information sciences", "benchmark", "method"]
canonical_tags: ["graph-based-memory", "agent-memory", "llm-agent"]
candidate_tags: ["memory-taxonomy", "memory-extraction", "memory-storage", "memory-retrieval", "memory-evolution", "knowledge-graph", "self-evolving-systems", "self-evolution"]

core_library_decision: "candidate" # candidate / include / exclude
core_library_reason: "作为关于图记忆的全面综述，包含分类、技术、资源和未来方向，适合作为领域入门和参考文档。"
research_relation: "本文为综述，梳理基于图的智能体记忆的体系与技术，为后续方法设计提供结构化参考。"
---

# Graph-based Agent Memory: Taxonomy, Techniques, and Applications

## 0. 先看这里
> [!abstract]
> **一句话定位**：综述基于图的智能体记忆，涵盖分类、技术（提取、存储、检索、演化）、基准与应用。
> **论文类型**：survey
> **问题**：LLM智能体在长期复杂任务中因知识截止、工具能力不足和性能饱和而受限，记忆是关键模块，图结构可有效建模关系与层次信息。
> **方法**：基于图的智能体记忆通过将记忆单元建模为节点、关系建模为边，实现结构化表示与高效推理。
> **结果**：提供了图基智能体记忆领域的首次系统性综述，覆盖分类法、技术、资源和挑战。
> **是否纳入核心库**：`candidate`
> **理由**：作为关于图记忆的全面综述，包含分类、技术、资源和未来方向，适合作为领域入门和参考文档。
> **为什么读**：如果你研究LLM智能体记忆，尤其是图结构如何用于长期记忆和推理，这篇综述提供系统分类和技术路线。

## 1. 核心内容（默认只读这里）

### 1.1 问题与贡献
- 核心问题：LLM智能体在长期复杂任务中因知识截止、工具能力不足和性能饱和而受限，记忆是关键模块，图结构可有效建模关系与层次信息。
- 核心瓶颈：图记忆的提取、存储、检索和演化环节仍面临效率、可扩展性和动态更新的挑战。
- 相比已有方法：非图结构记忆（如扁平列表、隐藏状态向量）、基于检索的短时记忆、知识图谱等；本文聚焦图结构。

**主要贡献：**
1. 提出了一种基于图的智能体记忆分类法，涵盖短时/长时记忆、知识/经验记忆、非结构化/结构化记忆。
2. 从记忆生命周期（提取、存储、检索、演化）系统分析了图基记忆的关键技术。
3. 总结了支持自我演化智能体记忆的开源库和基准，并探讨了多样化应用场景。
4. 识别了关键挑战和未来研究方向，为构建高效可靠的图基记忆系统提供了指导。

**主要局限：**
推断：作为综述，缺乏实验验证和定量比较；可能未覆盖所有最新方法；挑战部分仅列出方向未提供具体解决方案。

### 1.2 核心思路 / 构造方式（方法论文可按方法主线填写）
- 核心思路：利用图结构的天然优势（关系建模、层级组织、高效检索）来增强智能体记忆的表达和演化能力。
- 关键设计：
  - 记忆提取（Memory Extraction）
  - 记忆存储（Memory Storage）
  - 记忆检索（Memory Retrieval）
  - 记忆演化（Memory Evolution）
- 流程概览：
  1. 输入原始数据（文本、序列、多模态）。
  2. 记忆提取：将数据转换为结构化记忆单元（节点和边）。
  3. 记忆存储：通过索引和组织将单元存入图结构。
  4. 记忆检索：根据查询从图中检索相关子图。
  5. 记忆演化：通过合并、抽象、外部反馈等更新记忆。
  6. 输出推理结果或动作。
- 输入 / 数据来源：智能体从环境感知到的原始数据，包括文本、序列、多模态数据。
- 输出 / 评估对象：智能体执行的动作或推理结果。

### 1.3 实验结论
- 数据集 / Benchmark：待核查：摘要未完整给出数据集细节，需查看实验部分。
- Baselines：待核查：需回查原文。
- Metrics：待核查：当前摘录未完整说明指标定义，需查看实验设置部分。
- 主结果：待核查：需回查原文。
- 可信度判断：综述性质，引用多源工作，可靠性中等
- 最关键图/表：Table I (Methods Categorization)
- 它说明了什么：总结不同方法在记忆生命周期各阶段的分类，展示现有技术概览
- 效率 / 成本：待核查：需查看效率与成本对比。

### 1.4 我的判断与行动
- 值不值得细读：是，该综述系统梳理了基于图的agent记忆方法，对理解该领域全貌和选择研究方向有重要价值。
- 对我当前研究的价值：若研究方向涉及LLM agent记忆或图结构知识表示，可提供分类体系、技术流程和开源资源，帮助定位研究空白。
- 可以借鉴的点：其提出的记忆分类（短/长期、知识/经验、非结构化/结构化）、记忆生命周期（提取、存储、检索、演化）以及图记忆统一视角。
- 暂时不用管的点：应用场景部分较为简略，若不需要具体领域案例可略读。

**下一步行动：**
1. 阅读全文细节，特别是Section III和IV-VII的技术描述。
2. 查阅文中引用的关键开源库和基准（如Awesome-GraphMemory仓库）。
3. 根据自身任务需求，选择适合的图记忆方法进行复现或改进。

## 2. 关键图表（可选）
![[assets/L9F6VJ65/framework_p03_n005.png]]

- 图/表来源：Auto extracted from PDF page 3 image 5
- 图/表类型：framework / architecture / pipeline (待核查)
- 图/表说明：
  - 结构：图基智能体记忆将记忆内容建模为动态图，其中节点表示记忆单元（事件、实体、概念等），边表示它们之间的关系（语义、时序、因果等），从而支持显式关系建模、层级组织和高效检索。
  - 过程：输入原始数据（文本、序列、多模态）；记忆提取：将数据转换为结构化记忆单元（节点和边）；记忆存储：通过索引和组织将单元存入图结构。
  - 意义：总结不同方法在记忆生命周期各阶段的分类，展示现有技术概览
- 需回查项：不需要

## 3. 进阶细节（按需展开）
> [!info]- 核心设计细节
> - 训练策略 / 构造流程：待核查：需回查方法与训练章节。
> - 推理流程 / 评估流程：待核查：需回查方法章节。
> - 假设条件：记忆内容可以抽象为图结构，节点和边具有语义含义；图结构能够支持关系建模和高效检索。
> - 关键部分1：记忆提取：从输入数据中识别实体、事件或概念，并抽取它们之间的关系，形成结构化的记忆候选。
> - 关键部分2：记忆存储：将提取的记忆单元组织成图结构，包括索引、分区、层级化或超图等组织形式。

> [!info]- 公式与算法细节
> - 关键形式: 待核查：综述论文通常不提供统一训练目标或核心公式，需按被综述方法回查原文。
> - 该论文主要提供分类与方法梳理，非单一算法推导。
> - 与 baseline 差异: 待核查：需回查原文。

> [!info]- 实验细节
> - 模型 / Backbone：待核查：当前摘录未明确骨干模型，需查看 setup 或 appendix。
> - 消融实验：待核查：需查看消融实验章节。
> - 失败案例 / 边界：综述指出LLM-based agents存在知识截止、工具不熟练、性能饱和等错误模式，但未进行系统错误分析。
> - 数据集证据：待核查：需回查原文。
> - Backbone证据：待核查：需回查原文。
> - Baseline证据：待核查：需回查原文。
> - 指标证据：待核查：需回查原文。
> - 主结果证据：待核查：需回查原文。
> - 消融证据：待核查：需回查原文。
> - 效率证据：待核查：需回查原文。
> - 失败证据：待核查：需回查原文。

> [!info]- 可引用素材（写作时再看）
> - 背景：LLM-based agents: [1]-[10], Memory taxonomy: [8], Graph memory works: MemLLM, AriGraph, Mem0, Zep, etc.
> - 背景来源：From the abstract: 'Memory emerges as the core module in the LLM-based agents for long-horizon complex tasks' and 'graph stands out as a powerful structure for agent memory due to the intrinsic capabilities to model relational dependencies, organize hierarchical information, and support efficient retrieval.' Also from the introduction: LLMs face limitations like knowledge cutoff, tool incompetence, and performance saturation, motivating memory.
> - Gap：现有LLM-based agents在长期复杂任务中缺乏有效记忆管理，尤其是动态知识积累和结构化记忆整合方面存在明显不足。
> - Gap来源：待核查：需回查原文。
> - 方法比较：综述系统比较了基于图的记忆与扁平列表或隐藏状态记忆的优劣，强调图在关系建模、层次组织和高效检索方面的优势。
> - 方法比较来源：待核查：需回查原文。
> - 实验证据：综述未提供新实验，但引用了多个现有基准和开源库用于评估自我进化代理记忆。
> - 实验证据来源：待核查：需回查原文。
> - 局限：推断：基于图的代理记忆仍面临可扩展性、动态更新和跨任务泛化等挑战；当前方法在复杂多智能体场景中的有效性尚需验证。
> - 局限来源：待核查：需回查原文。

## 4. 证据区（按需展开）
> [!quote]- 证据摘录 / 原文转述
> - **问题背景**：LLM智能体受限于知识截止、工具无能、性能饱和，记忆是克服这些限制的核心模块。
>   来源：Abstract / Introduction
>
> - **核心瓶颈**：图基记忆的关键瓶颈在于如何高效提取、存储、检索和演化记忆内容以支持长时任务。
>   来源：Abstract / Introduction
>
> - **已有方法对比**：非结构记忆（如扁平列表、隐藏状态向量）和基于序列的记忆方法。
>   来源：Related Work / Introduction
>
> - **方法组成**：将记忆内容建模为动态图（节点表示实体/事件/概念，边表示语义/时序/因果关系），并通过提取、存储、检索、演化四个阶段管理。
>   来源：Abstract / Method
>
> - **主要贡献**：提出分类法、生命周期技术分析、资源汇总、挑战与未来方向。
>   来源：Abstract / Introduction
>
> - **局限信息**：综述本身未进行实验验证；可能遗漏部分新兴方法；挑战部分主要以列举形式呈现。
>   来源：Discussion / Limitation

> [!note]- 我的批注 / Zotero 批注
> - Zotero item key: L9F6VJ65
> - PDF key: MEANKNP3
> - 批注摘录：待核查：需回填 Zotero 真实批注。

## 5. 管理信息（可选）
> [!info]- 标签与文献库信息
> - 标准标签：graph-based-memory, agent-memory, llm-agent
> - 候选标签：memory-taxonomy, memory-extraction, memory-storage, memory-retrieval, memory-evolution, knowledge-graph, self-evolving-systems, self-evolution
> - 当前标签：graph-agent-memory, llm-agent, survey
> - 研究关系：本文为综述，梳理基于图的智能体记忆的体系与技术，为后续方法设计提供结构化参考。

## 6. 元数据（仅保留一份）
| 项目 | 内容 |
| --- | --- |
| Authors | Chang Yang, Chuang Zhou, Yilin Xiao, Su Dong, Luyao Zhuang, Yujing Zhang, Zhu Wang, Zijin Hong, Zheng Yuan, Zhishang Xiang, Shengyuan Chen, Huachi Zhou, Qinggang Zhang, Ninghao Liu, Jinsong Su, Xinrun Wang, Yi Chang, Xiao Huang |
| Year | 2026 |
| Venue | arXiv preprint |
| DOI | 10.48550/ARXIV.2602.05665 |
| Zotero item key | L9F6VJ65 |
| PDF key | MEANKNP3 |
| Zotero collections | 待核查：需从 Zotero 同步。 |
| Zotero tags | Artificial Intelligence (cs.AI), FOS: Computer and information sciences, benchmark, method |

## 7. 待复核问题
### 高优先级待复核
- 数据集 / benchmark 列表
- Backbone / base model
- 训练策略与优化目标
- 主评测指标定义
- 主结果表与关键数字
- 消融实验与效率成本

### 其他待复核问题
- 不同图记忆方法在具体任务上的性能差异缺乏定量基准对比。
- 记忆的持续演化机制（如合并、抽象）如何与长期推理协同尚待探索。
- 图记忆的扩展性和可解释性在复杂环境中的表现需进一步验证。
