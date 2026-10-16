# Robotic perturbation proteomics：HepG2 深度质谱扰动数据来源

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Yuming Jiang; Cameron S. Movassaghi; Jesús Muñoz-Estrada; Niveda Sundararaman; Amanda Momenzadeh; Jesse G. Meyer. **Robotic perturbation proteomics and AI agents enable scalable drug mechanism discovery.** bioRxiv, 2026.
- DOI：[10.64898/2026.05.04.722718](https://doi.org/10.64898/2026.05.04.722718)
- 本地文件：[本地 PDF](../../pdf/robotic-proteomics.pdf)
- **实际下载版本：** bioRxiv 2026 v1，预印本。
- 下载稿标题：Robotic perturbation proteomics and AI agents enable scalable drug mechanism discovery。
- 下载稿 DOI：[10.64898/2026.05.04.722718](https://doi.org/10.64898/2026.05.04.722718)。
- 篇幅：21 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/xomicsdatascience/AI-robotics-proteomics
- 数据：MassIVE MSV000101671 ; https://zenodo.org/records/20499242

## 为什么值得优先阅读

它对应本项目已经关注的 MSV000101671，比一般虚拟细胞综述更能直接帮助准备蛋白组训练或外部验证数据。

## 方法概要

结合半自动样品制备、快速 LC-MS/MS 和 AI 辅助解释，对 HepG2 药物处理后的蛋白丰度变化开展机制分析。AI 部分用于分析与假设提出，不能直接视作未见药物表达预测模型。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 实验输入 | HepG2 与 172 种化合物 | 1,232 个蛋白组样本 |
| 蛋白测量 | LC-MS/MS | 超过 8,700 个定量蛋白 |
| 机制分析 | 差异蛋白和通路 | 机制总结及待验证假设 |

## 论文中的评价设置与结果解读

原文通过质控、药物响应与独立验证展示平台能力；这不是与你的模型相同的训练–测试基准。样本数量、蛋白覆盖和条件应以下载原文 Methods 及样本表为准。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 适合作为公开蛋白组数据，或在 ProteinTalks 数据不足时形成 HepG2 的独立问题。但既有项目对 RNA 对齐的探索没有找到严格配对条件，不能假设能直接拼成成对矩阵。

## 局限与对比时需要注意的条件

预印本尚未完成同行评审。细胞系、时间和剂量范围较集中，不能仅靠这一数据声称跨细胞泛化；药物重复必须整体保留在同一划分中。

## 复现与接入建议

下载处理后的蛋白强度与完整样本表，核对对照、批次、重复及给药条件；与 LINCS Phase I/II 按结构比较覆盖。可开展非配对多任务训练，但评价需要真实的蛋白标签。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.64898/2026.05.04.722718](https://doi.org/10.64898/2026.05.04.722718)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC13174343/](https://pmc.ncbi.nlm.nih.gov/articles/PMC13174343/)
- [https://www.biorxiv.org/content/10.64898/2026.05.04.722718v1](https://www.biorxiv.org/content/10.64898/2026.05.04.722718v1)
- 实际 PDF 来源：[下载地址](https://www.biorxiv.org/content/10.64898/2026.05.04.722718v1.full.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
