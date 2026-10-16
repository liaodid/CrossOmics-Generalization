# 参考文献

## 2026-10-15 首轮扩展阅读

已筛选 18 篇与项目最相关的论文，下载 16 篇可验证 PDF，并为全部 18 篇编写中文介绍（未取得 PDF 的两篇标为初步笔记）。
请先看 [阅读索引与创新性分析](literature/README.md)、[详细表格](literature.csv) 和 [手动下载清单](../pdf/MANUAL_DOWNLOADS.md)。
本次按项目成员要求，PDF 实际放在根目录 `pdf/`；下文 `docs/papers/` 是早期目录约定，核心论文表中的旧文件名不是本次下载状态。
ProteinTalks、UniPert-G2CP、State、Tahoe-100M 当前获取的是作者预印本，totalVI 为作者接受稿；具体版本以新清单为准。

需要优先补读 [TransPro](literature/transpro.md) 和 [MultiPert](literature/multipert.md)：它们已经涉及 RNA 与蛋白组的扰动建模，不能笼统声称这类联合建模没有先例。

**论文清单以 [papers.csv](papers.csv) 为准**：一行一篇，列出方法名、标题、作者、年份、期刊、DOI、本地 PDF 文件名、
单位、组学、在项目中的角色、仓库内对应目录、代码和数据链接。可以直接用 Excel 或 pandas 打开。
本页是便于阅读的摘要。新增论文时先改 CSV，再视需要更新本页。

PDF 原约定放在本地的 `docs/papers/`，本次统一放在根目录 `pdf/`，出于版权和体积原因不提交到 Git（见 `.gitignore`）。
新成员按 DOI 自行下载到该目录，并按 CSV 中 `pdf_file` 列的名字保存。

## 核心论文

| # | 论文 | 期刊与 DOI | 本地 PDF | 在项目中的角色 |
|---|---|---|---|---|
| 1 | Li et al. **UniPert-G2CP bridges genetic and chemical screens from molecular representation to phenotype modeling.** 腾讯 AI for Life Sciences Lab、中南大学等 | Cell, 2026. https://doi.org/10.1016/j.cell.2026.06.005 | `1-s2.0-S0092867426006549-main.pdf` | [Baseline 1](../baseline/unipert-g2cp/README.md) |
| 2 | Sun, Qian, Li, Liu, …, Zhu, Guo. **An operational perturbation proteomics-based virtual cell model.** 西湖大学 | Nature, 2026. https://doi.org/10.1038/s41586-026-11001-9 | `s41586-026-11001-9.pdf` | [Baseline 2 / 主要对标对象](../baseline/proteintalks/README.md) |
| 3 | Adduri, Gautam, Bevilacqua, …, Goodarzi, Roohani. **Predicting cellular responses to perturbation across diverse contexts with State.** Arc Institute | Cell, 2026. https://doi.org/10.1016/j.cell.2026.07.052 | `PIIS0092867426009219.pdf` | 相关工作：单细胞转录组扰动预测 |
| 4 | Zhang, Ubas, Svensson, …, Goodarzi, Yu. **Tahoe-100M: Mapping drug-induced molecular phenotypes at single-cell resolution.** | Cell 189, 5945–5961, 2026. https://doi.org/10.1016/j.cell.2026.08.035 | `Zhang 等 - 2026 - Tahoe-100M ….pdf` | 候选数据：[data/tahoe-100m](../data/tahoe-100m/README.md) |
| 5 | Basu, Yu, …, Mülleder, Moreau, Ralser. **Proteome-guided drug discovery maps and mitigates therapeutic degrader toxicity.** | Nature Chemical Biology, 2026‑10‑09. https://doi.org/10.1038/s41589-026-02347-2 | 无 | 候选数据：[data/hepg2-degrader-proteome-basu2026](../data/hepg2-degrader-proteome-basu2026/README.md) |

## 数据相关

| 资源 | 链接 | 说明 |
|---|---|---|
| UniPert‑G2CP 数据与权重 | https://doi.org/10.5281/zenodo.20355906 | Baseline 1 复现所需 |
| UniPert‑G2CP 作者复现代码 | https://github.com/lynn-1998/UniPert-G2CP_reproduce | 本仓库 `baseline/unipert-g2cp/` 的来源 |
| UniPert 推理仓库 | https://github.com/TencentAILabHealthcare/UniPert | 只做推理时使用 |
| ProteinTalks 代码 | https://github.com/guomics-lab/PTV-1 | 尚未克隆 |
| State 代码 | https://github.com/ArcInstitute/state | — |
| HepG2 172 种药蛋白组：Robotic perturbation proteomics and AI agents enable scalable drug mechanism discovery（bioRxiv 2026，DOI 10.64898/2026.05.04.722718） | https://pmc.ncbi.nlm.nih.gov/articles/PMC13174343/ | 数据为 MassIVE MSV000101671 |
| LINCS 文件说明 | https://clue.io/connectopedia/category/Data | — |

## 方法学提醒

- Ahlmann‑Eltze, Huber, Anders. Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines.
  Nature Methods, 2025. https://doi.org/10.1038/s41592-025-02772-6 （标题与 DOI 经 Crossref 核对）
  结论是深度学习扰动预测模型尚未稳定胜过简单线性基线。设计评价协议时，应包含“预测均值”“预测对照”这类简单基线。
