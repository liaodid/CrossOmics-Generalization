# UniPert-G2CP 实验复现与基线协作

本仓库用于复现 UniPert-G2CP 的实验，并将其作为后续细胞扰动预测研究的基线。

代码来源于论文作者公开的复现仓库。我们保留原始代码与来源说明，逐步补充中文文档、环境配置、运行记录和基线实验结果。

> 当前状态：已整理代码说明与复现步骤，尚未完成实验验证。
> 本文根据上游公开代码编写；实际运行前需要核对本地版本、依赖和数据。
> State 论文作为相关工作列入文档，本仓库目前不包含其实现。

## 1. 论文与代码来源

### 1.1 UniPert-G2CP：本仓库的主要复现对象

**论文标题：**
UniPert-G2CP bridges genetic and chemical screens from molecular representation to phenotype modeling

- [Cell 正式论文](https://www.sciencedirect.com/science/article/pii/S0092867426006549)
- [论文 DOI](https://doi.org/10.1016/j.cell.2026.06.005)
- [作者实验复现仓库](https://github.com/lynn-1998/UniPert-G2CP_reproduce)
- [UniPert 官方使用与推理仓库](https://github.com/TencentAILabHealthcare/UniPert)
- [作者发布的数据、模型权重与中间结果](https://doi.org/10.5281/zenodo.20355906)

本地引入的上游版本记录在 `docs/upstream_commit.txt`。
作者原始 README 保存在 `docs/README.upstream.md`。

### 1.2 State：相关工作与后续比较对象

**论文标题：**
Predicting cellular responses to perturbation across diverse contexts with State

- [Cell 正式论文](https://www.sciencedirect.com/science/article/pii/S0092867426009219)
- [论文 DOI](https://doi.org/10.1016/j.cell.2026.07.052)
- [作者预印本](https://www.biorxiv.org/content/10.1101/2025.06.26.661135v2)
- [State 主代码](https://github.com/ArcInstitute/state)
- [State 实验与分析复现代码](https://github.com/ArcInstitute/state-reproduce)

State 包含细胞表示模型 SE 和细胞状态转移模型 ST，
重点研究不同细胞背景中的扰动响应预测。

两篇论文的任务、输入和数据划分存在差异。
后续比较应统一任务与评价方式，不能直接比较论文中的不同指标数值。

## 2. UniPert-G2CP 的整体思路

模型分成两个主要部分。

### 2.1 UniPert：统一遗传和化学扰动的表示

UniPert 将蛋白质和小分子编码到共同的向量空间。

- 蛋白质端：使用蛋白序列表示，并通过序列相似关系构建图。
- 化合物端：默认使用 ECFP4 分子指纹表示。
- 图学习：增强蛋白质表示。
- 跨模态对齐：利用化合物—靶点相互作用进行对比学习。

输出是扰动对象的向量表示，不是细胞响应预测结果。

### 2.2 G2CP：遗传到化学扰动的迁移

G2CP 使用改造后的 GEARS 骨干进行表型预测：

1. 在遗传扰动数据上预训练。
2. 在化学扰动数据上微调。
3. 预测留出药物引起的细胞响应。

其输入结合未扰动状态与扰动对象表示；
输出对应当前任务的基因表达或形态特征。

特别注意：遗传扰动不全部等同于 CRISPR 敲除。
具体操作类型需要根据 LINCS、CP-JUMP1 等数据的元信息确认。

## 3. 仓库结构

下面展示核心代码结构。
数据、权重和结果目录可能需要下载作者资源后补齐。

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── README.upstream.md
│   └── upstream_commit.txt
├── UniPert/
│   ├── unipert/
│   │   ├── __init__.py
│   │   ├── model.py
│   │   ├── modules.py
│   │   ├── dataset.py
│   │   ├── ctcloss.py
│   │   ├── scheduler.py
│   │   └── utils.py
│   ├── perturbation_tasks/
│   │   ├── genetic_benchmark/
│   │   └── chemcial_benchmark/
│   ├── run_scripts/
│   ├── data/
│   ├── current_model/
│   ├── saved_models/
│   └── results/
├── G2CP/
│   ├── backbone_model/GEARS/gears/
│   ├── run_scripts/
│   ├── train_G2CP_cpf.py
│   ├── train_G2CP_essp.py
│   ├── train_G2CP_pool.py
│   ├── train_G2CP_simf.py
│   ├── train_G2CP_ts.py
│   ├── data/
│   ├── saved_models/
│   └── results/
└── analysis_assets/
```

`chemcial_benchmark` 是上游目录中的实际拼写，使用时保持一致。

### 3.1 UniPert 核心代码

| 文件 | 职责 |
|---|---|
| `UniPert/unipert/__init__.py` | 定义数据、当前模型、保存模型和 MMseqs 缓存的默认位置，并导出接口 |
| `UniPert/unipert/model.py` | UniPert 主接口；组织模型构建、参考图准备、训练、模型加载和扰动表示生成 |
| `UniPert/unipert/modules.py` | 蛋白质与化合物嵌入器、编码器和图学习组件 |
| `UniPert/unipert/dataset.py` | 化合物—靶点训练数据的组织 |
| `UniPert/unipert/ctcloss.py` | Compound-Target Contrastive Loss，负责化合物与靶点表示对齐；不是语音识别中的 CTC 损失 |
| `UniPert/unipert/scheduler.py` | 学习率调度辅助代码 |
| `UniPert/unipert/utils.py` | 模型流程使用的辅助函数 |

当前代码默认配置包含 ESM2、ECFP4、GCN 和 256 维输出。
正式复现时应读取发布权重的配置，不能仅使用代码默认值推断论文全部实验设置。

### 3.2 UniPert 的实验目录

| 目录或脚本 | 用途 |
|---|---|
| `perturbation_tasks/genetic_benchmark/` | 遗传扰动预测基准与适配代码 |
| `perturbation_tasks/chemcial_benchmark/` | 化学扰动预测基准与适配代码 |
| `run_scripts/run_genetic_perturbation_benchmark_exps.sh` | 批量启动遗传扰动预测基准 |
| `run_scripts/run_chemical_perturbation_benchmark_exps.sh` | 批量启动化学扰动预测基准 |
| `run_scripts/run_embedder_gs.sh` | 嵌入器相关参数搜索入口 |
| `run_scripts/run_gnn_ln_od_gs.sh` | 图模型层数、输出维度等参数搜索入口 |
| `run_scripts/run_graph_weight_direct_rd.sh` | 图权重与方向相关实验入口 |
| `run_scripts/cal_new_cpi_unipert_similarity.py` | 新 CPI 数据的 UniPert 相似度计算入口 |

这些是实验入口，不应在未核对路径和资源需求时一次性全部执行。

### 3.3 G2CP 骨干代码

| 文件 | 职责 |
|---|---|
| `G2CP/backbone_model/GEARS/gears/pertdata.py` | 加载数据、检查 UniPert 表示、划分扰动集合、构造样本和 DataLoader |
| `G2CP/backbone_model/GEARS/gears/data_utils.py` | 数据准备与划分辅助逻辑 |
| `G2CP/backbone_model/GEARS/gears/model.py` | 扰动表型预测网络 |
| `G2CP/backbone_model/GEARS/gears/gears.py` | GEARS 模型的训练、保存及相关管理接口 |
| `G2CP/backbone_model/GEARS/gears/inference.py` | 推理与结果评估相关逻辑 |
| `G2CP/backbone_model/GEARS/gears/utils.py` | 损失、评价及其他工具函数 |

建议按以下顺序阅读：

训练入口 → `pertdata.py` → `data_utils.py` →
`gears.py` → `model.py` → 推理与分析代码。

### 3.4 G2CP 训练与推理入口

| 文件 | 用途 |
|---|---|
| `train_G2CP_cpf.py` | 遗传预训练和药物微调的比例实验 |
| `train_G2CP_essp.py` | 按基因必要性相关策略开展的预训练实验 |
| `train_G2CP_pool.py` | 多细胞系数据整合实验 |
| `train_G2CP_simf.py` | 化合物相似性或结构划分相关实验 |
| `train_G2CP_ts.py` | Touchstone 与 Discovery 设置相关实验 |
| `run_scripts/run_LINCS_*.sh` | 相应实验的批量启动脚本 |
| `run_scripts/inference_cell_line_chemical_perturb_effect.py` | 细胞系中的化学扰动效应推理入口 |
| `run_scripts/inference_cell_line_genetic_perturb_effect.py` | 细胞系中的遗传扰动效应推理入口 |
| `run_scripts/cmap_utils.py` | CMap 相关辅助代码 |

不同入口的划分策略与实验目的不同，不能混用结果。
训练模式的具体含义以入口和数据划分实现为准。

### 3.5 论文图表分析

`analysis_assets/` 中的 Notebook 用于分析模型表示和实验结果。

主要内容包括：

- Fig. 2：药物作用机制、靶点聚类、蛋白家族与 motif 分析。
- Fig. 3：遗传扰动、sci-Plex3 药物扰动和 HDAC 药物案例。
- Fig. 4：G2CP 验证结果。
- Fig. 5：统一扰动空间、CPI 预测、跨细胞系与敏感性分析。
- Fig. 6：扰动原因与效应的联合案例分析。
- 补充图：超参数搜索、图结构消融和 CP-JUMP1 结果等。

Notebook 通常依赖事先生成或下载的中间结果。
运行 Notebook 并不等于重新训练模型。

## 4. 数据与权重

### 4.1 第一篇论文：优先使用作者处理后的资源

复现的首选下载入口：

[UniPert-G2CP 数据、权重和中间结果（Zenodo）](https://doi.org/10.5281/zenodo.20355906)

按上游说明将资源放入对应的 `data/`、`current_model/`、
`saved_models/` 或 `results/` 目录。

本项目尚未核对下载包的全部文件清单。
下载后应记录文件名、版本、大小和 SHA256，并确认目录层级。

原始数据库下载不能直接替代作者处理后的实验输入。

### 4.2 第一篇的主要数据与原始来源

| 数据/资源 | 主要用途 | 来源 |
|---|---|---|
| LINCS L1000 / CMap | 遗传和药物扰动后的表达响应；G2CP 迁移实验 | [GSE92742](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92742)、[GSE70138](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE70138) |
| CP-JUMP1 | 遗传和化学扰动的 Cell Painting 形态特征 | [原始项目](https://github.com/jump-cellpainting/2024_Chandrasekaran_NatureMethods_CPJUMP1) |
| sci-Plex3 | 单细胞药物扰动预测基准 | [原始论文](https://doi.org/10.1126/science.aax6234) |
| Dixit、Norman 等遗传扰动基准 | 遗传扰动预测和组合扰动评估 | 优先从作者 Zenodo 资源与对应基准代码核对 |
| 化合物—靶点相互作用及参考序列 | UniPert 分子表征训练与对齐 | 作者处理后的资源；原始数据库包括 [PubChem](https://pubchem.ncbi.nlm.nih.gov/) 与 [UniProt](https://www.uniprot.org/) |

LINCS 核心代码包含 A549、A375、MCF7、PC3 和 HT29。
CP-JUMP1 数据加载代码包含 A549 和 U2OS。

上游 UniPert 代码引用了处理后的 PubChem CPI 文件。
具体样本数量与数据库版本应依据下载资源和正式论文确认，
不使用其他人的扩展仓库数据替代原论文数据。

### 4.3 第二篇 State 的数据参考

以下用于理解 State 或后续准备比较实验，
不是当前 UniPert-G2CP 实验的必需下载项。

| 数据资源 | 用途 | 链接 |
|---|---|---|
| Tahoe-100M | 大规模药物扰动单细胞数据 | [Hugging Face](https://huggingface.co/datasets/tahoebio/Tahoe-100M) |
| Parse PBMC-10M | 免疫细胞的细胞因子扰动 | [Parse 数据入口](https://www.parsebiosciences.com/datasets/10-million-human-pbmcs-in-a-single-experiment/) |
| Replogle–Nadig | 遗传扰动训练和评估 | [State 官方复现入口](https://github.com/ArcInstitute/state-reproduce) |
| Arc scBaseCount | SE 表征训练的数据来源之一 | [官方项目](https://github.com/ArcInstitute/scBaseCount) |
| CZ CELLxGENE | SE 表征训练的数据来源之一 | [官方数据入口](https://cellxgene.cziscience.com/) |

State 的 SE 还使用 Tahoe 的选定子集。
其预训练语料与 ST 的扰动实验数据应分别记录。

## 5. 运行前准备

### 5.1 环境

建议在 WSL/Linux 下使用独立 Python 环境。
依赖范围包括 PyTorch、PyTorch Geometric、NumPy、
Pandas、AnnData/Scanpy，以及相关分子和蛋白质处理工具。

使用 UniPert 的序列搜索流程时还需要 MMseqs2。
具体依赖版本必须以代码、作者资源及实际安装验证为准。

本仓库目前没有团队验证通过的完整环境锁定文件，
因此本文不宣称提供一条命令即可完成安装。

环境跑通后保存：

```bash
python -m pip freeze > docs/environment.pip.txt
nvidia-smi > docs/environment.gpu.txt
```

如使用 Conda，可额外导出：

```bash
conda env export --no-builds > docs/environment.conda.yml
```

提交前移除环境文件末尾与本机绑定的 `prefix:` 路径。

### 5.2 修改作者机器上的固定路径

原始代码中存在 `/data/liyiming/Project/...` 等固定路径。

在仓库根目录检查：

```bash
rg -n '/data/liyiming|/fionafyang|sys\.path|source activate|gpu_num' UniPert G2CP
```

如果没有安装 `rg`：

```bash
grep -RInE '/data/liyiming|/fionafyang|sys\.path|source activate|gpu_num' UniPert G2CP
```

至少核对：

- Python 模块搜索路径。
- 数据目录。
- UniPert 权重目录。
- 模型和结果保存目录。
- Shell 脚本的环境名称。
- GPU 编号与并发任务数量。
- Notebook 中的数据和结果路径。

`train_G2CP_cpf.py` 中的数据路径和 GEARS 导入路径写死在代码中，
仅传入 `--save_dir` 不能解决全部路径问题。

团队后续应将路径改为相对路径、环境变量或命令行配置，
并通过 Pull Request 保留改动记录。

## 6. 先运行一个实验

建议先跑通：

一个 LINCS 细胞系 → 一个随机种子 →
一种训练模式 → 一组预训练/微调比例。

确认数据、模型和评估流程正确后，再扩大到论文完整实验。

### 6.1 检查数据格式

以 LINCS-A549 为例，加载代码预期的路径形式为：

```text
G2CP/data/LINCS/A549/A549_gene_chem_ctrl_adata.h5ad
```

检查 AnnData 中：

- `obs["pert_type"]`：扰动类型。
- `obs["condition"]`：扰动条件。
- 对照条件是否对应 `ctrl`。
- `uns["UniPert_reps"]`：扰动表示。

同时核对基因/特征顺序、扰动 ID 与权重配置。
缺少 UniPert 表示时，应先按作者流程生成或使用处理后的数据。

### 6.2 单任务命令示例

下列命令使用上游 CPF 入口支持的参数。
前提是已安装依赖、准备数据并修正内部路径。

```bash
cd ~/UniPert-G2CP_reproduce

export WANDB_MODE=offline
export CUDA_VISIBLE_DEVICES=0

python G2CP/train_G2CP_cpf.py \
  --dataset LINCS-A549 \
  --train_mode pretrain-finetune-cpf \
  --seed 1310 \
  --pretrain_frac 1.0 \
  --finetune_frac 0.2 \
  --epochs 20 \
  --unipert_model_dir "$PWD/UniPert/current_model" \
  --save_dir "$PWD/G2CP/saved_models/baseline_a549"
```

这是单任务启动示例，尚未在本项目实际运行验证。

原始 CPF 代码会在保存路径包含字符串 `test` 时改变训练 epoch。
命名实验目录时需要注意，并检查日志中的实际 epoch。

原始批量脚本会在多组条件上后台启动任务，
应先改为符合本机 GPU 数量的受控执行方式。

### 6.3 完整复现顺序

1. 准备作者数据和发布权重。
2. 验证单任务能够正常加载、训练和评估。
3. 核对实际训练与测试扰动集合。
4. 使用论文设置运行正式实验。
5. 重复指定随机种子。
6. 汇总模型指标。
7. 运行相应图表 Notebook。
8. 将复现结果与论文结果逐项对应。

## 7. 作为基线的实验规范

比较自己的方法时，至少统一：

- 数据版本及预处理。
- 细胞系和扰动范围。
- 输入及输出特征。
- 训练、验证与测试划分。
- 随机种子。
- 可使用的外部预训练数据。
- 评价指标定义与聚合方式。

不要以“随机划分单个细胞”替代论文的扰动对象留出设置。
不要使用测试响应选择模型、超参数或预处理规则。

建议先复现论文，再单独建立适用于本项目的统一比较协议。
协议变化后的结果应标明“本项目基线”，与论文原始设置区别记录。

每次实验建议保存：

| 项目 | 记录内容 |
|---|---|
| 代码版本 | commit SHA 与未提交修改 |
| 数据版本 | 下载来源、文件名、校验值 |
| 实验设置 | 任务、细胞系、划分文件、随机种子 |
| 训练设置 | 模式、比例、epoch、batch size、优化器 |
| 环境 | Python、依赖、GPU、驱动 |
| 运行命令 | 实际执行的完整命令 |
| 结果 | 日志、指标、权重位置和耗时 |

结果汇总建议采用：

```text
run_id,dataset,cell_line,train_mode,seed,
pretrain_frac,finetune_frac,metric,value,commit_sha
```

不同指标使用独立行，并另行记录其定义。
不能把全特征相关性、差异基因相关性和分类指标混作同一结果。

## 8. 团队协作

### 8.1 分支与 Pull Request

- `main`：保留经过检查的代码和文档。
- `docs/...`：文档更新。
- `fix/...`：运行问题修复。
- `exp/...`：实验改动。

示例：

```bash
git switch -c exp/a549-baseline

# 修改并验证后，按实际文件选择提交
git add README.md
git commit -m "docs: update baseline instructions"
git push -u origin exp/a549-baseline
```

在自己的协作仓库中提交 Pull Request。
PR 说明应包含修改目的、验证方式和受影响的实验。

### 8.2 建议分工

| 工作 | 交付物 |
|---|---|
| 环境与路径修正 | 可复现环境文件、运行说明 |
| 数据准备 | 数据清单、校验值、划分说明 |
| 原论文实验 | 命令、日志、指标与论文对应关系 |
| 新方法比较 | 统一评估协议和结果表 |

在 Issues 中记录待办、运行错误和复现差异，
避免仅依赖聊天记录传递实验设置。

### 8.3 GitHub 中保存什么

提交代码、配置、说明文档和小型结果汇总。
大型数据、模型权重、缓存和训练日志通过作者数据入口
或团队共享存储管理，并在文档中记录位置。

上游 `.gitignore` 已排除多种数据与权重文件。
被忽略的文件不会随普通 Git 克隆自动下载。

## 9. 来源与许可证

本仓库基于作者公开的 UniPert-G2CP 复现代码，
不代表论文作者的官方维护版本。

保留根目录 LICENSE、原始版权声明和第三方组件的许可信息。
上游复现仓库根目录采用 MIT 许可证；
UniPert 独立仓库和其他组件的许可应分别核对，
不能用一个根目录声明替代所有组件许可。

引用结果时，应引用相应论文、数据集，
并说明本项目对代码和实验设置的改动。

## 10. 复现进度

- [x] 整理论文、代码和主要数据入口
- [x] 编写代码结构与实验流程说明
- [ ] 固定上游版本并确认本地差异
- [ ] 建立经过验证的依赖环境
- [ ] 下载并核对数据、权重
- [ ] 修正固定路径
- [ ] 跑通单个 LINCS-A549 实验
- [ ] 核对划分和评价指标
- [ ] 完成正式多种子实验
- [ ] 汇总论文复现结果
- [ ] 建立本项目的统一基线协议