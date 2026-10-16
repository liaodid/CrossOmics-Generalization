# CrossOmics-Generalization

研究问题：**同时用转录组和蛋白组的扰动数据训练一个扰动响应模型（“虚拟细胞”），能否提升蛋白组层面预测的泛化性。**

> **当前阶段：设想与数据调研，尚无实验结果。**
> - 只使用公开数据，不做湿实验。
> - 主要对标对象：西湖大学的蛋白组虚拟细胞模型 ProteinTalks（Nature 2026，已确认）。代码已公开，训练数据尚未拿到。
> - 已入库的代码只有 Baseline 1（UniPert‑G2CP 上游代码，未运行）。
>
> 已核实的事实、讨论结论和待定事项都记录在 [docs/findings.md](docs/findings.md)。

## 新成员从哪里开始

| 想了解 | 去看 |
|---|---|
| 生物学术语（面向 CS 背景） | [docs/glossary.md](docs/glossary.md) |
| 项目目标、已知事实、待定事项 | [docs/findings.md](docs/findings.md) |
| 相关论文与链接 | [18 篇论文阅读索引](docs/literature/README.md)（逐篇中文介绍与优先级），[docs/papers.csv](docs/papers.csv)（总清单），[手动下载入口](pdf/MANUAL_DOWNLOADS.md) |
| 有哪些对比方法 | [baseline/README.md](baseline/README.md) |
| 有哪些数据、能否获取 | [data/README.md](data/README.md) |
| 分析脚本 | [script/README.md](script/README.md) |
| 探索性 notebook 及其结论 | [colab/README.md](colab/README.md) |
| 分析结果（对齐表、汇总） | [reports/](reports/README.md) |
| 汇报幻灯片与文献综述 | [output/](output/README.md) |
| 分支、提交、文件放置约定 | [docs/collaboration.md](docs/collaboration.md) |
| 手上有原作者的其他源码，该放哪里 | [baseline/unipert-g2cp/README.md 第 11 节](baseline/unipert-g2cp/README.md#11-补充原作者源码放在哪里) |

## 目录结构

```text
CrossOmics-Generalization/
├── README.md                    # 本文件：项目总览
├── baseline/                    # 对比方法（他人已发表的方法）
│   ├── README.md
│   ├── unipert-g2cp/            # Baseline 1：UniPert-G2CP 上游复现代码（原样保留）
│   │   ├── README.md            #   复现说明（中文）
│   │   ├── LICENSE              #   上游 MIT 许可证
│   │   ├── docs/                #   上游原始 README 与来源提交号
│   │   ├── UniPert/             #   扰动表示模型
│   │   ├── G2CP/                #   扰动响应预测模型（改自 GEARS）
│   │   ├── analysis_assets/     #   论文作图 notebook（依赖相对路径，需与代码同目录）
│   │   └── extra/               #   复现仓库之外的原作者源码 + 来源登记表
│   └── proteintalks/            # Baseline 2：ProteinTalks（主要对标对象；代码公开，尚未放入本仓库）
├── data/                        # 数据：Git 只跟踪各数据集的 README.md
│   ├── README.md                #   数据集一览、论文与数据文档对应表、目录约定
│   ├── <方法名>/                #   各篇相关论文所用数据的说明（gears、cpa、state、multipert 等 11 个）
│   ├── lincs-l1000/
│   ├── unipert-g2cp-zenodo/
│   ├── proteintalks/            #   ProteinTalks 数据总说明
│   │   ├── ptds/                #     主数据集：18 个乳腺癌系
│   │   ├── mtptds/              #     多时间点数据集
│   │   └── ptpc/                #     跨癌种数据集（含 A375）
│   ├── hepg2-drug-proteome-msv000101671/
│   ├── hepg2-drug-transcriptome-gse51952/
│   ├── hepg2-degrader-proteome-basu2026/
│   └── tahoe-100m/
├── script/                      # 可复现的分析脚本（说明见 script/README.md）
│   ├── audit_lincs_metadata.sh
│   ├── lincs_cell_line_coverage.sh
│   ├── collect_literature.py    #   下载并校验论文 PDF
│   ├── retry_literature.py      #   对未下载成功的论文重试其他链接
│   └── build_literature_docs.py #   生成 docs/literature/ 阅读索引
├── colab/                       # 探索性 Colab notebook（结论见 colab/README.md）
│   ├── hepg2_alignment_drive.ipynb
│   ├── ptds_unipert_lincs_alignment_drive.ipynb   # PTDS × LINCS（MCF7）药物对齐
│   └── ptds_tahoe100m_alignment_drive.ipynb       # PTDS × Tahoe-100M 药物对齐
├── reports/                     # 分析结果：每次分析一个 <名称>-<日期>/ 目录，放小型 CSV/JSON
│   └── ptds-unipert-2026-10-16/ #   PTDS × LINCS（MCF7）对齐结果
├── output/                      # 汇报材料：幻灯片、综述等，每份一个 <名称>-<日期>/ 目录
│   └── overleaf-expanded-2026-10-16/  # 25 页 Beamer 幻灯片 + 文献综述
├── pdf/                         # 论文 PDF（仅本地，不提交）；下载清单与手动下载入口会提交
└── docs/
    ├── findings.md              # 已核实的事实、结论、待定事项
    ├── glossary.md              # 术语表
    ├── papers.csv               # 论文总清单：方法名 ↔ 标题 ↔ DOI ↔ 本地 PDF ↔ 仓库目录
    ├── literature.csv           # 18 篇论文的详细表格
    ├── literature/              # 18 篇论文中文介绍与阅读索引
    ├── references.md            # 参考文献摘要
    ├── collaboration.md         # 协作约定
    └── papers/                  # 早期约定的 PDF 位置，已由根目录 pdf/ 取代
```

## 进度

- [x] 梳理 Baseline 1 的代码、任务定义与已知问题
- [x] 核实 LINCS 中各细胞系的药物与 CRISPR 覆盖（`script/audit_lincs_metadata.sh`）
- [x] HepG2 RNA‑蛋白配对探索：没有找到同条件的数据（见 `colab/`）
- [x] 仓库结构与文档整理
- [x] 确认对标论文：ProteinTalks（2026‑10‑15）
- [x] 确认 ProteinTalks 代码公开且完整（`guomics-lab/PTV-1`），并整理其输入格式
- [x] 核对 ProteinTalks 细胞系与 LINCS 的重合：A375、MCF7 两边都有（`script/lincs_cell_line_coverage.sh`）
- [ ] 定义任务、测试集与指标（[待定事项](docs/findings.md#待定事项) 第 2 项）
- [ ] 获取 ProteinTalks 训练数据（正在与西湖作者联系）
- [x] 完成首轮 18 篇相关文献检索：已找到 TransPro、MultiPert 等跨组学先例（尚非穷尽性检索）
- [x] PTDS × LINCS（MCF7）药物对齐：20 种药两边都有，200 条 RNA 签名、174 个蛋白样本，不限剂量和时间（`reports/ptds-unipert-2026-10-16/`）
- [ ] PTDS × Tahoe-100M 对齐：流程已验证，尚未完整扫描
- [ ] 选定主线细胞系，整理转录组与蛋白组数据
- [ ] 跑通基线，建立统一评价协议
- [ ] 实现并评估联合训练模型

## 运行环境说明

- `colab/` 中的 notebook 在 Google Colab 上运行，输出写入运行者自己的 Google Drive。
- 在 HPC 集群（如 Vulcan）上运行时，训练等重计算必须通过 Slurm 提交，大文件放在 `$SCRATCH` 或项目空间，不放在 `$HOME`。
- Baseline 1 的依赖、写死路径和数据放置，见其 [README](baseline/unipert-g2cp/README.md) 第 4–6 节。

## 许可证

- `baseline/unipert-g2cp/` 沿用上游的 MIT 许可证（见该目录下的 `LICENSE`）。
- 本项目自有代码与文档的许可证：现阶段不考虑（2026‑10‑15 决定），之后再定。
