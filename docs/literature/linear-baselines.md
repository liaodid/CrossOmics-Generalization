# Linear baselines benchmark：实验可信度与简单强基线设计

> 整理日期：2026-10-15。阅读优先级：**P0**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Constantin Ahlmann-Eltze; Wolfgang Huber; Simon Anders. **Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines.** Nature Methods, 2025.
- DOI：[10.1038/s41592-025-02772-6](https://doi.org/10.1038/s41592-025-02772-6)
- 本地文件：[本地 PDF](../../pdf/linear-baselines.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines。
- 下载稿 DOI：[10.1038/s41592-025-02772-6](https://doi.org/10.1038/s41592-025-02772-6)。
- 篇幅：21 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/const-ae/linear_perturbation_prediction-Paper
- 数据：https://doi.org/10.5281/zenodo.14832393

## 为什么值得优先阅读

你需要证明额外 RNA 监督带来真实的蛋白响应增益。该文说明复杂模型的高表达相关性并不保证其学到了扰动特异效应。

## 方法概要

统一比较多种单细胞基础模型、GEARS 和 CPA 与简单基线；双扰动采用对照不变及单扰动效应相加，未见单扰动采用均值和带基因/扰动表示的线性模型。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 双扰动任务 | 已测单扰动响应 | 相加的双扰动预测 |
| 未见单扰动任务 | 训练表达与基因/扰动表示 | 线性预测表达谱 |
| 模型审计 | 预测与真实变化 | 误差、相互作用识别及变化量指标 |

## 论文中的评价设置与结果解读

在作者所测的数据、任务与划分中，深度方法没有超过相应简单基线。双扰动主要使用 Norman 数据，单扰动包括 Replogle 和 Adamson 数据，并以重复划分检验稳定性。该结论有明确适用范围。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 为本项目增加对照不变、训练平均变化、细胞系条件均值、结构特征线性或岭回归等基线。主比较在完全相同的蛋白观测集合与药物划分上完成。

## 局限与对比时需要注意的条件

该论文测试的是遗传扰动转录组，不能据此断言所有药物蛋白预测深度模型无效。其相加基线需要单扰动数据，不能机械用于只有单药的测试。

## 复现与接入建议

先实现同输入预算的简单基线，再报告每药物 Δ Pearson、MSE、变化方向和差异蛋白覆盖。以药物为独立单位统计置信区间，避免用大量重复样本制造虚假的统计显著性。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s41592-025-02772-6](https://doi.org/10.1038/s41592-025-02772-6)
- [https://www.nature.com/articles/s41592-025-02772-6](https://www.nature.com/articles/s41592-025-02772-6)
- [https://github.com/const-ae/linear_perturbation_prediction-Paper](https://github.com/const-ae/linear_perturbation_prediction-Paper)
- 实际 PDF 来源：[下载地址](https://www.nature.com/articles/s41592-025-02772-6.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
