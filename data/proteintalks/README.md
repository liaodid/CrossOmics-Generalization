# ProteinTalks 扰动蛋白组数据（西湖大学）

## 是什么

西湖大学郭天南组为训练蛋白组虚拟细胞模型 ProteinTalks 产生的大规模药物扰动蛋白组数据（DIA 质谱）。
这是本项目对标对象 [baseline/proteintalks](../../baseline/proteintalks/README.md) 使用的数据。

## 子数据集

论文里有三个有名字的蛋白组数据集，各建了一个子目录：

| 子目录 | 细胞系 | 扰动 | 时间点 | 样本规模 | 论文中的用途 |
|---|---|---|---|---|---|
| [ptds/](ptds/README.md) | 18 个乳腺癌系 | 63 种 FDA 药 + 59 种组合 | 6 / 24 / 48 h | 16,311 个质谱文件 | 主训练数据 |
| [mtptds/](mtptds/README.md) | 3 个三阴性乳腺癌系 | 55 种单药 + 57 种组合 | 11 个时间点（0–60 h） | 2,528 个样本 | 时间动态与时间点选择 |
| [ptpc/](ptpc/README.md) | 5 个非乳腺癌系，含 **A375** | 708 种化合物 | 6 / 24 h | 2,307 个样本 | 跨癌种迁移验证 |

论文里还有一个 **PTNC**：4 个三阴性乳腺癌系（BT549、HCC1806、HS578T、MDA‑MB‑468）× 81 种抗癌化合物，
得到 2,076 条药物剂量反应测量（对应 173 个高置信度的药物‑细胞系组合），用作新药物的独立测试。
它主要提供药效标签，暂不单独建目录。

## 来源与获取

- 论文：Sun, Qian, Li, Liu, …, Zhu, Guo. An operational perturbation proteomics-based virtual cell model. Nature, 2026.
  https://doi.org/10.1038/s41586-026-11001-9
- 原始质谱数据：ProteomeXchange / iProX，项目编号 **IPX0007409000**
- PTDS 蛋白矩阵及相关资源：https://db.prottalks.com （论文称供学术、非商业用途使用）
- 论文的 Reporting Summary 另写有 “Data are available upon request for non-commercial purposes”。

## 状态

⏳ 待获取。截至 2026‑10‑15：模型代码已公开（见 [baseline/proteintalks](../../baseline/proteintalks/README.md)），训练数据还没拿到，项目成员正在与西湖作者联系。

拿到数据后：
- 整个 iProX 项目或作者打包的原始文件放本目录的 `raw/`；
- 各子集整理好的数据放对应子目录的 `processed/`；
- 在本 README 中登记下载日期、来源（公开下载，还是作者直接提供）、文件清单、SHA256，以及使用限制。

## 代码需要的输入格式

依据 `guomics-lab/PTV-1@1223e94` 中的 `ProteinTalks/README.md` 和 `ProteinTalks/dataset.py`（2026‑10‑15 核对）。

同一个前缀（如 `allcelltype_drugpair_crossdrug_`）对应 7 个 CSV 文件，**都没有表头，并且按行一一对应**：
第 i 行在每个文件里描述的都是同一个“实验 × 时间点”。

| 文件 | 每行的内容 |
|---|---|
| `<prefix>loo_label.csv` | 第 1 列是实验 ID（必须含 `#`，第一个 `_` 之前的部分是细胞系名）；第 2 列是时间点（0、6、24 或 48） |
| `<prefix>expr.csv` | 这一行的蛋白表达向量 |
| `<prefix>drug_fp_phychem_A.csv` | 药物 A 的特征，单元格是列表字符串：881 维分子指纹 + 54 维理化性质，共 935 维 |
| `<prefix>drug_fp_phychem_B.csv` | 药物 B 的特征，格式同上，用于药物组合 |
| `<prefix>pert.csv` | 与蛋白对齐的扰动描述向量，每个实验取第一行 |
| `<prefix>pheno.csv` | 药效或协同标签（一个数），每个实验取第一行；缺失值按 0 处理 |
| `<prefix>node_Index.csv` | 读入但在 `dataset.py` 中没有用到，可能是蛋白列表 |

模型的输入是该细胞系 0 h 那一行的表达，预测目标是该实验 6、24、48 h 三行的表达。
只有三个时间点都齐全的实验才会被使用。
