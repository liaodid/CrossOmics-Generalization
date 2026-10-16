# MultiPert：肾脏 RNA–ADT 扰动数据

## 是什么

使用 CaRPool-seq 共测转录组与蛋白读出的多组学数据，MultiPert 将其作为跨组织和跨技术的评估资源。

## 内容

MultiPert Datasets 小节报告：人胚肾上皮细胞、7 种扰动、8,802 个细胞、20,639 个基因和 7 个蛋白。具体细胞株、扰动靶点名单、处理时间及对照构造需核对 GEO 样本表，不能从“kidney”直接推断为任意肾细胞或病人样本。

## 来源与获取

- [GEO GSE213957](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE213957)。
- [MultiPert PDF](../../../pdf/multipert.pdf)：Datasets、Data availability statement。
- 通用格式见[父目录](../README.md)。

## 状态与存放

⏳ 未下载。原始文件放 `raw/`，RNA/ADT 配对及过滤结果放 `processed/`；下载后记录版本与 SHA-256。

## 使用注意

按条码核对两模态，保留蛋白面板与基因标识。7 个蛋白的误差与数千蛋白的误差不可直接比较；不要仅依据该资源名称就把它当成药物扰动数据。
