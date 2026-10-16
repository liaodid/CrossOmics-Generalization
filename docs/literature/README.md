# 与 CrossOmics-Generalization 最相关的 18 篇论文

检索与整理日期：2026-10-15。已验证下载 **16/18 篇 PDF**；每篇均有单独中文介绍，未下载条目也提供初步解读及手动入口。

## 选文依据

项目目标是用转录组与蛋白组扰动数据联合训练，改善蛋白组响应泛化。先选择直接跨组学先例与 ProteinTalks/UniPert-G2CP，再补充药物泛化、公开蛋白/RNA 数据和评价方法；不是按引用量排列。

P0：先读，影响创新性与主实验；P1：建模、数据或评估的重要参考；P2：方法基础。列表已包括仓库原先登记的核心文献，而非声称 18 篇都是新发现。

远端 GitHub 连接器与匿名原始文件入口返回 404；通过已配置 Git 凭据查询到远端 HEAD 为 `6464fb0aac7084a5df2ff01e4709b3430c00d772`，与读取时的本地 HEAD 一致。项目判断依据该版本本地 README、findings、数据文档和 ProteinTalks baseline。没有把远端读取失败写成已成功读取网页。

## 阅读索引

| 顺序 | 优先级 | 方法 / 论文介绍 | 本项目中的角色 | PDF | 实际保存版本 |
|---|---|---|---|---|---|
| 1 | P0 | [TransPro](transpro.md) | 最直接的跨组学药物扰动先例与候选基线 | 需手动下载 | 待手动获取 |
| 2 | P0 | [MultiPert](multipert.md) | 直接的 RNA–蛋白多组学扰动预测先例 | 已下载 | 出版社论文版本 |
| 3 | P0 | [ProteinTalks](proteintalks.md) | 本项目既定的蛋白组主要对标对象 | 已下载 | bioRxiv 2025 v1；不是 Nature 2026 正式版 |
| 4 | P0 | [UniPert-G2CP](unipert-g2cp.md) | 本地已有源码的扰动编码和迁移学习基线 | 已下载 | bioRxiv 2025 v2；不是 Cell 2026 正式版 |
| 5 | P1 | [State](state.md) | 跨细胞背景泛化与评价方法参考 | 已下载 | bioRxiv 2025 v1；不是 Cell 2026 正式版 |
| 6 | P1 | [Tahoe-100M](tahoe-100m.md) | 大规模药物转录组辅助训练数据 | 已下载 | bioRxiv 2025 v2；不是 Cell 2026 正式版 |
| 7 | P1 | [Robotic perturbation proteomics](robotic-proteomics.md) | HepG2 深度质谱扰动数据来源 | 已下载 | bioRxiv 2026 v1，预印本 |
| 8 | P1 | [Proteome-guided degrader toxicity](degrader-proteomics.md) | HepG2 蛋白组与分布外药物验证数据 | 已下载 | 出版社论文版本 |
| 9 | P0 | [Linear baselines benchmark](linear-baselines.md) | 实验可信度与简单强基线设计 | 已下载 | 出版社论文版本 |
| 10 | P1 | [XPert](xpert.md) | 药物、细胞背景和时间剂量泛化方法 | 已下载 | 出版社论文版本 |
| 11 | P1 | [PerturbNet](perturbnet.md) | 未见化学及遗传扰动的分布预测基线 | 已下载 | 出版社论文版本 |
| 12 | P0 | [chemCPA](chemcpa.md) | RNA 大数据迁移与未见药物预测的关键先例 | 已下载 | NeurIPS 2022 会议论文 |
| 13 | P2 | [CPA](cpa.md) | 可组合扰动表示与解耦学习基础方法 | 已下载 | 出版社论文版本 |
| 14 | P1 | [GEARS](gears.md) | 本地 G2CP 骨干和遗传扰动知识图基线 | 已下载 | 出版社论文版本 |
| 15 | P2 | [biolord](biolord.md) | 细胞背景与扰动因素解耦的候选基线 | 已下载 | 出版社论文版本 |
| 16 | P2 | [totalVI](totalvi.md) | RNA 与蛋白联合概率建模基础 | 已下载 | 作者接受稿，由 UC eScholarship 存储；对应 Nature Methods 2021 正式论文 |
| 17 | P1 | [MultiVI](multivi.md) | 不完整模态与部分配对数据整合方法 | 已下载 | 出版社论文版本 |
| 18 | P1 | [L1000 / Connectivity Map](l1000.md) | 当前 LINCS RNA 数据与处理层级的原始来源 | 需手动下载 | 待手动获取 |

## 对论文定位的直接影响

1. **TransPro 已涉及从转录组到药物诱导蛋白组及表型的建模**；[作者仓库](https://github.com/XieResearchGroup/TransPro)提供含扰动 RNA 辅助数据的训练设置。不能笼统声称首次联合 RNA 与蛋白预测药物响应。
2. **MultiPert 已联合预测 RNA 与蛋白扰动响应**，但主要蛋白读出是 ADT 表面蛋白，且与本项目的小分子质谱场景不同。参见[原论文](https://doi.org/10.1371/journal.pcbi.1014054)。
3. **ProteinTalks 正式版还探索了由蛋白预训练迁移至 PDX 转录组**，见[正式版扩展数据图 8](https://www.nature.com/articles/s41586-026-11001-9)。主训练数据以蛋白为主，与“完全没有跨组学探索”不是同一断言。
4. 更合适的候选研究问题是：**非严格配对的大规模 RNA 辅助监督，是否在同样的蛋白数据和预算下，提高质谱蛋白组对未见药物、未见骨架或新细胞背景的泛化？** 这是本次检索后的建议，尚待数据和实验证明，也不构成穷尽性新颖性检索结论。

## 建议的最小对比

| 比较 | 要回答的问题 |
|---|---|
| 对照不变、训练平均变化、结构特征岭回归 | 是否优于简单强基线？ |
| 同架构蛋白组单任务 | RNA 辅助数据是否有增益？ |
| RNA 预训练后蛋白微调 | 同步联合训练是否必要？ |
| RNA/蛋白联合训练 | 主设想是否成立？ |
| TransPro、ProteinTalks 及适配后的 MultiPert | 相比已有直接先例有何改进？ |

按药物及结构骨架隔离重复；细胞背景泛化单列；报告 Δ 蛋白相关性、MSE、方向与差异蛋白恢复。药效分类另报 AUROC/AUPRC，不能与表达重建混成一个结论。用于验证的特征集合与预处理不能由测试标签决定。

RNA 中若出现蛋白测试药物，应明确称为跨模态标签迁移设置；若声称全新药物外推，则应从各组学训练数据中隔离这些药物。非配对的双 head 在工程上能训练，但是否能有效迁移取决于共同扰动、细胞背景、先验或桥接样本，不能保证可辨识性。

## 文件与版本说明

- PDF 在根目录 `pdf/`，与用户指定一致；中文介绍在 `docs/literature/`，仿照 ProteinTalks baseline 的结构，而不是把所有相关工作都当成已经安装的 baseline。
- [18 篇详细表格](../literature.csv)包括版本、DOI、介绍路径及下载状态；[下载清单](../../pdf/download_manifest.json)包含页数、大小、SHA-256 和来源。
- [手动下载清单](../../pdf/MANUAL_DOWNLOADS.md)包含尚缺 PDF 和仅获取预印本的正式版。
- 成功仅表示文件以 PDF 魔数开头、可解析页数与正文且人工核对了首页论文身份，不代表完成全文精读或模型复现。
- 不覆盖既有 baseline，不提交或推送 Git；PDF 被 `.gitignore` 排除。
