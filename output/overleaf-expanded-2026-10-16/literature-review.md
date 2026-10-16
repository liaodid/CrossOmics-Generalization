# 文献调研记录：虚拟细胞与扰动响应预测

检索截止：2026-09-16。此文档对应第二版 slides：只谈虚拟细胞，以转录组扰动响应预测为具体任务。第一版围绕科研 Agent 与经验积累的来源已从 slides 与参考文献页移除，其核查记录保留在文末。没有开展模型训练、数据下载或湿实验。

## 覆盖范围与实际核查深度

先检索虚拟细胞综述、基础模型、扰动预测和独立评测；第一版还按汇报人当时的兴趣补充了科研 Agent、记忆和持续评测类工作。

使用 arXiv 官方 API，限定首次提交时间为 2026-01-01 至 2026-09-16，执行四组可复现检索：

| 查询组 | 命中条目 | 本次取得的元数据 | 本版 slides 是否引用 |
|---|---:|---:|---|
| Agent 改进、记忆与技能（标题） | 963 | 963 | 否，第一版主线 |
| 科学、生物、单细胞领域 Agent | 332 | 332 | 否，第一版主线 |
| 相关 benchmark / evaluation | 397 | 397 | 部分 |
| 虚拟细胞与扰动预测（标题） | 38 | 38 | 是 |

四组去重后为 **1,678 条元数据**。这表示执行完这些查询的分页，**不表示精读了 1,678 篇论文，也不表示检索穷尽了 2026 年全部相关 arXiv**。关键词会漏检，同义词和交叉领域边界会影响召回，命中结果也包含不相关条目。没有纳入尚未发生的 9 月 17 日至年底。首次发表于 2025 年而在 2026 年更新的论文由补充检索覆盖，不能从上述日期过滤保证完整召回。虚拟细胞与扰动预测这一组只按标题匹配，召回偏窄，是本版最需要补检的部分。

- `research/arxiv-2026.csv`：可浏览的去重检索索引。
- `research/arxiv-2026.json`：精确查询、分页计数及元数据。
- `scripts/search_arxiv.py`：查询脚本；服务端元数据更新后再次运行可能得到不同计数。
- `research/selected-sources.json`：本版的 21 项核心来源及实际核查层级，编号与参考文献页一致。

对与主线最相关的条目做了定向筛选，按下表标注摘要核查与正文核查。尚未逐篇筛查全部元数据，也未做完整系统综述的纳入/排除判定。

## 本版核心证据

编号与 slides 参考文献页一致：1–3 愿景与数据，4–9 预测模型，10–13 评测与任务设置，14–21 LLM 与细胞数据的其他连接。

| 编号 | 来源与链接 | 实际核查层级 | 采用的结论及边界 |
|---|---|---|---|
| 1 | [How to build the virtual cell with artificial intelligence: Priorities and opportunities](https://doi.org/10.1016/j.cell.2024.11.015)；Bunne et al. · Cell, 2024 | 概念综述；核查摘要及评价、数据相关正文。 | 多尺度、多模态细胞建模的愿景；初期价值在于可验证假设。 |
| 2 | [Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq](https://doi.org/10.1016/j.cell.2022.05.013)；Replogle et al. · Cell, 2022 | 核查 Perturb-seq 数据说明与正文。 | 基因组规模 CRISPRi 扰动与单细胞转录组读出；候选任务的主要数据来源。 |
| 3 | [Transcriptome-wide analysis of differential expression in perturbation atlases](https://doi.org/10.1038/s41588-025-02169-3)；Nadig et al. · Nature Genetics, 2025 | 核查摘要和数据说明。 | 扰动图谱的差异表达分析；效应随细胞背景变化，跨背景任务定义需谨慎。 |
| 4 | [Predicting transcriptional outcomes of novel multigene perturbations with GEARS](https://doi.org/10.1038/s41587-023-01905-6)；Roohani et al. · Nature Biotechnology, 2024（2023 在线） | 模型论文；核查模型、划分及评价相关正文。 | 利用基因关系图预测单/多基因扰动；原始设置须与跨背景预测区别。 |
| 5 | [scGPT: toward building a foundation model for single-cell multi-omics using generative AI](https://doi.org/10.1038/s41592-024-02201-0)；Cui et al. · Nature Methods, 2024 | 模型论文；核查摘要与任务描述。 | 基因和分箱表达值建模，含扰动预测微调任务；不能把微调能力直接等同于零样本泛化。 |
| 6 | [Transfer learning enables predictions in network biology](https://doi.org/10.1038/s41586-023-06139-9)；Theodoris et al. · Nature, 2023 | 核查摘要与 rank-value 编码说明。 | Geneformer 使用经过表达统计校正的排序编码；不直接输出表达值。 |
| 7 | [Large-scale foundation model on single-cell transcriptomics](https://doi.org/10.1038/s41592-024-02305-7)；Hao et al. · Nature Methods, 2024 | 核查期刊摘要与模型说明。 | scFoundation 学习表达表示；输入与训练目标有别于其他单细胞基础模型。 |
| 8 | [Predicting cellular responses to perturbation across diverse contexts with State](https://doi.org/10.1016/j.cell.2026.07.052)；Adduri et al. · Cell, 2026（8 月 31 日在线） | 期刊出版信息、摘要；另核查官方模型页和预印本部分正文。 | 在细胞集合上建模状态转移；固定模型接口可作为候选预测器。 |
| 9 | [Stack: In-Context Learning of Single-Cell Biology](https://doi.org/10.64898/2026.01.09.698608)；Dong et al. · bioRxiv, 2026（预印本） | 核查预印本摘要及 Arc 官方说明；标题与作者经 Crossref 元数据核对。 | 细胞集合的上下文学习是新进展；本版不把其指标与其他设置混用。 |
| 10 | [Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines](https://doi.org/10.1038/s41592-025-02772-6)；Ahlmann-Eltze et al. · Nature Methods, 2025 | 独立评测；核查正文、基线与划分方法。 | 在所测任务中简单基线具有竞争力；双基因加性基线有其适用条件。 |
| 11 | [Systema: a framework for evaluating genetic perturbation response prediction beyond systematic variation](https://doi.org/10.1038/s41587-025-02777-8)；Viñas Torné et al. · Nature Biotechnology, 2026（2025 在线） | 评测方法；核查正文、centroid accuracy 及局限。 | 共享变化会影响常用分数；仍发现部分模型能恢复特定功能群信息。 |
| 12 | [Zero-shot evaluation reveals limitations of single-cell foundation models](https://doi.org/10.1186/s13059-025-03574-x)；Kedzierska et al. · Genome Biology, 2025 | 核查正文；标题经 Crossref 元数据核对。 | 主要是零样本表征评测，所测基础模型未稳定超过简单方法；预训练不保证迁移。 |
| 13 | [The 2026 Virtual Cell Challenge: predicting perturbation responses in cell contexts a model has never seen](https://arcinstitute.org/news/virtual-cell-challenge-2026)；Arc Institute · 官方任务说明，2026-08-20 | 官方任务全文。 | 目标背景提供对照而隐藏干预响应；并非所有该背景信息都不可见。 |
| 14 | [Cell2Sentence: Teaching Large Language Models the Language of Biology](https://proceedings.mlr.press/v235/levine24a.html)；Levine et al. · ICML, 2024 | 核查论文摘要与 PMLR 页面。 | 基因排序文本支持直接适配语言模型。 |
| 15 | [Scaling Large Language Models for Next-Generation Single-Cell Analysis](https://doi.org/10.1101/2025.04.14.648850)；Rizvi et al. · bioRxiv, 2025/2026（预印本） | 核查 v4 摘要及作者研究发布页。 | C2S-Scale：基因排序文本接入 LLM；特定细胞实验支持的假设不能泛化为普遍疗效。 |
| 16 | [Simple and effective embedding model for single-cell biology built from ChatGPT](https://doi.org/10.1038/s41551-024-01284-6)；Chen and Zou · Nature Biomedical Engineering, 2025（2024 在线） | 核查期刊摘要、出版信息及代码指针。 | GenePT 将基因描述转为向量；它是表示方法，不是预测器。 |
| 17 | [Universal Cell Embeddings: A Foundation Model for Cell Biology](https://doi.org/10.1101/2023.11.28.568918)；Rosen et al. · bioRxiv, 2023（预印本） | 核查原始预印本摘要与表示说明；标题与作者经 Crossref 元数据核对。 | 使用蛋白质表示连接跨物种细胞。 |
| 18 | [Genome modelling and design across all domains of life with Evo 2](https://doi.org/10.1038/s41586-026-10176-5)；Brixi et al. · Nature, 2026 | 核查期刊摘要与出版信息；标题经 Crossref 元数据核对。 | DNA 序列模型的能力需与细胞响应预测区别。 |
| 19 | [TranscriptFormer: A generative cell atlas across 1.5 billion years of evolution](https://doi.org/10.1126/science.aec8514)；Pearce et al. · Science, 2026 | 核查期刊元数据与摘要。 | 跨物种生成式图谱；保留为补充阅读。 |
| 20 | [CellAgent: An LLM-driven Multi-Agent Framework for Automated Single-cell Data Analysis](https://arxiv.org/abs/2407.09811)；Xiao et al. · arXiv, 2024 | 核查 arXiv 摘要与方法概述。 | 规划、执行、评估与任务内迭代；本版仅作为 LLM 连接方式之一列出。 |
| 21 | [Biomni: A General-Purpose Biomedical AI Agent](https://doi.org/10.1101/2025.05.30.656746)；Huang et al. · bioRxiv, 2025（所查预印本） | 核查原始预印本摘要、架构概述及作者信息。 | 检索辅助规划和代码执行组合生物工具；本版仅作为 LLM 连接方式之一列出。 |

## 补充查阅的原始来源

- [ESM, Science 2023](https://doi.org/10.1126/science.ade2574)：核查摘要与出版信息；提供蛋白质语言模型这一分子层面的参照。
- [Arc Virtual Cell Atlas](https://arcinstitute.org/tools/virtualcellatlas)：官方数据资源说明；2025 VCC 数据公开，不代表本项目已经下载和审计。

## 第一版核查过、本版未引用的来源

以下条目服务于第一版的科研 Agent 主线。本版 slides 与参考文献页不再引用；保留核查记录以便日后需要时复用。

| 来源与链接 | 实际核查层级 |
|---|---|
| [EvoScientist](https://arxiv.org/abs/2603.08127)；Lyu et al. · arXiv, 2026（预印本） | 核查摘要及方法正文 3.2–3.5。 |
| [Darwin Godel Machine](https://arxiv.org/abs/2505.22954)；Zhang et al. · arXiv, 2025 | 核查原始摘要与机制概述。 |
| [Hyperagents](https://arxiv.org/abs/2603.19461)；Zhang et al. · arXiv, 2026（预印本） | 核查原始摘要与机制概述。 |
| [MemRL](https://arxiv.org/abs/2601.03192)；Zhang et al. · arXiv, 2026（预印本） | 核查 arXiv v2 摘要。 |
| [SEA-Eval](https://arxiv.org/abs/2604.08988)；Jiang et al. · arXiv, 2026（预印本） | 核查 v3 摘要、任务流及指标正文。 |
| [EvoMemBench](https://arxiv.org/abs/2605.18421)；Wang et al. · arXiv, 2026（预印本） | 核查 v2 摘要与二维评价设置。 |
| [AgentStream](https://arxiv.org/abs/2608.00155)；Yan et al. · arXiv, 2026（预印本） | 核查 v1 摘要与任务流定义。 |
| [BixBench](https://arxiv.org/abs/2503.00096)；Mitchener et al. · arXiv, 2025 | 核查 arXiv v3 摘要及任务描述。 |
| [BioAgent Bench](https://arxiv.org/abs/2601.21800)；Fa et al. · arXiv, 2026 | 核查 v4 摘要；元数据注明 ICML 2026 camera ready。 |
| [BixBench3](https://arxiv.org/abs/2608.25286)；Koch et al. · arXiv, 2026（预印本） | 核查 v1 摘要、任务规模与产物评价说明。 |

## 本版做出的收敛

汇报人目前没有相关项目经历，组内课题是虚拟细胞。因此本版把范围收敛为虚拟细胞本身，以转录组扰动响应预测为具体任务，提出两个候选方向：方向 A（首选）问目标细胞背景只提供对照数据时，预训练细胞模型相对简单基线的增益有多大、出现在哪些扰动和基因群上；方向 B（备选、可并行）借 Systema 的分解思路，把响应拆成共享的系统性变化与扰动特异信号，分层评估后输出可预测性地图。两者共用数据审计、按背景划分与冻结的评分脚本。均为研究设想，不能当作已验证创新。

优先复现对照均值、源背景平均效应迁移、线性/加性基线，再接入一个公开预测器（GEARS 或 State 权重）。按细胞背景划分，同一数据集不跨集合泄漏；测试答案与评分脚本在实验前冻结；每个指标同时报告全部基线，并按扰动与基因群做分层分析。

第一阶段考察的是评估与复现，不声称改进底层预测模型。是否具有论文级创新，需要在基线结果之后与 State、Stack 及独立评测的已报告结果对照后判断。

slides 第 11–13 页的实验条件（跨课题定位图、两阶段泳道、医院合作关卡）为经验性整理，不引用文献；显存与数据规模为量级估计，合规事项以医院伦理委员会与主管部门规定为准。

## 尚需补充的工作

1. 按明确纳入标准筛选 2026 检索全集中的虚拟细胞与扰动预测条目，补充同义词、bioRxiv 工作，以及 2025 首发而 2026 更新的论文。
2. 完整阅读并复现 Ahlmann-Eltze et al. 的基线与划分代码；核对 GEARS、State 的公开权重、接口与训练数据暴露。
3. 审计候选数据集（Perturb-seq、VCC 2025 数据）与预处理，设计按背景划分、没有泄漏的最小任务集。
4. 与老师确认应用价值、计算预算和生物结果的核验条件，再决定研究贡献。


## 2026-10-16 扩展核查

新增 [22–25] 的数据与方法页面。前三篇使用用户提供正式 PDF，CPT 使用 v1 全文及 SI。数据规模、版本变化和未解决的统计/评估输入疑点见 [data-audit.md](research/data-audit.md)。
