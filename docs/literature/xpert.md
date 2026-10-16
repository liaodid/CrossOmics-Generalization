# XPert：药物、细胞背景和时间剂量泛化方法

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Yue Guo; Hao Zhang; Haitao Hu; Jialu Wu; Ji Cao; Chang-Yu Hsieh; et al.. **Modelling drug-induced cellular perturbation responses with a biologically informed dual-branch transformer.** Nature Machine Intelligence, 2026.
- DOI：[10.1038/s42256-025-01165-w](https://doi.org/10.1038/s42256-025-01165-w)
- 本地文件：[本地 PDF](../../pdf/xpert.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：Modelling drug-induced cellular perturbation responses with a biologically informed dual-branch transformer。
- 下载稿 DOI：[10.1038/s42256-025-01165-w](https://doi.org/10.1038/s42256-025-01165-w)。
- 篇幅：20 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：未在本次核验中单独确认；以论文 Code availability 为准。
- 数据：L1000（具体处理版本见原文 Data availability）

## 为什么值得优先阅读

它明确区分基础状态和扰动变化，并建模剂量与时间，适合为 ProteinTalks 的时间预测及本项目的 RNA 支路提供参考。

## 方法概要

双分支 Transformer 分别编码基础细胞状态与药物诱导调控；以 UniMol 化学表示、药物–靶点/PPI/药物结构相似图和时间剂量 token 组织输入，用注意力捕捉药物–基因交互。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 基础分支 | 未扰动表达的基因 token | 细胞内在表达状态 |
| 扰动分支 | 化学与生物知识、时间、剂量 | 条件特异扰动状态 |
| 输出 | 双分支表征 | 处理后表达与表达变化 |

## 论文中的评价设置与结果解读

L1000 的单剂量单时间场景区分 warm-start、cold-drug 和 cold-cell，并扩展到多剂量多时间。原文还加入全局均值、细胞条件均值和药物条件均值，分别评价整谱和变化量。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 重点借鉴‘状态与变化分离’以及有条件适用的均值基线。若采用双组学 head，可分别预测 RNA 和蛋白变化，同时显式输入时间剂量。

## 局限与对比时需要注意的条件

这是转录组方法，知识图中的蛋白节点不等于蛋白丰度监督。冷药物设置不能使用测试药物的平均响应作为基线；冷细胞设置也不能使用测试细胞标签计算均值。

## 复现与接入建议

核对数据处理、药物划分与图预训练信息来源；先比较简单共享编码器，再判断引入 Transformer 和知识图是否带来额外收益。不要同时改变架构、数据规模与训练预算后归因于跨组学。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s42256-025-01165-w](https://doi.org/10.1038/s42256-025-01165-w)
- [https://www.nature.com/articles/s42256-025-01165-w](https://www.nature.com/articles/s42256-025-01165-w)
- 实际 PDF 来源：[下载地址](https://www.nature.com/articles/s42256-025-01165-w.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
