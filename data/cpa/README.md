# CPA 使用的单细胞扰动与药物组合数据

## 是什么

CPA 的多条件响应资源集合，包括药物、基因组合和免疫刺激。最值得本项目额外关注的是作者产生的 A549 药物组合转录组 Combosciplex。

## 子数据集

| 数据 | 内容与本地论文口径 | 来源 / 关联目录 |
|---|---|---|
| sci-Plex2 | A549；4 药物、7 剂量、24 h；原矩阵 24,262 细胞，QC 后 14,811，5,000 HVG | [GSM4150377](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4150377) |
| sci-Plex3 | A549、MCF7、K562；188 药物、4 剂量；本文原矩阵 581,777 细胞，抽半为 290,888，5,000 HVG | [GSM4150378](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4150378)；[chemCPA](../chemcpa/README.md)同源不同处理 |
| Combosciplex | A549，13 化合物构成 32 个单药/组合条件；1 μM/药，24 h；Fig. 3 报告 63,378 细胞 | [GSE206741](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE206741) |
| Norman 组合遗传扰动 | K562，单/双基因激活，RNA 读出 | [GSE133344](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344)；[GEARS](../gears/README.md) |
| Kang PBMC / Hagai 跨物种 / L1000 | IFN-β 刺激、LPS 跨物种或 bulk 化合物响应 | 见原文 Datasets；Hagai 为 [E-MTAB-6754](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-6754)；[LINCS](../lincs-l1000/README.md) |

这里是各实验所用数据的索引，不是可以直接拼接的同一矩阵。Combosciplex 的样本/条件数与单细胞数也不是同一计量单位。

## 来源与获取

- [本地正式版 PDF](../../pdf/cpa.pdf)：Datasets、Combosciplex、Fig. 3、Data availability。
- [CPA 复现 notebooks](https://github.com/theislab/cpa-reproducibility/tree/main/notebooks)；[模型代码](https://github.com/theislab/cpa)。
- 上表 accession 来自论文；数据包文件与实时可得性本次未在线核验。

## 状态

📝 已核对论文数据说明，矩阵与元数据未下载。

## 输入与整理约定

组合必须拆成成分列表和每成分剂量；保留时间、细胞系、对照及批次。不要把 `drugA+drugB` 仅当成一个不含结构信息的新 ID，也不要将同一组合因字符串次序不同分到不同集合。

原始下载按 `raw/<dataset>/` 存放，处理与划分按 `processed/<dataset>/<version>/`；共享 sci-Plex3 和 Norman 文件复用，不重复保存原始数据。具体 AnnData 字段由作者代码与文件核实。

## 与本项目的关系

Combosciplex 可用于 RNA 侧的药物组合辅助监督，与 ProteinTalks 的协同任务有联系，但没有成对的质谱蛋白响应。留出组合但保留两个单药的测试，与留出完全新药的测试不同。

方法背景见 [CPA 论文介绍](../../docs/literature/cpa.md)。
