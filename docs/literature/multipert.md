# MultiPert：直接的 RNA–蛋白多组学扰动预测先例

> 整理日期：2026-10-15。阅读优先级：**P0**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Mengyuan Zhao; Xinyue Tang; Jiawei Li; Cheng Liang; Jijun Tang; Fei Guo. **MultiPert: An adversarial alignment and dual attention framework for single-cell multi-omics perturbation prediction.** PLOS Computational Biology, 2026.
- DOI：[10.1371/journal.pcbi.1014054](https://doi.org/10.1371/journal.pcbi.1014054)
- 本地文件：[本地 PDF](../../pdf/multipert.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：MultiPert: An adversarial alignment and dual attention framework for single-cell multi-omics perturbation prediction。
- 下载稿 DOI：[10.1371/journal.pcbi.1014054](https://doi.org/10.1371/journal.pcbi.1014054)。
- 篇幅：20 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/MengyuanZhaoo/MultiPert
- 数据：https://zenodo.org/records/7041849 ; https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE213957

## 为什么值得优先阅读

论文同时预测扰动后 RNA 与蛋白，是必须讨论的相关工作；其测量技术和扰动类型与本项目的区别，决定能否形成清晰的新问题。

## 方法概要

先分别预训练 RNA 的 ZINB-VAE 和蛋白 ADT 的自编码器；用组学专用编码器保留特异信息，用共享编码器与对抗网络对齐公共表示。GO 图提供扰动表示，交叉注意力与通道注意力融合扰动和细胞状态，再由两个解码器重建响应。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 状态输入 | 对照 RNA 与 ADT 蛋白 | 各模态独有及共享表示 |
| 扰动输入 | GO 图、GEARS 提供的扰动嵌入 | 组学专用扰动表示 |
| 预测输出 | 对齐和注意力融合后的状态 | 扰动后 RNA 与 ADT 丰度 |

## 论文中的评价设置与结果解读

THP-1 与肾脏多组学数据用于评估，包含未见扰动设置，使用 MSE、PCC 等指标，并分析变化方向及免疫检查点相关信号。具体数据与划分见论文 Materials and methods 和 Results；这里不将其结果外推为药物质谱数据上的优势。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** ‘共享表示加两个 head’本身已经存在。可研究的差异包括：小分子结构编码、非配对的大规模 RNA 辅助数据、质谱蛋白缺失、时间与剂量，以及对蛋白组泛化增益的严格因果消融。

## 局限与对比时需要注意的条件

这里的蛋白主要是抗体衍生标签 ADT，尤其细胞表面蛋白，不是覆盖数千蛋白的质谱全蛋白组。主模型输入包含多组学对照信息；是否能在完全非配对训练及只给蛋白对照时运行，不能从对抗对齐这一点直接推断。

## 复现与接入建议

先读 Fig. 1、Methods 的 integrative training 与数据划分；再审查 GEARS 扰动嵌入是否严格只使用训练响应，避免外部嵌入带入测试标签。移植到质谱时重写观测模型与缺失掩码。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1371/journal.pcbi.1014054](https://doi.org/10.1371/journal.pcbi.1014054)
- [https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014054](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014054)
- [https://github.com/MengyuanZhaoo/MultiPert](https://github.com/MengyuanZhaoo/MultiPert)
- 实际 PDF 来源：[下载地址](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014054&type=printable)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
