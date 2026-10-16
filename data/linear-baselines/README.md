# 线性基线评估论文使用的遗传扰动数据

## 是什么

Ahlmann-Eltze 等（Nature Methods 2025）比较复杂模型与简单基线时采用的固定数据版本。它与 GEARS、CPA、biolord 共用部分原始实验，但过滤、特征和划分可能不同。

## 子数据集与获取

以下直接地址来自本地 PDF 的 Data availability，本次未实际下载或验证链接状态。

| 数据 | 论文取得的处理版本 | 用途 |
|---|---|---|
| Norman | [scFoundation 提供的 figshare 文件 44477939](https://figshare.com/ndownloader/files/44477939) | 单/双扰动与相加基线；不能替换成任意同名版本 |
| Adamson | [GEARS / Harvard Dataverse 文件 6154417](https://dataverse.harvard.edu/api/access/datafile/6154417) | 未见单基因扰动 |
| Replogle K562 | [GEARS / Harvard Dataverse 文件 7458695](https://dataverse.harvard.edu/api/access/datafile/7458695) | 未见单基因扰动 |
| Replogle RPE1 | [GEARS / Harvard Dataverse 文件 7458694](https://dataverse.harvard.edu/api/access/datafile/7458694) | 另一细胞背景下的单基因测试 |

Norman 主实验采用 100 单扰动、124 双扰动和对照；论文的部分误差指标读取 1,000 个高表达基因。这些是特定实验口径，不是上述下载文件的总细胞/基因维度。

## 来源

- [本地 PDF](../../pdf/linear-baselines.pdf)：主文及 Methods → Data availability。
- [复现代码](https://github.com/const-ae/linear_perturbation_prediction-Paper)。
- [Zenodo 14832393](https://doi.org/10.5281/zenodo.14832393)：论文说明含代码与中间计算结果，不能将其中的图表结果当作原始表达标签。

## 状态与存放

📝 已核对下载地址，数据未下载。`raw/` 保存指定文件原样副本；`processed/` 保存明确定义的 pseudobulk、特征与固定划分。复用同一物理文件时在记录里保留其来源版本。

## 输入与整理约定

记录 counts/log 表达层、单/双扰动、对照、read-out 基因、划分与种子；原始细胞条码和聚合后的条件 ID 分开。相加基线需要两个单扰动的训练标签；没有相应标签时不能构造一个泄漏测试信息的“理想基线”。

## 与本项目的关系

用于评价协议和基线设计，没有蛋白组监督。移植到药物蛋白任务时可以使用训练平均变化和结构特征线性模型，但不能声称此遗传基准的结论已经在药物质谱数据成立。

参见[论文介绍](../../docs/literature/linear-baselines.md)和[GEARS 原始资源索引](../gears/README.md)。
