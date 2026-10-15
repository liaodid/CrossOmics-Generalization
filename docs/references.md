# 参考文献

PDF 放在本地的 `docs/papers/`，出于版权和体积原因不提交到 Git（见 `.gitignore`）。新成员按 DOI 自行下载到该目录，文件名与下表一致。

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

- Ahlmann‑Eltze, Huber, Anders（Nature Methods, 2025）比较了深度学习扰动预测模型与简单线性基线，发现前者尚未稳定胜出。
  设计评价协议时应包含“预测均值”“预测对照”这类简单基线。（本仓库未存 PDF，引用前请核对原文。）
