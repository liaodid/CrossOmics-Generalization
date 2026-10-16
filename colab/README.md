# colab/：探索性 Notebook

放在 Google Colab 上运行的探索性 notebook。
成熟、需要反复运行的逻辑应整理成 `script/` 中的脚本。

约定：

- 文件开头写清目的、数据来源、运行环境，以及输出保存在哪里。
- 输出若存放在个人 Google Drive，要在本 README 中注明路径；其他成员无法直接访问，关键结论需另外记录到 [docs/findings.md](../docs/findings.md)。
- 提交前保留关键单元的输出，便于不运行也能看到结果。

上游论文的作图 notebook 不在这里，而在 `baseline/unipert-g2cp/analysis_assets/`。
它们通过 `../UniPert/...` 这样的相对路径读取文件，必须与上游代码放在一起。

## Notebook 清单

| Notebook | 目的 | 结果 | 输出位置 |
|---|---|---|---|
| [hepg2_alignment_drive.ipynb](hepg2_alignment_drive.ipynb) | 为 HepG2 的药物扰动蛋白组（MSV000101671）寻找同细胞、同药、同剂量、同时长的转录组数据，并做基因层面的 RNA‑蛋白对齐 | **对齐的基因行数为 0**：GSE51952 没有可用配对，LINCS Phase I 按药名匹配为 0；之后的 RNA 差异计算、蛋白统计下载和基因映射都没有执行 | 作者的 Google Drive：`MyDrive/virtualcell_hepg2_alignment_v1/` |
| [ptds_unipert_lincs_alignment_drive.ipynb](ptds_unipert_lincs_alignment_drive.ipynb) | 从 UniPert-G2CP 作者 LINCS 子集中提取与 PTDS 同细胞系、同药物的表达签名；剂量和时间不参与筛选 | 2026-10-16 本地验证：MCF7、20 种 PTDS 药物、21 个 BRD 条目、200 条 RNA 签名；另有 1 个药物名称待复核。尚未在用户 Colab 中执行 | `MyDrive/virtualcell_ptds_unipert_alignment_v1/` |
| [ptds_tahoe100m_alignment_drive.ipynb](ptds_tahoe100m_alignment_drive.ipynb) | 从 Tahoe-100M 提取与完整 PTDS 样本表同细胞系、同药物的单细胞原始 counts；剂量不限制 | 已验证官方真实数据块的格式、筛选、CLS 去除、checkpoint 与 pseudobulk 汇总；尚未全量扫描，不预填实际交集 | `MyDrive/virtualcell_ptds_tahoe_alignment_v1/` |

### PTDS 与 Tahoe-100M 的提取流程

使用 CPU Colab，从上到下运行 `ptds_tahoe100m_alignment_drive.ipynb`，仅需输入 PTDS 的 `01_sample_info.xlsx`，不需要先下载 Tahoe 全集或上传蛋白强度矩阵。默认复用上一份 notebook 在 Drive 中的 PubChem 查询缓存。

- 固定 [官方 Hugging Face 数据集](https://huggingface.co/datasets/tahoebio/Tahoe-100M) 的 commit；下载四张小型元数据表。筛选范围是完整 PTDS，不限于 UniPert 的 MCF7 或 20 种药。
- 注释表中初筛为 BT20、DU4475、HCC1143、HS578T、MCF7 五个候选；最终以源表达记录中的 `(sample, cell_line_id)` 实际出现为准，不把元数据候选当作实际交集。
- 药物接受精确 PubChem CID 或标准化母体完整 InChIKey 匹配，逐条保存依据；仅连接骨架相同但立体信息不同的候选进入 `structure_match_review.csv`，不自动合并。`drug_candidate_coverage.csv` 记录每种 PTDS 药物在 Tahoe 注释中的候选数量。
- 通过 Parquet footer 的 sample min/max 筛选行组，再用元数据列做精确筛选，命中后才读取表达列。不依赖已经迁移的旧 Arc GCS 地址，也不使用预计算 DE 结果代替 raw counts。
- 默认保存筛选后的单细胞 Parquet 分片、逐细胞元数据及按 `sample + cell_line_id + plate` 求和的 `pseudobulk_raw_counts.h5ad`；保存所有匹配剂量，保留同 plate、同细胞系的 DMSO_TF 对照。
- 源数据共 3,388 个分片；筛选仍可能读取数 GB 至数十 GB，不能承诺只下载最终子集的字节数。每个分片有持久 checkpoint，可在 Colab 断开后续跑。设置 `SAVE_SINGLE_CELL=False` 可只保留 pseudobulk 和细胞元数据。
- 提取阶段默认 `EXTRACT_WORKERS=4`：有限并发、每线程独立 HTTP Session、可用时复用 CDN 下载地址；本地压缩/计算哈希后顺序复制每个文件到 Drive，避免在挂载盘上直接做压缩文件的随机写入。可以试 6 个并发；内存不足或频繁 429 时降至 2。不会自动扩大到全源分片下载。
- 可保留原 BASE、source revision 和 checkpoint；性能参数不改变匹配范围。中断后请等“提取线程已停止”再重跑，避免旧线程和新运行同时写同一分片。仍需完整扫描才能报告最终交集，不能用 `MAX_SHARDS` 缩小扫描范围来当作加速完成。
- `MAX_SHARDS=None` 为完整扫描；整数是试跑上限。失败分片和未扫描分片不会被当作无数据。最终 `scan_status.json` 只有在全扫描且校验通过后才标记 `complete=true`。
- 主要交付：`matched_conditions.csv`、`matched_pairs.csv`、`matched_ptds_samples.csv`、`condition_coverage.csv`、`pseudobulk_obs.csv`、`pseudobulk_control_pairs.csv`、原始计数 h5ad、单细胞分片及复核/错误报告。
- 本地使用官方首个行组的 1,000 条真实记录验证了 CLS 去除、非负整数 counts 检查、样本/细胞精确过滤、分片复用、计数守恒及 h5ad 读写；局部流程夹具不作为实际 PTDS 匹配结果报告。完整覆盖仍需在 Colab 执行扫描。

### PTDS 与 UniPert-G2CP 的提取流程

在 Colab 中上传并打开新 notebook，从上到下运行（CPU 即可）。先将 PTDS 的 `01_sample_info.xlsx` 放到配置的 Drive 路径，或使用首次运行时的上传框。无需上传蛋白强度矩阵。

- 数据来源：[作者 Zenodo 20355906](https://zenodo.org/records/20355906)，读取 `G2CP:data.zip` 中的 MCF7 化学扰动 h5ad 和化合物结构表；通过范围请求仅提取两个成员，压缩大小合计约 58 MB，不下载整个约 3.25 GB 压缩包。
- 已核对作者 MCF7 文件：11,138 行 × 978 基因，其中 11,137 条化学扰动记录和 1 条 `ctl_vehicle.cns` 对照；`condition=ctrl` 标识作者对照。LINCS 数据是处理后的 Level 5 表达签名，不是单细胞 counts。
- 药物匹配：PTDS 原名经 PubChem 查询结构，与作者 BRD 编号的结构比较；RDKit 标准化母体并保留立体化学。剂量和时间不参与匹配，但完整保留原始元数据。未解析、歧义和未匹配药物分别输出供复核。
- 主要输出：`matched_pairs.csv`、`matched_ptds_samples.csv`、`matched_rna_obs.csv`、`matched_rna_expression.csv`、`matched_rna_with_controls.h5ad`、`summary.json`。
- `matched_rna_expression.csv` 与 RNA 元数据按 `rna_row_index` 对齐；不生成跨组学样本的一一对应关系。最终未匹配不代表整个 LINCS 无该药，仅表示本作者 MCF7 子集及当前结构解析流程未匹配。
- 本地验证使用真实 PTDS 样本表和作者 MCF7 数据，成功执行结构匹配、CSV/h5ad 导出及 h5ad 重新读取，确认矩阵行序一致；盐型归并、立体异构体区分和不同母体区分检查通过。63 个 PTDS 名称中 62 个成功解析，`Verteporfin` 的 PubChem 名称查询返回 404，留待人工复核。当前 20 种是本轮保守结构匹配结果，不宣称完整交集。

### hepg2_alignment_drive.ipynb 的已知问题

- 只检查了 LINCS Phase I。Phase II 中 HepG2 在 24 h、10 µM 下有 268 种化合物，没有被检查。
- 药名精确匹配不去除盐型，蛋白组那边的药名（如 “Abemaciclib (methanesulfonate)”）几乎不可能对上 LINCS。
- 第 1 节的数据仓库读取失败，改用了 `jymbcrc/drug-portal`。2026‑10‑15 已核对：MassIVE 数据集的提交者账号名与它一致，基本可以确定是作者本人发布的处理结果。
- 这个 notebook 由 AI 工具生成，第 1 个单元中关于“未读到本地 PDF”等说明，描述的是生成时的工具环境。
