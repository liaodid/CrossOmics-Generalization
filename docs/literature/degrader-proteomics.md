# Proteome-guided degrader toxicity：HepG2 蛋白组与分布外药物验证数据

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Shaon Basu; Jason Shu Lim Yu; Jessica Bosak; Sharan K. Bagal; Claire Crafter; Charlene Fallan; et al.. **Proteome-guided drug discovery maps and mitigates therapeutic degrader toxicity.** Nature Chemical Biology, 2026.
- DOI：[10.1038/s41589-026-02347-2](https://doi.org/10.1038/s41589-026-02347-2)
- 本地文件：[本地 PDF](../../pdf/degrader-proteomics.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：Proteome-guided drug discovery maps and mitigates therapeutic degrader toxicity。
- 下载稿 DOI：[10.1038/s41589-026-02347-2](https://doi.org/10.1038/s41589-026-02347-2)。
- 篇幅：37 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/Ralser-Lab/Proteomic-drug-discovery
- 数据：PRIDE PXD062492 ; https://doi.org/10.6084/m9.figshare.28578113

## 为什么值得优先阅读

它把质谱蛋白组与药物毒性联系起来，可帮助区分蛋白响应重建和功能表型预测，并提供不同化学空间的验证机会。

## 方法概要

先测量药物诱导的蛋白组变化，再以蛋白组训练机器学习模型关联毒性机制，分析双功能降解剂的脱靶效应，并通过结构优化及实验检验机制。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 已批准药物筛选 | HepG2 药物处理 | 蛋白丰度变化 |
| 降解剂筛选 | AR 双功能降解剂 | 蛋白响应、肝毒性与机制线索 |
| 预测模块 | 测得蛋白组特征 | 毒性相关表型 |

## 论文中的评价设置与结果解读

原文报告 78 种 FDA 批准药物的筛选以及一致定量的 3,331 个蛋白，并分析实验性降解剂。主要证据围绕毒性机制、复合物 I 和更安全类似物；不是从药物结构直接预测全蛋白组的标准成绩。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可把降解剂作为区别于常规小分子的外部测试，但应先确认编码器能处理其分子大小、靶点机制及结构特征。RNA 辅助学习是否对这种分布偏移仍有帮助，是有意义的实验问题。

## 局限与对比时需要注意的条件

蛋白覆盖低于另一个 HepG2 深度数据；交集评价和全覆盖评价应分开。以真实处理后蛋白为输入预测毒性，与仅给未处理蛋白预测响应是不同任务。

## 复现与接入建议

优先下载处理后矩阵和元数据，按化合物而不是孔位划分。把常规药物训练、降解剂测试明确标为外部化学域验证，并增加预测均值和结构近邻基线。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s41589-026-02347-2](https://doi.org/10.1038/s41589-026-02347-2)
- [https://www.nature.com/articles/s41589-026-02347-2](https://www.nature.com/articles/s41589-026-02347-2)
- 实际 PDF 来源：[下载地址](https://www.nature.com/articles/s41589-026-02347-2.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
