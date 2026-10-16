# PerturbNet 使用的化学、遗传与编码变异响应数据

## 是什么

PerturbNet 的多类型扰动资源集合，响应读出为转录组。输入中有蛋白序列或 GO 表示，不等于输出中具有蛋白丰度标签。

## 子数据集

下表按本地 PDF 的 Table 7/8 逐项记录模型所用统计；不要拿这些数代替原始 accession 总量。

| 数据 | 背景 / 扰动 | measurements | 基因数 | 扰动数（表中口径） |
|---|---|---:|---:|---|
| sci-Plex | A549、K562、MCF7；药物 | 648,857 | 5,087 | 180 |
| LINCS-Drug | 约 100 细胞系；药物 | 677,159 | 978 | 19,990；不重复计算立体异构体为 8,955 |
| Norman | K562；CRISPRa | 109,738 | 2,279 | 230 |
| Jorge | HSPC；GATA1 变异 | 142,872 | 2,477；另一预测实验加 marker 为 2,563 | 257 |
| Ursu | A549；TP53/KRAS 变异 | 162,532 | 1,629 | 163 |

**原文口径不完全一致：** sci-Plex Methods 提到过滤前 648,737 细胞与筛药前 188 药，而 Table 7 是 648,857/180；Ursu Methods 也列过滤阶段 164,931。下载后必须按实际对象、过滤步骤和作者划分核对，不自行把这些数字合并或“纠正”。LINCS 的 measurements 是 bulk profiles，不是单细胞数。

## 来源与获取

- [本地正式版 PDF](../../pdf/perturbnet.pdf)：Methods → Datasets、Table 7/8、Data availability。
- 论文列出的处理数据与权重：[Hugging Face cyclopeta/PerturbNet_reproduce](https://huggingface.co/cyclopeta/PerturbNet_reproduce)。这是仓库入口；不同文件的原始/处理/权重类别需看文件清单。
- [作者代码与教程](https://github.com/welch-lab/PerturbNet)。
- 原始数据：[GSM4150378](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4150378)、[GSE92742](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92742)、[GSE133344](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344)、[GSE161824](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE161824)、[GSE215253](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE215253)。

## 状态

📝 已核对论文来源与表格；本次未下载矩阵、预训练语料或权重，也未检查在线入口当前可访问性。

## 输入与整理约定

化学条件保留 canonical SMILES、立体化学、剂量和细胞背景；遗传条件保留靶基因、变异序列与参考序列。RNA 原始计数、归一化层和潜表示要分开登记，不能将预训练细胞 embedding 当作未经处理的真实表达。

建议 `raw/<source>/`、`processed/<source>/<version>/`，权重与数据分开；同源 LINCS/sci-Plex/Norman 文件复用[相关数据目录](../README.md)。

## 与本项目的关系

适合检验未见扰动表示，但需另接蛋白组真实标签。立体异构体处理会改变有效药物数与测试隔离程度；按结构标准化后再设计骨架划分。更多见[论文介绍](../../docs/literature/perturbnet.md)。
