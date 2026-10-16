# 已核实的事实、结论与待定事项

按主题记录对项目有影响的事实。每条注明日期、来源和可信度，未核实的内容会明确标出。
新结论请追加到对应小节，不要删除旧记录；若旧结论被推翻，在原条目后注明。

---

## 1. 项目目标（2026‑10‑15，来自项目成员的口头说明）

- 现有扰动响应模型要么只用转录组数据训练（如 UniPert‑G2CP、State、Geneformer 类基础模型），要么只用蛋白组（如 ProteinTalks）。
- 设想：用一个**共享扰动编码器 + 转录组 head + 蛋白组 head** 的多任务模型，同时在两种组学数据上训练，
  以提升模型的鲁棒性和泛化性。
- 对标对象是“西湖的那篇文章”，目标是在蛋白组任务上超过它。
- 实验室没有自产数据，也不打算做湿实验，只使用公开数据。
- “没有人做过两种组学联合训练”目前**没有经过系统文献检索**。

## 2. “西湖那篇”就是 ProteinTalks（2026‑10‑15，项目成员已确认）

- 起初是推断：`docs/papers/` 中只有 Sun et al.（Nature 2026）来自西湖大学，而且正是纯蛋白组的虚拟细胞模型。2026‑10‑15 项目成员确认无误。
- UniPert‑G2CP 的作者单位是腾讯和中南大学等，与西湖大学无关，而且它不预测蛋白组。
- 详见 [baseline/proteintalks](../baseline/proteintalks/README.md)。

## 3. Baseline 1（UniPert‑G2CP）代码层面的事实（2026‑10‑15，读代码核实）

路径相对于 `baseline/unipert-g2cp/`。

- **UniPert 的两侧编码器：**
  - 蛋白侧：ESM2 序列 embedding，在 MMseqs2 序列相似度图上跑 GCN，用 BGRL 自监督训练。
  - 化合物侧：ECFP4 指纹后只接一层线性层（`UniPert/unipert/modules.py:194`）。
- **对比学习的方向：** 第二阶段做化合物‑靶点对比学习时，靶点特征在 `torch.no_grad()` 下计算（`UniPert/unipert/model.py:544`），
  因此对比损失只训练化合物侧，实际效果是把化合物映射进蛋白表示空间。
- **温度参数没有被学习：** `CTCLoss` 的 `logit_scale` 写成 `nn.Parameter(...).exp()`（`UniPert/unipert/ctcloss.py:13`），
  结果是普通张量而不是可训练参数，所以温度固定为 1/0.07。
- **G2CP 的输入与输出：**
  - 输入：一条对照表达谱，加上扰动的 256 维 UniPert 向量（`G2CP/backbone_model/GEARS/gears/model.py:62`）。
  - 输出：对照谱加上预测的变化量（残差结构，同文件第 188 行）。
- **训练流程：** 先在 CRISPR 敲除（`trt_xpr`）上预训练，再在部分药物（`trt_cp`）上微调，最后在未见过的药物上测试。
  数据按扰动划分，不按样本划分。
- **论文内部的两个基线：**
  - `no-perturb`：直接输出对照谱。
  - `ground-truth`：同一扰动的重复样本之间的相似度，作为可达上限。
- **评价指标的坑：** `compute_metrics`（`G2CP/backbone_model/GEARS/gears/inference.py:53`）计算的是预测与真实**整体表达谱**之间的 Pearson、Spearman 和 MSE。
  加药前后的整体谱本来就高度相似，这个指标偏乐观，应同时看变化量（Δ）的相关性。
- **一个没有用到的参数：** `train_G2CP_*.py` 中的 `--unipert_model_dir` 参数解析后从未使用；UniPert 向量直接从数据文件的 `adata.uns['UniPert_reps']` 读取。
- **写死的路径：** 代码中有 96 处作者机器上的绝对路径（`/data/liyiming/...`、`/fionafyang/...`）。
- **实验规模：** `G2CP/run_scripts/run_LINCS_cpf_exps.sh` 会用 `nohup` 起 3×5×5×11×9 = 7,425 个后台任务，在集群上必须改成 Slurm 作业阵列。

## 4. LINCS 中的细胞系覆盖（2026‑10‑15，`script/audit_lincs_metadata.sh`）

- CRISPR 敲除只有 Phase II（GSE70138）有，细胞系为 A375、A549、HA1E、HELA、HT29、MCF7、PC3、YAPC。**HepG2 没有。**
- HepG2 的化合物签名：
  - Phase I：5,774 条；其中 24 h、10 µM 的有 199 条，涉及 176 种化合物。
  - Phase II：1,775 条；其中 24 h、10 µM 的有 305 条，涉及 268 种化合物。
- HepG2 的遗传扰动只有 shRNA 敲低（Phase I，`trt_sh` 12,868 条）。
- 详见 [data/lincs-l1000](../data/lincs-l1000/README.md)。

## 5. HepG2 RNA‑蛋白对齐的探索结果（2026‑10‑15，读 notebook 输出核实）

- [colab/hepg2_alignment_drive.ipynb](../colab/hepg2_alignment_drive.ipynb) 最终**对齐的基因行数为 0**。
  基因层面的对齐代码写好了，但从未执行。
- 原因：两边找不到同细胞、同药、同剂量、同时长的条件。
  - GSE51952 与蛋白组只对上 Tolbutamide 一个药，剂量还不同（2,000 µM 对 10 µM）。
  - LINCS Phase I 按药名匹配为 0。
- “LINCS 为 0”**不是最终结论**：notebook 没有检查 Phase II，而且按药名精确匹配时没有处理盐型。
  抽查的 5 个蛋白组药物中，只有 Tolbutamide 出现在 LINCS 的 HepG2 数据里（Phase I，6 h）。真实重叠可能确实很少。

## 6. 关于配对数据的判断（2026‑10‑15，讨论结论）

- 多任务训练**不需要**两种组学在同一药物上配对：两个 head 各自用自己的数据训练，药物编码器共享即可。
  例如 UniPert 只需要分子结构就能给任意药物生成向量。
- 严格配对数据只在回答“同一扰动下 RNA 变化与蛋白变化是否一致”这类分析问题时才需要。
- 细胞系最好一致。A375（ProteinTalks 的 PTPC 子集与 LINCS 都有，且 LINCS 有其 CRISPR 数据）是目前最现实的候选；
  MCF7 已由 PTDS 样本表确认属于 PTDS（见第 11 节），是另一个重要候选。HepG2 缺少 CRISPR 数据和配对条件，不适合作为主线。

## 7. MSV000101671 的来源已核实（2026‑10‑15，MassIVE 与 Europe PMC）

- MassIVE MSV000101671 来自 Cedars‑Sinai 的 Meyer 实验室，仪器为 Orbitrap Astral，状态为 Partial Public，许可证 CC0。
- 对应预印本：Robotic perturbation proteomics and AI agents enable scalable drug mechanism discovery（bioRxiv 2026）。
  摘要给出的规模：HepG2，172 种化合物，1,232 个蛋白组样本，定量蛋白超过 8,700 个。
- MassIVE 上的提交者账号名与 GitHub `jymbcrc` 一致，所以 notebook 用到的 `jymbcrc/drug-portal` 基本可以确定是作者本人发布的处理结果。
- “24 h、10 µM、每种药 6 个重复”尚未对照原文 Methods 核实。
- 详见 [data/hepg2-drug-proteome-msv000101671](../data/hepg2-drug-proteome-msv000101671/README.md)。

## 8. ProteinTalks：代码已公开，训练数据还没拿到（2026‑10‑15）

- 项目成员说明：西湖作者那边代码可以拿到，训练数据集还没拿到。
- 公开代码：GitHub `guomics-lab/PTV-1`，核对时的最新提交为 `1223e94`，模型目录下的许可证为 MIT。
  - `ProteinTalks/` 中有完整的模型、训练、评价代码，还有一个训练好的 checkpoint（`best_checkpoint.pth`）。
  - 根目录有 4 个 R 分析脚本：分子指纹计算、差异分析、PertScore、Mfuzz 聚类。
- 代码层面的事实（读 `ProteinTalks/README.md` 核对）：
  - 输入：加药前的蛋白组、一个“与蛋白对齐的扰动描述”、两种药物的分子特征向量（881 维指纹 + 54 维理化性质，由 `ChemmineR.R` 生成）。
  - 用神经 ODE 预测 6、24、48 h 的蛋白组，再由一个表型 head 预测药效或药物组合协同的概率。
  - **ProteinTalks 本身已经是多任务模型**：损失 = (1 − λ) × 蛋白表达 MSE + λ × 表型 BCE，默认 λ = 0.8。
    本项目若提出“多 head 联合训练”，要明确新意在于“加入转录组数据”，而不是“多任务”本身。
  - 训练数据是同一前缀的 7 个 CSV 文件，格式见 [data/proteintalks](../data/proteintalks/README.md)。
- 详见 [baseline/proteintalks](../baseline/proteintalks/README.md)。

## 9. ProteinTalks 的细胞系与 LINCS 的重合（2026‑10‑15，`script/lincs_cell_line_coverage.sh`）

ProteinTalks 有三个蛋白组子数据集：PTDS（主数据集）、mtPTDS（多时间点）、PTPC（跨癌种），各自的说明见 [data/proteintalks](../data/proteintalks/README.md)。
论文中出现的细胞系，在 LINCS 中的签名数如下：

| 细胞系 | 属于 | LINCS 化合物签名（Phase I / II） | LINCS CRISPR | LINCS shRNA |
|---|---|---|---|---|
| **A375** | PTPC | 15,453 / 12,050 | 353 | 14,800 |
| **MCF7** | PTDS（2026‑10‑16 由 PTDS 样本表确认，见第 11 节） | 29,312 / 12,737 | 705（2 批） | 19,669 |
| BT20、HS578T、MDA‑MB‑231 | 论文正文提到（乳腺癌） | 各约 1,400 / 1,400 | 无 | 无 |
| HCT116 | PTPC | 363 / 0 | 无 | 无 |

其余 15 个（NCI‑H1975、NCI‑H2170、Panc 10.05、T47D、BT549、MDA‑MB‑436/453/468、HCC 系列）在 LINCS 中按常见命名都没找到。

**结论：A375 是目前最现实的联合训练起点**：ProteinTalks 有它的蛋白组（PTPC，708 种化合物），LINCS 有它的大量转录组和 CRISPR 数据。
MCF7 已确认在 PTDS 里，是第二个候选。按化学结构核对 MCF7 两边化合物重合的结果见第 11 节。

---

## 10. 首轮相关文献检索：已存在跨组学扰动建模先例（2026-10-15）

- **TransPro（Cell Reports Methods, 2023）**已有转录组与蛋白组解码器、RNA 到蛋白隐空间的 transmitter，以及药物响应预测；作者仓库还提供利用扰动 RNA 数据训练的设置。来源：[论文](https://doi.org/10.1016/j.crmeth.2023.100452)、[作者仓库](https://github.com/XieResearchGroup/TransPro)。它是本项目需要首先比较的直接先例。本次未成功下载该文 PDF，初步介绍依据公开 HTML 正文和作者代码说明，尚未运行方法。
- **MultiPert（PLOS Computational Biology, 2026）**联合预测扰动后的 RNA 与蛋白，包含共享编码、模态专用解码、对抗对齐和注意力。其蛋白主要为 ADT 表面蛋白，不等同于质谱全蛋白组；遗传扰动与本项目的小分子条件也需区分。来源：[论文](https://doi.org/10.1371/journal.pcbi.1014054)。本次已下载并核对正文。
- **ProteinTalks 的主训练以蛋白组为主，但正式版并非没有跨组学迁移探索**：扩展数据图 8 描述蛋白组预训练后以 PDX 转录组微调。来源：[Nature 正式版](https://www.nature.com/articles/s41586-026-11001-9)。因此第 1 节的早期研究动机不能作为“跨组学联合建模从未有人做过”的结论。
- 建议将候选创新点收窄为：**非严格配对 RNA 辅助监督能否在相同蛋白训练数据与预算下，提升质谱蛋白响应的未见药物/骨架或细胞背景泛化**。这是研究建议，尚需核查更全面文献并完成实验。
- 共整理 18 篇论文，16 篇 PDF 已保存在根目录 `pdf/`，逐篇介绍见 [阅读索引](literature/README.md)。四篇核心论文仅下载到预印本，具体版本与缺失 PDF 见 [手动下载清单](../pdf/MANUAL_DOWNLOADS.md)。本次没有运行模型或生成性能结果。

## 11. PTDS × LINCS（MCF7）的药物对齐（2026‑10‑16，项目成员）

结果在 [reports/ptds-unipert-2026-10-16/](../reports/ptds-unipert-2026-10-16/)，由 [colab/ptds_unipert_lincs_alignment_drive.ipynb](../colab/ptds_unipert_lincs_alignment_drive.ipynb) 生成，方法见 [colab/README.md](../colab/README.md)。

- **数据：**
  - 蛋白侧：PTDS 样本表 `01_sample_info.xlsx`（只用了样本表，没有用蛋白强度矩阵）。
  - RNA 侧：UniPert‑G2CP 作者在 Zenodo 发布的 MCF7 LINCS 子集，11,138 条签名 × 978 个基因。
- **MCF7 确实在 PTDS 中**：这关闭了第 6、9 节里“需查补充表 1a”的疑问。
- **药物解析：** PTDS 共 63 种药，其中 62 种通过 PubChem 名称查询得到结构；`Verteporfin` 查询返回 404，待人工复核。
- **按标准化母体 InChIKey 匹配**（会自动处理盐型和水合物，例如 “Lapatinib Ditosylate Hydrate”）：
  - **20 种药物**两边都有，对应 21 个 LINCS BRD 编号（Lapatinib 有 2 个）。
  - 涉及 **200 条 RNA 签名**和 **174 个 PTDS MCF7 样本**；每种药 8–9 个蛋白样本，即 3 个时间点 × 3 个重复。
  - 每种药的 RNA 签名数从 1 条到 92 条不等（Vorinostat 92 条）。
- **剂量和时间没有参与筛选**。这是“同细胞、同药物”的条件级重合，不是同剂量、同时间的严格配对。
- 并行的 [Tahoe‑100M 对齐 notebook](../colab/ptds_tahoe100m_alignment_drive.ipynb) 流程已在样例数据上验证，但尚未完整扫描，没有交集结果。

结论：MCF7 上有 20 种药同时具备 RNA（LINCS）和蛋白（PTDS）数据。结合 PTPC 中的 A375，非严格配对的联合训练在两个细胞系上都有数据基础。

## 待定事项

| # | 问题 | 负责人 | 状态 |
|---|---|---|---|
| 1 | 确认“西湖那篇”就是 ProteinTalks | 项目成员 | ✅ 已确认（2026‑10‑15） |
| 2 | 定义任务与指标：比药效预测（AUPRC/AUROC）、蛋白组变化预测（Δ 的相关性），还是两者都比？在哪个测试集上比？ | — | 未定 |
| 3 | 获取 ProteinTalks 训练数据（向西湖作者索取，或通过 iProX IPX0007409000 / db.prottalks.com）。代码已公开，见第 8 节 | 项目成员 | 进行中：代码可得，数据未拿到 |
| 4 | 系统文献检索：是否已有联合转录组与蛋白组扰动数据训练的模型 | — | 首轮 18 篇已整理：存在 TransPro、MultiPert 等先例，见第 10 节；仍需针对具体数据与任务补查 |
| 5 | 选定主线细胞系（A375 / MCF7 / 其他），并核对两种组学的药物与剂量覆盖 | — | 进行中：细胞系重合已核对（第 9 节）；MCF7 有 20 种药两边都有（第 11 节）；A375 待拿到 PTPC 药物列表后核对；剂量和时间的匹配情况未核对 |
| 6 | 数据划分策略：按药物 k 折；结构类似物要按分子骨架划分 | — | 未定 |
| 7 | 数据量不平衡的处理：损失加权、均衡采样、先预训练再微调，或按相关性筛选数据 | — | 未定 |
| 8 | 项目自有代码与文档的许可证 | 项目成员 | 现阶段不考虑（2026‑10‑15 决定） |

## 讨论中提出的最小实验设计（草案，未采纳）

固定测试协议：蛋白组数据按药物做 k 折交叉验证，指标为每种药蛋白变化量的 Pearson 相关，重复多个随机种子。

| 编号 | 模型 | 作用 |
|---|---|---|
| A | 预测训练集所有药物的平均响应 | 最简单的基线 |
| B | 只用蛋白组训练的模型（ProteinTalks，或把 G2CP 的输出换成蛋白组） | 对标基线 |
| C | 共享编码器 + 转录组 head + 蛋白组 head，联合训练 | 本项目方法 |
| D | 先在转录组上预训练，再在蛋白组上微调 | 迁移学习变体 |

只有当 C 或 D 稳定优于 B、且 B 优于 A 时，“联合训练提升泛化性”的结论才成立。
