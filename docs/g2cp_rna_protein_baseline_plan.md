# G2CP 转录组基线与 RNA 到蛋白组迁移

核查日期：2026-10-21。依据本地代码和用户已下载数据。本文是输入接口核查和实验设计，尚未执行模型训练。

## 1. 已核实的数据与当前缺口

- Tahoe 本地目录：`results/parts_946c2dde4ebaa65b-20261020T124048Z-1-001/parts_946c2dde4ebaa65b/`。
- 3,308 组分片，每组有 `.cells.parquet`、`.counts.parquet`、`.pb.csv`、`.pb.npz`，没有发现这四类伴随文件缺失。
- `.pb.npz` 的特征数均为 62,710，行数与各自 `.pb.csv` 一致。检查了稀疏 data 数值有限性，未做完整生物学 QC 或文件哈希验证。
- 根据全部 `.pb.csv` 汇总，选中 161,217 个细胞，119 个唯一 `(sample, cell_line_id, plate)` 组，仅一个细胞系 `CVCL_0332`。它是 HS578T，见 https://www.cellosaurus.org/CVCL_0332 。这些不是 119 种药物。
- 合并后每组 1–4,394 个细胞，其中一组仅有 1 个细胞，需作为低覆盖组检查。不能把来源文件数当成生物学重复数。
- 3,388 个源分片编号中有 80 个编号没有本地 pb 文件，可能本就没有命中目标。未取得 `scan_status.json` 前，不能断言下载缺失，也不能断言完整扫描成功。
- 本地 `results/` 下未发现这次 Tahoe 的 `genes.csv`、`matched_conditions.csv`、`pseudobulk_control_pairs.csv`、`pseudobulk_raw_counts.h5ad` 和 `scan_status.json`。
- `results/unipert-g2cp_ptds/results/` 是另一批 MCF7/LINCS 对齐结果，不能拿其中的基因顺序、条件标签替代 HS578T/Tahoe。
- 蛋白表 `baseline/proteintalks/02_protein_intensity_matrix.xlsx`：331,411,929 bytes，工作表范围 `A1:XCK5586`，两列注释 `uniprotID`、`geneName`，其余 16,311 列样本、5,585 行蛋白群组。这里只读取了表范围及前几行，未逐个检查全部丰度值。
- 蛋白表前几行包含空值、文本数值（如带前导空格的强度）和数字/字符串混合的样本 ID。应显式转换数值和保留缺失掩码。
- `01_sample_info.xlsx` 有 15,073 条数据记录，HS578T 813 条，其中 single 545、combo 268。single 内含 `Pert_Name1=no` 的 41 条对照，不能把 545 都称为给药样本；对照时间为 6/24/48 h。这里的记录数尚未逐一与丰度列取交集，也未验证这些对照均可用于某个具体处理样本。

机器可读记录：`reports/g2cp_input_audit_2026-10-21.json`。

## 2. 当前代码真正接收什么

代码位置：

- `baseline/unipert-g2cp/G2CP/backbone_model/GEARS/gears/pertdata.py`：输入和配对。
- 同目录 `model.py`：张量与模型。
- 同目录 `gears.py`：初始化、图构建和权重加载。
- `baseline/unipert-g2cp/G2CP/train_G2CP_cpf.py`：作者训练入口。

UniPert 使用分子结构、蛋白靶点序列及互作关系学习扰动表示，不直接把实测 RNA 或质谱丰度作为同一个预训练输入。G2CP 用 UniPert 表示预测响应。

单个训练样本由对照向量、处理后向量、扰动嵌入组成：

| 字段 | 单样本形状 | 含义 |
| --- | --- | --- |
| `Data.x` | `[G, 1]` | 适当预处理后的对照表达 |
| `Data.y` | `[1, G]` | 同一组有序特征的处理后表达标签 |
| `Data.unipert_rep` | 单药时一份 256 维表示 | 药物或遗传扰动表示 |
| `Data.pert` | 字符串 | 条件/扰动类别 |
| `de_idx` | 索引列表 | DE 评价辅助；当前构造器没有真实计算 DE 索引，而使用占位值 |

批次输出为 `[B,G]`。基因数 `G` 由输入确定，并非网络写死为 978；作者 LINCS 实验使用 978 landmark 特征。复用作者权重仍需要核对具体特征集、顺序与参数形状。

原版接近 `预测处理后表达 = 对照表达 + f(基因身份、训练图、扰动表示)`：`model.py` 在最后把 `x` 作为残差相加，主干没有先将对照表达值编码为细胞状态。因此 RNA 训练学到的是响应预测参数，不能直接称为通用 RNA 编码器预训练。当前 forward 也没有显式剂量、时间或细胞背景条件输入。

## 3. 如何整理 AnnData 输入

以下是概念上的接口，不是当前原版可直接运行的完整训练脚本：

```python
# 每一行是一个处理样本或其可用对照，每一列是固定顺序的基因。
adata.X                              # CSR 稀疏矩阵，已预处理；不是未归一化计数直接送入
adata.var_names                      # G 个稳定且唯一的基因 ID
adata.obs['condition']                # 'ctrl' 或可找到嵌入的药物 ID
adata.obs['pert_type']                # 药物 'trt_cp'，遗传 'trt_xpr'；对照另标
adata.obs['cell_line']                # HS578T
adata.obs['plate']                    # RNA 对照匹配用
adata.obs['dose']                     # 保留元数据；原模型不会自动使用它
adata.obs['time_h']                   # 同上
adata.uns['UniPert_reps'][drug_id]     # 256 维有效扰动表示
```

必须另设样本索引/condition_id 追踪 `drug + dose + time + cell + plate`。原版按 `condition` 分组并用其查嵌入；改造时应分离条件 ID 与药物 ID，并按药物分组划分。只把剂量写进字符串、仍查同一药物嵌入，并不会让模型获得剂量信息。若保留原版单药命名，避免把非组合标签写成含 `+` 的字符串，加载器会据此拆分组合。

准备步骤：

1. 取得此次运行的 `genes.csv`、药物/剂量/时间条件映射、对照配对表与状态文件。
2. 先核查 `scan_status.json`、`summary.json`、`index_errors.json`、`extraction_errors.json`，确定完整性和覆盖。
3. 分片 pb 已是细胞求和。按 `(sample, cell_line_id, plate)` 将同一组跨文件的 counts 相加；不可将每片中的同组当独立重复。
4. 通过 `genes.csv` 恢复精确列顺序和 token/gene 映射。单细胞 Parquet 中的 token ID 不能直接当 gene symbol。
5. RNA 使用总量归一化及 log1p 等明确、固定的变换；保留 raw counts。滤除低覆盖、零库大小、低表达特征时登记规则。不要把全部 62,710 个位置直接当有效表达基因。
6. 同细胞系、同 plate 匹配对照；原版 `LINCS-pool` 只按 cell_line 匹配，不足以替代本任务的 plate 匹配。
7. 第一轮固定时间和剂量、只用单药。具体交集需要条件表核实，不能现在假定已经严格配对。
8. 为药物生成/加载 UniPert 256 维嵌入，记录其版本、ID 与覆盖，避免用随机嵌入替代后声称复现。
9. 自定义加载器初始化 `gene_names/gene_ptbgs/chem_ptbgs/all_ptbgs/batch_key` 等字段，重用构造和训练逻辑。`load(data_path=...)` 的自定义分支没有补齐这些字段，不能仅另存 `perturb_processed.h5ad` 就认为能运行。
10. 为 Tahoe 编写单独入口。原入口只接收特定 LINCS 名称，含作者绝对路径并固定 CUDA；本地也尚无 PyTorch/torch-geometric/Scanpy 等训练依赖和 UniPert 权重。

先训练特征子集或 RNA/蛋白共同基因集。原代码计算全特征 Pearson 图，62,710² 约 39.3 亿元素，单张 float64 矩阵约 31.5 GB，另有中间数组。不是一次性直接全量建图的合适起点。

## 4. 先 RNA 训练再蛋白微调是否可行

可行，属于需要验证的监督迁移方案。原论文的“遗传扰动 RNA → 化学扰动 RNA”没有改变表达测量模态，而此方案改变模态、数值分布与部分特征。当前 Tahoe 子集是药物响应；不能直接当作原训练入口中的遗传预训练集合。

推荐第一版使用共同基因集 `G_shared`：

1. 蛋白 `geneName` 与 RNA Ensembl/gene symbol 进行版本明确的映射。蛋白群组、多基因和多蛋白映射须登记，初版可先用无歧义的一对一映射。不要按行号对齐。
2. RNA 和蛋白分别按同一个 `genes_shared` 顺序选列。共同基因数待取得 Tahoe genes.csv 后计算，不假定为 5,585 或 978。
3. 蛋白转成样本×蛋白的方向，与样本表按规范化 Sample_ID 连接；匹配细胞系、时间和批次/仪器等可用信息下的对照。6/24/48 h 的未给药对照不能声称是真实 0 h 的同一个细胞。
4. 对正蛋白强度做适当 log2/样本层面归一化。是否进一步按特征标准化由训练集拟合，验证/测试只应用。RNA 与蛋白不混用同一数值预处理。
5. 缺失蛋白保留 mask，预测损失只对有效观测计算。当前 G2CP 损失没有该掩码，必须修改，不能用 0 代替缺失后照常计算。
6. 在 RNA 处理样本上训练响应任务，再将同维同序模型迁移至蛋白，先冻结部分主干、训练蛋白相关参数，然后小学习率解冻作为候选策略。具体学习率用验证集选择。
7. 对图是否固定为训练 RNA 图、或用蛋白训练集重建，做明确选择和记录；不得把测试处理谱用于构图或特征筛选。

G2CP 有 `gene_emb/emb_pos/indv_w1/indv_w2/cross_gene_state` 等依赖特征数量与顺序的参数。不同 G 的检查点不能整体直接加载；仅 `strict=False` 也不能忽略同名参数的尺寸冲突。要么从一开始采用共同特征集，要么明确映射/重置特征相关层，仅迁移形状和语义兼容的部分。原版 `load_pretrained` 是严格权重加载，不能自动完成上述跨组学适配。

另一路线是不同模态各自输入/输出适配层，共享扰动表示和部分主干。这样可使用 RNA 和蛋白各自的全部有效特征，但偏离原版更多，应作为后续模型。

## 5. 同时使用 RNA 和蛋白训练

非配对联合多任务训练可先交替取 RNA batch、蛋白 batch，使用模态专用输入/输出层，优化各自监督损失；损失权重与采样比例需要验证，避免 RNA 样本多而支配训练。

这不要求每个 RNA 样本都有蛋白配对。若要预测时同时输入 RNA 和蛋白，需要额外的融合网络和可信的共同背景/配对数据；当前条件交集不能当成同一细胞测得的配对。相关性聚类可作为额外分析，不应替代基因身份映射或产生测试响应参与的训练配对。

## 6. 最小可解释对照

| 组别 | 训练设置 | 回答的问题 |
| --- | --- | --- |
| A | 预测处理后等于对照、训练集平均效应、线性模型 | 基础参照 |
| B | 蛋白 G2CP，从随机初始化训练 | 同一改造网络无 RNA 迁移的能力 |
| C | 同网络、同蛋白划分；RNA 响应训练后蛋白微调 | RNA 是否增加收益 |
| D | 同网络交替 RNA/蛋白训练 | 联合训练与顺序迁移的差异 |

固定蛋白训练/验证/测试划分、共同特征、随机种子和下游预算。RNA 额外计算量需报告，可加等步数蛋白训练对照。同一药物的重复和不同剂量/时间不要无意跨越“留药物”划分。

分开报告两个问题：

- RNA 中已见测试药物、蛋白中未见该药物：跨模态迁移，不能称全部训练未见药物。
- RNA 和蛋白所有训练阶段都排除测试药物：更严格的未见药物泛化。

目前 RNA 只有 HS578T，因此可以开展该背景内的留药物实验，不能仅凭这批 RNA 声称跨 RNA 细胞背景泛化。119 个样本组也不等于 161,217 个独立药物实验。

评价优先用处理−对照的变化量：RMSE/MAE、变化量相关性、扰动区分和差异特征方向等。蛋白缺失 mask 贯穿训练与评价，DE 特征若由测试标签定义应明确仅用于最终评价，不能用于训练期特征选择。

## 7. 现在从 Drive 补齐什么

从 `MyDrive/virtualcell_ptds_tahoe_alignment_v1/results/` 直接下载以下文件，放入本地 `results/ptds_tahoe_alignment_v1/`：

```text
scan_status.json
summary.json
index_errors.json
extraction_errors.json
genes.csv
matched_conditions.csv
matched_pairs.csv
matched_ptds_samples.csv
pseudobulk_control_pairs.csv
missing_plate_controls.csv
pseudobulk_obs.csv
pseudobulk_raw_counts.h5ad
candidate_conditions.csv
target_sample_cells.csv
tahoe_drug_structure_map.csv
ptds_drug_resolution.csv
```

优先下载前 12 项；CSV/JSON 可逐个下载，H5AD 也可作为单文件下载，无需重新打包 13,232 个中间文件。若云端第 6 节尚未成功完成，应先运行合并与校验；不要借用另一实验的同名 summary.json。

## 代码及外部依据

- 本地 `baseline/unipert-g2cp/G2CP/backbone_model/GEARS/gears/{pertdata,model,gears,utils}.py`。
- 本地 `colab/ptds_tahoe100m_alignment_drive.ipynb`：分片产生及合并语义。
- 上游 https://github.com/lynn-1998/UniPert-G2CP_reproduce 。本文输入判断以本地实际代码为准。
- UniPert https://github.com/TencentAILabHealthcare/UniPert 。
- HS578T 标识 https://www.cellosaurus.org/CVCL_0332 。
