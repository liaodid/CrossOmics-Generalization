# XPert 使用的 L1000、PANACEA 与临床转录组

## 是什么

XPert 处理的药物诱导转录组资源，覆盖细胞系、多时间剂量与临床前后治疗数据。预测目标主要限制为 978 个 L1000 landmark 基因；没有质谱蛋白矩阵。

## 子数据集

| 数据 | 内容 / 条件 | 在论文中的用途 |
|---|---|---|
| L1000_full | CMap2020 level-3 处理后的全量集合；保留 3、6、24 h 等条件 | 转录组预训练 |
| L1000_sdst | 10 μM、24 h | 单剂量单时间、冷药物/冷细胞测试 |
| L1000_mdmt | 同一 cell–drug 对具有多剂量多时间信息 | 条件动态预测 |
| L1000_mdmt_pretrain | full 中去除 mdmt 子集的部分 | 多剂量多时间迁移的来源集合 |
| PANACEA | 论文使用的扰动子集涉及 32 kinase inhibitors、11 细胞系；IC20、24 h、三重复 | 独立临床前 RNA 迁移 |
| CDS-DB | 原库更大；作者过滤后为 613 对治疗前后谱、14 癌种、14 药物，保留芯片数据 | 临床适配评估 |

PANACEA 原资源所述 25 细胞系/约 400 临床肿瘤药，和上表模型实际子集不是一个规模；不能混用。L1000 仍复用[已有源目录](../lincs-l1000/README.md)，作者转换版另登记。

## 来源与获取

- [本地正式版 PDF](../../pdf/xpert.pdf)：Methods → Dataset preprocessing、Data availability。
- L1000：[CMap2020](https://clue.io/data/CMap2020#LINCS2020)。
- PANACEA：[GSE186341](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE186341)。
- CDS-DB：[论文列出的网站](http://cdsdb.ncpsb.org.cn/)。
- 作者处理数据：[figshare 28955141](https://doi.org/10.6084/m9.figshare.28955141)、[Zenodo 15357711](https://doi.org/10.5281/zenodo.15357711)。
- [GSanShui/XPert](https://github.com/GSanShui/XPert)：论文称提供最小数据及处理代码。

上述入口依据论文登记，本次未在线核验数据包与下载权限。

## 状态

📝 数据说明已核对；数据、demo 和权重未下载。

## 输入与整理约定

作者为 L1000 处理谱匹配同板 DMSO 对照，整理重复聚合向量；PANACEA 为 `log2(TPM+1)` 后选择 landmark 基因。临床成对谱是同一患者治疗前后信息，不能与对照细胞配对的含义混同。

建议保留 drug/SMILES、cell line、plate、对照来源、剂量原值与单位、离散区间、处理时间、基因顺序、来源患者和重复标记。作者把剂量分为十档，映射在补充表中；本地仅有正文 PDF，不据此虚构具体档位边界。

原始文件放 `raw/<source>/`，处理与划分放 `processed/<source>/<version>/`。HVG、缩放和基因选择的可学习部分在训练集上确定；论文的具体作者文件 schema 需另行核对。

## 与本项目的关系

适合提供时间/剂量 RNA 辅助监督及冷药物评估参考。临床与蛋白组的细胞、采样时间和观测单位不同，不能视作配对蛋白标签。方法说明见 [XPert](../../docs/literature/xpert.md)。
