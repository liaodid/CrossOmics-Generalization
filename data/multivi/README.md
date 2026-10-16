# MultiVI 使用的配对与缺失模态单细胞数据

## 是什么

MultiVI 用 RNA、ATAC 和表面蛋白数据检验部分配对整合与缺失模态推断。主线是观测多组学整合，并非小分子蛋白响应预测。

## 子数据集与获取

| 数据 | 模态 / 用途 | 论文登记入口 |
|---|---|---|
| 10x PBMC Multiome | 配对 RNA + ATAC；人工拆分配对的插补评估 | [10x 数据集目录](https://www.10xgenomics.com/resources/datasets)，需进一步确认具体版本与样本 |
| TEA-seq | RNA + ATAC + 表面蛋白 | [GSE158013](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158013) |
| DOGMA-seq | RNA + ATAC + 表面蛋白，含不同条件 | [GSE156478](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE156478) |
| Satpathy | 单模态 scATAC，跨来源整合 | [GSE129785](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE129785) |
| Ding | 单模态 scRNA，跨来源整合 | [GSE132044](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132044) |
| 中间数据、notebooks 和模型 | 复现论文分析 | [Zenodo 5762077](https://doi.org/10.5281/zenodo.5762077) |

各来源的总细胞、特征和配对比例随实验变化，不能用一个“MultiVI 数据集大小”概括。原文人工打散配对产生的两个单模态视图不是两个独立新细胞。

## 来源

[本地正式版 PDF](../../pdf/multivi.pdf)：Methods、Data availability、Code availability 及参考文献 38。以上入口仅依据原文登记，本次未重新核验在线状态。

## 状态

📝 已核对来源；本仓库未下载计数矩阵、peak 集合、权重或插补结果。

## 输入与整理约定

分别保存 RNA counts、ATAC 片段/peak 计数、蛋白 ADT、细胞条码、样本/批次以及模态是否真实观测的掩码。peak 的参考基因组和坐标转换要登记；不能把缺失模态全零当成生物学零观测。

`raw/<source>/` 保存下载原件，`processed/<source>/<version>/` 保存共同特征集合、配对规则和人工遮蔽划分。GSE156478 与 [MultiPert PBMC](../multipert/pbmc/README.md)同源，应共享实体并分别登记子集。

## 与本项目的关系

可为部分配对的 RNA–蛋白数据处理提供思路；完全无配对、无共享锚点时的对应关系不会因采用 MultiVI 自动确定。蛋白为 ADT；缺失模态插补与未见药物扰动响应是不同任务。

方法说明见[MultiVI 论文介绍](../../docs/literature/multivi.md)。
