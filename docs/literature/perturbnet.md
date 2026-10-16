# PerturbNet：未见化学及遗传扰动的分布预测基线

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Hengshi Yu; Weizhou Qian; Yuxuan Song; Joshua D Welch. **PerturbNet predicts single-cell responses to unseen chemical and genetic perturbations.** Molecular Systems Biology, 2025.
- DOI：[10.1038/s44320-025-00131-3](https://doi.org/10.1038/s44320-025-00131-3)
- 本地文件：[本地 PDF](../../pdf/perturbnet.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：PerturbNet predicts single-cell responses to unseen chemical and genetic perturbations。
- 下载稿 DOI：[10.1038/s44320-025-00131-3](https://doi.org/10.1038/s44320-025-00131-3)。
- 篇幅：23 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/welch-lab/PerturbNet
- 数据：见作者仓库链接的 Hugging Face 数据与权重

## 为什么值得优先阅读

它以扰动特征而不是仅以固定 ID 推断响应，适合比较共享扰动表示能否泛化到未见药物。

## 方法概要

由扰动表示网络、细胞表示网络和条件可逆映射网络组成。前两个网络分别学习两侧空间，再以条件 normalizing flow 将扰动映射到细胞隐状态分布，并解码得到表达。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 扰动网络 | 化合物、遗传扰动或变异描述 | 扰动嵌入 |
| 细胞网络 | 表达数据 | 细胞隐表示 |
| 条件映射 | 扰动嵌入与随机变量 | 响应细胞状态分布 |

## 论文中的评价设置与结果解读

使用化学、遗传及编码变异等场景检验未见扰动预测，关注细胞状态分布。作者代码提供 LINCS、sci-Plex 和遗传扰动的复现 notebook。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可作为 RNA 支路的强方法参考，也可与 UniPert 表示结合形成受控的迁移实验。若最终只比较 bulk 蛋白均值，必须说明分布预测能力没有被完整评价。

## 局限与对比时需要注意的条件

原论文不是 RNA 与质谱蛋白共同监督模型；将细胞编码器改为多组学需要重新设计观测似然。相同结构的药物靠近训练集可能使未见药物任务更容易。

## 复现与接入建议

先检查 LINCS 药物划分，再选择与本项目一致的冷药物测试。比较均值响应与分布层指标，并记录三部分网络分别用了哪些预训练数据。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s44320-025-00131-3](https://doi.org/10.1038/s44320-025-00131-3)
- [https://github.com/welch-lab/PerturbNet](https://github.com/welch-lab/PerturbNet)
- 实际 PDF 来源：[下载地址](https://link.springer.com/content/pdf/10.1038/s44320-025-00131-3.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
