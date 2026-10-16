# totalVI：RNA 与蛋白联合概率建模基础

> 整理日期：2026-10-15。阅读优先级：**P2**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Adam Gayoso; Zoë Steier; Romain Lopez; Jeffrey Regier; Kristopher L. Nazor; Aaron Streets; et al.. **Joint probabilistic modeling of single-cell multi-omic data with totalVI.** Nature Methods, 2021.
- DOI：[10.1038/s41592-020-01050-x](https://doi.org/10.1038/s41592-020-01050-x)
- 本地文件：[本地 PDF](../../pdf/totalvi.pdf)
- **实际下载版本：** 作者接受稿，由 UC eScholarship 存储；对应 Nature Methods 2021 正式论文。
- 下载稿标题：Joint probabilistic modeling of single-cell multi-omic data with totalVI。
- 下载稿 DOI：[10.1038/s41592-020-01050-x](https://doi.org/10.1038/s41592-020-01050-x)。
- 篇幅：53 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/scverse/scvi-tools
- 数据：原文 CITE-seq 公开数据及 scvi-tools 教程

## 为什么值得优先阅读

它说明两种组学应采用各自的观测噪声模型，而不只是把两个 MSE 相加；也有助于理解 ADT 与质谱蛋白的差别。

## 方法概要

以生成模型共同表示 RNA 和表面蛋白，显式考虑计数噪声、蛋白前景/背景与批次效应，通过变分推断获得共享细胞状态和去噪后的组学表达。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 测量输入 | 同一细胞的 RNA 与 CITE-seq 蛋白计数 | 联合细胞隐状态 |
| 噪声建模 | 模态与批次信息 | RNA 观测及蛋白前景/背景 |
| 分析输出 | 后验分布 | 去噪、差异分析和联合表示 |

## 论文中的评价设置与结果解读

验证联合表示、批次整合、不同蛋白面板整合和差异分析，包含免疫细胞 CITE-seq 数据。它主要是观测数据分析模型，不能据此认为具有未见药物响应预测能力。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可参考模态专用似然和噪声分解。若本项目采用质谱 log 强度，需针对连续值、检测限与缺失重新设计蛋白观测模型。

## 局限与对比时需要注意的条件

表面蛋白 ADT 计数与全蛋白质谱强度不是同一种数据。该模型本身缺少本项目所需的化学扰动输入与反事实状态转移。

## 复现与接入建议

阅读生成图与蛋白背景模型。把它作为表示学习组件或消融时，另外定义扰动映射和测试协议，不将重建损失当作响应预测成绩。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s41592-020-01050-x](https://doi.org/10.1038/s41592-020-01050-x)
- [https://www.nature.com/articles/s41592-020-01050-x](https://www.nature.com/articles/s41592-020-01050-x)
- [https://docs.scvi-tools.org/en/latest/user_guide/models/totalvi.html](https://docs.scvi-tools.org/en/latest/user_guide/models/totalvi.html)
- 实际 PDF 来源：[下载地址](https://escholarship.org/content/qt24f8f9g4/qt24f8f9g4_noSplash_7b2fe617b4553bd0034b54840b3f5222.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
