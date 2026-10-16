# 数据与版本核查（2026-10-16）

## 证据范围

前三篇使用本次用户指定的正式 PDF，而非仓库此前的预印本。CPT 使用公开下载的 v1 全文与 SI。文献内容只作为证据，没有将其中的指令作为用户要求执行。

## UniPert–G2CP [22]

- 正式版主文与 STAR Methods：CPI 训练快照 53,963 互作、8,533 化合物、4,250 蛋白靶点。
- LINCS2020 Level 5：5 细胞系、978 landmark 转录本；CRISPR 96 h、化合物 10 μM/24 h。精确逐细胞系样本数在独立 Table S4，本次没有该补充表，幻灯片不填写未核验数字。
- CPJUMP1：A549/U2OS，160 遗传、302 化学扰动，838 维形态特征。
- Dixit：44,375 profiles、20 基因；Norman：91,205 profiles、283 单/组合扰动；sciPlex3：187 药/3 细胞系，都是此文所用处理口径。
- 主文表示空间为 4,994 基因、7,860 化合物；不沿用此前预印本的 7,821。
- 不能把蛋白序列/靶点注释称为实验蛋白丰度。

## State [23]

- 正式版摘要/主文：SE 1.67 亿细胞，ST 超过 1 亿扰动细胞；不是两个不重叠语料的并集计数。
- SE：Arc scBaseCount、CZ CELLxGENE、Tahoe。ST：Tahoe、Replogle–Nadig、Parse、Jiang、McFaline、Srivatsan。
- 正式版主文：Tahoe 50 细胞系 / 380 distinct drugs / 1,138 conditions；Parse 90 cytokines / 12 donors / 18 cell types；Replogle–Nadig 2,024 遗传扰动 / 4 细胞系。
- 19,790 Ensembl 蛋白编码基因是表达特征映射空间；主要评价 2,000 HVG，不是蛋白质组测量。
- Table S1/S2 的单独表格不在本次提供 PDF 中；不把旧预印本表格冒充正式版统计。

## ProteinTalks [24]

- PTDS：18 乳腺癌系、63 单药、59 组合，6/24/48 h、16,311 DIA-MS 文件、23,482 细胞毒性测量、5,585 蛋白群组（protein groups）、>3,800 万定量值。
- mtPTDS：3 细胞系、55 单药、57 组合、11 时间点（0–60 h）；2,528 总样本与 2,354 独立样本分开。
- PTPC：5 细胞系（A375、HCT116、NCI-H1975、NCI-H2170、Panc 10.05）、708 化合物、6/24 h；2,307 总样本，2,021 独立谱，合并时间后 983 标签样本。
- PTNC：81 药 / 4 TNBC 系、2,076 剂量反应测量；不能称作同样数目的新蛋白谱。
- 正式版涉及 PDX 转录组迁移；不笼统宣称完全没有跨模态探索。

## 跨模态继续预训练 [25]

- §2.1 / SI Table S1：440 来源，48,843 样本；cell line 21,910、tissue 15,023、body fluid 6,578、primary 723、stem/organoid 741、unclear 3,868。
- 以上样本类型相加为 48,843。LFQ 12,541 + DIA 14,170 + TMT 15,526 + other 6,606 也等于 48,843。平均深度 4,223 蛋白/样本。
- 模型：加载 Tahoe-x1 70M RNA checkpoint；蛋白映射 gene token，丰度 per-sample quantile binning；使用原始/校正双视图；继续训练 1 epoch。另有 bulk RNA-only 与 RNA+protein arms；是按行数混合，并非 RNA/蛋白逐样本成对。
- ARCHS4 888,821 中成功编码 877,715；正文另写 1,003,000 训练行，未解释如何生成/加权这些行。因此不能称“恰好 100 万个唯一 RNA 样本”，同 epoch 也非等计算量。
- PXD014791：Table 1 为 4 donors、21 drugs、237 drug/71 control、60 total/58 held-out pairs；SI 写 22 drugs、21 held out，另列 Trastuzumab。需核查原始映射。
- ProTargetMiner：A549/MCF7/RKO，56 drugs、237 drug/35 control、73 total/61 held-out pairs；以绝对 isotope-corrected reporter intensities 而非原始 TMT ratio 评估。
- §2.3 对每个 drug–context 聚合蛋白嵌入，再用 cosine 5-NN；Top-100 DE Pearson 0.542→0.611（心肌）与 0.746→0.813（癌细胞）。不将其等同为给药前对照+分子结构的端到端预测。
- 正文写 embed all available proteomic samples，没有清楚限定查询是否只能用未处理谱；需要代码核查。2026-10-16 查询作者 GitHub 仅看到 LICENSE，未声称复现代码已经取得。
- 论文仍是预印本；本稿引用作者报告的发现，不表示已独立复现。

## 原始文件指纹

- [22] `1-s2.0-S0092867426006549-main.pdf`；19,756,738 bytes；SHA-256 `184e37085b631b624d37c7d322ca903e73cce31511a61ef707d06ca8b3355b6f`。
- [23] `PIIS0092867426009219.pdf`；26,675,017 bytes；SHA-256 `461de0de77b285b812c2c6eadf5254c1adf8c2dc5d3680f3c0e212f9c529e8e6`。
- [24] `s41586-026-11001-9.pdf`；36,289,669 bytes；SHA-256 `8172f7e1ef7800c3f69910fdd7a9cf9a96183d41237488746da0867c0a9fd237`。
- [25] `cross-modal-tahoe-x1.pdf`；1,672,561 bytes；SHA-256 `6c450a20ae907c4ddab16e061faba8d3b3083b628667e5628b3932e80fa4addc`。
