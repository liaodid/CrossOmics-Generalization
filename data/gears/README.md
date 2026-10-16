# GEARS 使用的 Perturb-seq 与遗传交互数据

## 是什么

GEARS 复用的遗传扰动转录组资源；是本地 G2CP 骨干及若干后续方法的基础。基因图、GO 注释属于先验，不是测得的蛋白组。

## 子数据集与获取

下表来自本地 PDF 的 Data availability；原始项目与作者处理后的矩阵是不同版本。

| 资源 | 原始入口 | 内容 / 本项目关注点 |
|---|---|---|
| Norman | [GSE133344](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344) | K562 单/双基因 CRISPRa，组合泛化 |
| Adamson | [GSE90546](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE90546) | 遗传扰动响应；与线性基线论文共享 |
| Replogle genome-scale | [figshare.plus.20022944](https://doi.org/10.25452/figshare.plus.20022944) | K562、RPE-1 等基因扰动；每个对象背景需核实 |
| Dixit / Jost / Tian | [GSE90063](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE90063)、[GSE132080](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132080)、[GSE124703](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE124703) | 额外 Perturb-seq 实验，具体规模查原始项目 |
| Replogle combinatorial / Horlbeck | [GSE146194](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE146194)、[GSE116198](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116198) | 额外组合与交互验证资源；不要默认都可作同一种单细胞矩阵 |

处理数据与配置从 [GEARS](https://github.com/snap-stanford/GEARS) 和论文列出的 [GEARS_misc](https://github.com/yhr91/GEARS_misc) 追溯。

## 状态

📝 原文来源已登记；本次未下载这些数据，也未确认各在线入口当前状态。已存在的 [UniPert-G2CP 数据包](../unipert-g2cp-zenodo/README.md)是其下游另一个发布版本，不能混为 GEARS 原始处理数据。

## 输入与整理约定

保留 counts、基因顺序、扰动基因列表、对照、细胞背景和来源实验。单/双基因组合规范化为无序成分集合；“零/一个/两个未见组分”划分各自登记。GO 图、共表达图、训练划分与随机种子应与矩阵一起追踪。

`raw/<source>/` 存原始或作者原样发布数据，`processed/<source>/<version>/` 存派生结果；不从全体测试响应计算共表达后再声称无测试信息。规模应按所选版本读取，不在多个方法之间搬用细胞数。

## 与本项目的关系

适合支持遗传到化学扰动迁移的消融，不能替代药物蛋白组终点。基因敲除/激活和药物抑制的强度、靶点范围及时间不等价。

## 核验依据

[本地 GEARS PDF](../../pdf/gears.pdf)，Data availability、单/双基因测试设计；[论文介绍](../../docs/literature/gears.md)。
