# data/：数据目录

Git 只跟踪各数据集目录下的 `README.md`，数据文件本身不提交（规则见根目录 `.gitignore`）。
克隆仓库后，按各数据集 README 的说明自行下载。

## 目录约定

每个数据集一个子目录，结构如下：

```text
data/<数据集名>/
├── README.md     # 来源、内容、获取方式、已核实事实、状态（提交到 Git）
├── raw/          # 原始下载文件，不做任何修改（不提交）
└── processed/    # 由脚本生成的处理结果（不提交）
```

- 数据集名统一用小写加短横线，形如 `<细胞系或来源>-<内容>-<编号>`。
- 同一来源发布了多个有名字的子数据集时，在该来源目录下按子集名建子目录（如 `proteintalks/ptds/`）。来源目录的 README 写获取方式和通用格式，子目录的 README 写各子集的内容。
- 下载后在 README 中记录：下载日期、URL、文件名、大小、SHA256。
- `processed/` 中的文件必须能由 `script/` 或 `colab/` 中的代码重新生成，并在 README 中写明生成方式。
- 未经核实的数字要明确标注“未核实”，并写明出处。

## 数据集一览

状态：✅ 已获取　⏳ 待获取　📝 仅元数据　❓ 可得性未确认

| 目录 | 组学 | 细胞系 | 规模（摘要） | 状态 | 在项目中的作用 |
|---|---|---|---|---|---|
| [lincs-l1000](lincs-l1000/README.md) | 转录组（L1000，978 个地标基因） | 数十个，含 HepG2、A375、MCF7 | 数十万条扰动签名 | 📝 | 转录组侧的主要大规模数据 |
| [unipert-g2cp-zenodo](unipert-g2cp-zenodo/README.md) | 转录组、细胞形态、化合物‑靶点对 | A549、A375、MCF7、PC3、HT29、U2OS | 作者处理后的全部实验输入与权重 | ⏳ | Baseline 1 复现所需 |
| [proteintalks](proteintalks/README.md)<br>└ [ptds](proteintalks/ptds/README.md) · [mtptds](proteintalks/mtptds/README.md) · [ptpc](proteintalks/ptpc/README.md) | 蛋白组（DIA‑MS） | 18 个乳腺癌系 + 5 个其他癌种系（含 A375） | PTDS 16,311 个质谱文件；mtPTDS 2,528 个样本；PTPC 2,307 个样本 | ⏳ | 对标模型 ProteinTalks 的数据，蛋白侧的主要大规模数据 |
| [hepg2-drug-proteome-msv000101671](hepg2-drug-proteome-msv000101671/README.md) | 蛋白组（Orbitrap Astral） | HepG2 | 172 种化合物，1,232 个样本，超过 8,700 个蛋白 | 📝 | HepG2 蛋白组；数据规模可观，但只有一个细胞系 |
| [hepg2-drug-transcriptome-gse51952](hepg2-drug-transcriptome-gse51952/README.md) | 转录组（芯片） | HepG2 | 22 种药，105 个样本 | 📝 | 早期探索用的小型转录组，已证实与上面蛋白组无可用配对 |
| [hepg2-degrader-proteome-basu2026](hepg2-degrader-proteome-basu2026/README.md) | 蛋白组 | HepG2 等 | 78 种 FDA 药 + 204 个 AR 降解剂；PXD062492 已从 PDF 确认 | 📝 | 候选的 HepG2 蛋白组数据，实验数据未下载 |
| [tahoe-100m](tahoe-100m/README.md) | 单细胞转录组 | 50 个癌细胞系，含 HepG2/C3A | 1 亿个细胞，约 1,100 个药物‑剂量条件 | ⏳ | 候选的大规模药物扰动转录组 |
| [multipert](multipert/README.md)<br>└ [thp1](multipert/thp1/README.md) · [kidney](multipert/kidney/README.md) · [pbmc](multipert/pbmc/README.md) | RNA + ADT / ATAC | THP-1、胚肾上皮、PBMC | THP-1 8,984 细胞/4 蛋白；kidney 8,802 细胞/7 蛋白 | 📝 | 直接多组学扰动先例；蛋白为抗体标签 |
| [state](state/README.md) | 单细胞 RNA | 多细胞背景、PBMC donors 等 | ST 六组资源；另有 SE 观测预训练数据 | 📝 | 上下文泛化与评价；2025 v1 口径 |
| [chemcpa](chemcpa/README.md) | bulk + 单细胞 RNA | LINCS 多细胞系；A549/MCF7/K562 | LINCS 预训练、sci-Plex3 适配；977/2,000 特征设置 | 📝 | 大规模 RNA 迁移与未见药物 |
| [cpa](cpa/README.md) | 单细胞 RNA | A549、K562、PBMC 等 | 含 Combosciplex：32 单药/组合条件、63,378 细胞 | 📝 | 组合响应与解耦；GSE206741 |
| [gears](gears/README.md) | 扰动 RNA；另含交互验证资源 | K562、RPE-1 等 | 多来源单/双基因扰动，版本分别登记 | 📝 | G2CP 骨干与遗传先验来源 |
| [linear-baselines](linear-baselines/README.md) | 单细胞扰动 RNA | K562、RPE-1 等 | Norman、Adamson、Replogle 的指定下载版本 | 📝 | 强基线与可比评价协议 |
| [xpert](xpert/README.md) | bulk / 临床 RNA | 多细胞系及临床癌种 | L1000 派生集、PANACEA、过滤后 CDS-DB 613 对谱 | 📝 | 时间剂量与跨来源迁移 |
| [perturbnet](perturbnet/README.md) | 化学/遗传/变异响应 RNA | A549/MCF7/K562、HSPC 等 | 五个主要响应集合；Table 7/8 分别记录 | 📝 | 未见扰动与立体化学处理 |
| [biolord](biolord/README.md) | RNA、ATAC 等 | 多背景；含观测图谱 | sci-Plex3、单/双基因 Perturb-seq 等 | 📝 | 属性解耦与共享数据版本追踪 |
| [totalvi](totalvi/README.md) | RNA + ADT | 人 PBMC、MALT；小鼠脾/淋巴结 | GSE150599 与 10x 数据，面板依样本变化 | 📝 | 配对多组学噪声模型；非药物质谱 |
| [multivi](multivi/README.md) | RNA + ATAC + ADT | PBMC 等 | TEA-seq、DOGMA-seq、单模态来源等 | 📝 | 部分配对与缺失模态处理 |

各数据集之间的关系、已核实的重叠情况，见 [docs/findings.md](../docs/findings.md)。

## 已下载论文与数据文档对应表

2026-10-15 依据本地 **16 篇 PDF** 补充。新增 11 个方法数据集合说明和 MultiPert 的 3 个子集说明；已有 5 个数据目录在原文档内补充，没有创建同名副本。

📝 在本轮新增条目中表示“已登记论文提供的数据来源”，不表示本地已经取得实验数据。论文声明公开与链接当前可下载是两回事；本轮没有联网核验入口，也没有下载实验数据。

| 本地 PDF | 数据文档 | 版本 / 处理说明 |
|---|---|---|
| [ProteinTalks](../pdf/proteintalks.pdf) | [proteintalks](proteintalks/README.md) | 本地为 2025 v1；既有正式版/代码说明保留并标出来源 |
| [UniPert-G2CP](../pdf/unipert-g2cp.pdf) | [unipert-g2cp-zenodo](unipert-g2cp-zenodo/README.md) | 2025 v2；与此前登记的正式版 Zenodo 分开 |
| [Tahoe-100M](../pdf/tahoe-100m.pdf) | [tahoe-100m](tahoe-100m/README.md) | 2025 v2；条件数与独立化合物数区分 |
| [Robotic proteomics](../pdf/robotic-proteomics.pdf) | [MSV000101671](hepg2-drug-proteome-msv000101671/README.md) | 2026 v1；24 h/10 μM/六重复已补核 |
| [Degrader proteomics](../pdf/degrader-proteomics.pdf) | [Basu2026](hepg2-degrader-proteome-basu2026/README.md) | 正式版；补齐 PRIDE/figshare 和已核实规模 |
| [MultiPert](../pdf/multipert.pdf) | [multipert](multipert/README.md) | 正式版；按 THP-1、kidney、PBMC 分子目录 |
| [State](../pdf/state.pdf) | [state](state/README.md) | 2025 v1；ST 和 SE 来源区分 |
| [chemCPA](../pdf/chemcpa.pdf) | [chemcpa](chemcpa/README.md) | NeurIPS 2022 |
| [CPA](../pdf/cpa.pdf) | [cpa](cpa/README.md) | 正式版；含新产生的 Combosciplex |
| [GEARS](../pdf/gears.pdf) | [gears](gears/README.md) | 正式版；原始 accession 与处理版区分 |
| [Linear baselines](../pdf/linear-baselines.pdf) | [linear-baselines](linear-baselines/README.md) | 正式版；记录作者具体下载文件 |
| [XPert](../pdf/xpert.pdf) | [xpert](xpert/README.md) | 正式版；含临床前/临床资源 |
| [PerturbNet](../pdf/perturbnet.pdf) | [perturbnet](perturbnet/README.md) | 正式版；保留原文表格与 Methods 的统计差异 |
| [biolord](../pdf/biolord.pdf) | [biolord](biolord/README.md) | 正式版；多任务复用数据 |
| [totalVI](../pdf/totalvi.pdf) | [totalvi](totalvi/README.md) | 作者接受稿；RNA/ADT 配对观测 |
| [MultiVI](../pdf/multivi.pdf) | [multivi](multivi/README.md) | 正式版；包括部分配对实验 |

TransPro 与 L1000 原始论文的 PDF 尚未下载，因此本轮不冒充依据其 PDF 新建说明；既有 [LINCS](lincs-l1000/README.md) 继续作为共享来源目录。

## 共享数据与输入格式

- LINCS 被 UniPert-G2CP、chemCPA、CPA、XPert、PerturbNet 等复用；sci-Plex 被 chemCPA、CPA、biolord、PerturbNet、State 等复用；Norman 等遗传数据同样在多篇论文出现。**方法目录是资源使用说明，不意味着应重复下载原始数据。**
- 原始来源相同不保证基因数、细胞数、过滤、归一化及划分相同；raw 实体可以共享，各方法处理版本分别登记。
- ADT 表面蛋白、质谱蛋白丰度、蛋白序列和药物靶点注释是不同数据类型。RNA 与 ADT 可在同一细胞配对，处理前后单细胞通常不是同一细胞的纵向配对。
- 新文档中明确标为“建议”的字段与路径是本项目整理约定；未获得矩阵并审查读取代码前，不声称已核验作者文件 schema。下载后统一记录 URL、日期、版本、文件大小与 SHA-256。
