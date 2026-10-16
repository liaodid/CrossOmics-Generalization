# biolord 使用的药物、遗传及观测单细胞数据

## 是什么

biolord 复用多种数据检验已知/未知属性解耦。与本项目直接相关的是 sci-Plex3 和单/双基因 Perturb-seq；另有胎儿染色质和疟原虫时空图谱，它们不提供药物质谱蛋白监督。

## 子数据集与获取

| 数据 | 论文登记的下载入口 | 用途 |
|---|---|---|
| 所有处理数据的项目页 | [figshare biolord_datasets/160085](https://figshare.com/projects/biolord_datasets/160085) | 获取与作者处理版本一致的对象 |
| sci-Plex3 | [chemCPA 的 sciplex_complete_middle_subset.h5ad](https://f003.backblazeb2.com/file/chemCPA-datasets/sciplex_complete_middle_subset.h5ad) | 未见药物，来自同源 sci-Plex 的专用处理版 |
| Perturb-seq one-gene | [Dataverse 文件 6154020](https://dataverse.harvard.edu/api/access/datafile/6154020) | GEARS 提供的处理数据及附加文件 |
| Perturb-seq two-gene | [Dataverse 文件 6894431](https://dataverse.harvard.edu/api/access/datafile/6894431) | GEARS 提供的组合数据 |
| 胎儿染色质图谱 | [figshare 24886248.v1](https://doi.org/10.6084/m9.figshare.24886248.v1) | scATAC 的属性解耦 |
| Plasmodium liver stage | [GSE181725](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE181725)、[Zenodo 7081863](https://zenodo.org/record/7081863) | 时空/感染状态，后者为处理 Seurat 对象 |

## 来源

[本地正式版 PDF](../../pdf/biolord.pdf)：Methods → Perturb-seq / Drug perturbations、Data availability；[复现仓库](https://github.com/nitzanlab/biolord_reproducibility)。链接依据论文抄录，当前可访问性与文件大小本次未在线核验。

## 状态

📝 已登记来源；本地未下载数据。不同作者的过滤版维度不同，本次不从其他论文借用规模填入该版本。

## 输入与整理约定

保留表达矩阵、已知属性（药物/剂量/细胞系/时间等）、细胞条码、基因名、对照和预定义划分；特征向量的构造也需版本化。论文单基因/双基因实验采用来自 GEARS GO 图的特征，且部分训练按扰动聚合均值，不能默认都是逐细胞监督。

原始下载放 `raw/<source>/`，处理结果放 `processed/<source>/<version>/`；与 [GEARS](../gears/README.md)、[chemCPA](../chemcpa/README.md)共享原始来源时，通过版本记录引用，不重复下载。

## 与本项目的关系

帮助研究细胞/批次与扰动的解耦，但没有直接解决非配对 RNA–质谱蛋白的标签对应。胎儿和疟原虫观测图谱优先级低于药物响应数据。

方法说明见 [biolord](../../docs/literature/biolord.md)。
