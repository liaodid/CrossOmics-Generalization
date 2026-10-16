# totalVI 使用的 RNA–表面蛋白 CITE-seq 数据

## 是什么

同一细胞中配对测量 RNA 与抗体标签表面蛋白的 CITE-seq 资源。用于联合概率建模、去噪和批次整合，**不是药物扰动质谱数据**。

## 子数据集

| 数据 | 生物来源 / 模态 | 论文中的用途 |
|---|---|---|
| SLN-all | 小鼠脾与淋巴结免疫细胞；RNA + 表面蛋白 | 作者产生的主 CITE-seq 资源；具体对象如 SLN111-D1 需按元数据区分 |
| PBMC5k / PBMC10k | 人 PBMC，10x 公共 CITE-seq | 联合建模及跨批次分析 |
| MALT | 10x MALT 样本，RNA + 蛋白 | 与 PBMC 等不同数据来源的整合 |

原文部分评估采用 PBMC10k/MALT 的 14 蛋白面板和 SLN111-D1 的 110 蛋白面板。这是特定分析面板，不是每个对象必然统一的维度。总细胞数与完整基因集合需下载核对。

## 来源与获取

- [本地作者接受稿 PDF](../../pdf/totalvi.pdf)：Data availability、Extended Data Fig. 1；对应正式 DOI [10.1038/s41592-020-01050-x](https://doi.org/10.1038/s41592-020-01050-x)。
- SLN-all：[GEO GSE150599](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE150599)。
- 处理数据：[YosefLab/totalVI_reproducibility](https://github.com/YosefLab/totalVI_reproducibility)。
- 论文提供的 10x 样本入口：[PBMC5k](https://support.10xgenomics.com/single-cell-gene-expression/datasets/3.0.2/5k_pbmc_protein_v3)、[PBMC10k](https://support.10xgenomics.com/single-cell-gene-expression/datasets/3.0.0/pbmc_10k_protein_v3)、[MALT](https://support.10xgenomics.com/single-cell-gene-expression/datasets/3.0.0/malt_10k_protein_v3)。这些是原文旧版网址，是否重定向需下载时核实。
- [Zenodo 4330368](https://doi.org/10.5281/zenodo.4330368)为代码归档入口，不应默认其中含全部原始数据。

## 状态

📝 论文来源已核对；RNA/ADT 计数与条码元数据未下载。本次未检查在线可访问性。

## 输入与整理约定

模型按每细胞 RNA 原始计数、蛋白 ADT 原始计数和批次协变量建模。保存空白/背景、抗体面板、物种、样本和条码信息；RNA 与 ADT 的特征轴独立，不能强行按基因名取交集后视作同一矩阵。

建议 `raw/<sample>/` 放原始对象，`processed/<version>/` 放整理文件；具体 scvi-tools 使用的 AnnData 键名受软件版本影响，需按实际 API 和文件核对，不在这里声称固定作者 schema。

## 与本项目的关系

适合设计模态专用噪声模型或联合表示的小规模验证。人/鼠、观测/扰动以及 ADT/质谱三种差异都要保留；不作为 ProteinTalks 的直接同任务对照。见[论文介绍](../../docs/literature/totalvi.md)。
