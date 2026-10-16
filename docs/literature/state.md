# State：跨细胞背景泛化与评价方法参考

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。 本地 PDF 为早期预印本，正式版的补充结论仅来自明确列出的正式版页面或既有项目记录；不能将两个版本的数字混用。

## 论文与代码

- **正式引用 / 目标论文：** Abhinav K. Adduri; Dhruv Gautam; Beatrice Bevilacqua; Mohsen Naghipourfar; Alishba Imran; Rohan Shah; et al.. **Predicting cellular responses to perturbation across diverse contexts with State.** Cell, 2026.
- DOI：[10.1016/j.cell.2026.07.052](https://doi.org/10.1016/j.cell.2026.07.052)
- 本地文件：[本地 PDF](../../pdf/state.pdf)
- **实际下载版本：** bioRxiv 2025 v1；不是 Cell 2026 正式版。
- 下载稿标题：Predicting cellular responses to perturbation across diverse contexts with State。
- 下载稿 DOI：[10.1101/2025.06.26.661135](https://doi.org/10.1101/2025.06.26.661135)。
- 篇幅：66 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/ArcInstitute/state
- 数据：https://github.com/ArcInstitute/state-reproduce

## 为什么值得优先阅读

本项目要证明的是泛化增益，State 对细胞异质性和跨实验背景的处理，以及 Cell-Eval 的评价设计值得借鉴。

## 方法概要

由细胞表示模型和状态转移模型构成。前者从大规模观测数据学习细胞表示，后者以细胞集合建模扰动响应，避免把单细胞响应强行视为可逐个配对的前后观测。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 细胞表示 | 观测单细胞 RNA | 细胞状态嵌入 |
| 状态转移 | 细胞群体、扰动与背景 | 响应后的单细胞转录状态 |

## 论文中的评价设置与结果解读

评估跨数据与跨背景的扰动响应，并通过 Cell-Eval 检查效应识别和差异表达等生物学指标。此处下载版本若为 bioRxiv，应按该版本解读模型规模与实验，不能将预印本数字直接标为 Cell 正式结果。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可借鉴集合级预测和背景编码，但它的转录组成绩不能直接回答蛋白组终点。优先迁移评价框架，再决定是否需要训练这样规模的模型。

## 局限与对比时需要注意的条件

单细胞分布预测与 bulk 质谱平均丰度具有不同的观测单位。模型预训练是否包含测试细胞或测试药物，需要在严格泛化实验中披露。

## 复现与接入建议

阅读方法总图和 Cell-Eval，建立每种药物而非每个细胞的汇总评价；比较未见药物、未见细胞背景及二者同时未见三类测试。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1016/j.cell.2026.07.052](https://doi.org/10.1016/j.cell.2026.07.052)
- [https://www.biorxiv.org/content/10.1101/2025.06.26.661135v1](https://www.biorxiv.org/content/10.1101/2025.06.26.661135v1)
- [https://github.com/ArcInstitute/state](https://github.com/ArcInstitute/state)
- 实际 PDF 来源：[下载地址](https://www.biorxiv.org/content/10.1101/2025.06.26.661135v1.full.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
