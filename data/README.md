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
- 下载后在 README 中记录：下载日期、URL、文件名、大小、SHA256。
- `processed/` 中的文件必须能由 `script/` 或 `colab/` 中的代码重新生成，并在 README 中写明生成方式。
- 未经核实的数字要明确标注“未核实”，并写明出处。

## 数据集一览

状态：✅ 已获取　⏳ 待获取　📝 仅元数据　❓ 可得性未确认

| 目录 | 组学 | 细胞系 | 规模（摘要） | 状态 | 在项目中的作用 |
|---|---|---|---|---|---|
| [lincs-l1000](lincs-l1000/README.md) | 转录组（L1000，978 个地标基因） | 数十个，含 HepG2、A375、MCF7 | 数十万条扰动签名 | 📝 | 转录组侧的主要大规模数据 |
| [unipert-g2cp-zenodo](unipert-g2cp-zenodo/README.md) | 转录组、细胞形态、化合物‑靶点对 | A549、A375、MCF7、PC3、HT29、U2OS | 作者处理后的全部实验输入与权重 | ⏳ | Baseline 1 复现所需 |
| [proteintalks](proteintalks/README.md) | 蛋白组（DIA‑MS） | 18 个乳腺癌系 + 5 个其他癌种系 | 16,311 个质谱文件 + 2,307 个样本 | ⏳ | 对标模型 ProteinTalks 的数据，蛋白侧的主要大规模数据 |
| [hepg2-drug-proteome-msv000101671](hepg2-drug-proteome-msv000101671/README.md) | 蛋白组 | HepG2 | 172 种药，24 h，10 µM | 📝 | 早期探索用的 HepG2 蛋白组 |
| [hepg2-drug-transcriptome-gse51952](hepg2-drug-transcriptome-gse51952/README.md) | 转录组（芯片） | HepG2 | 22 种药，105 个样本 | 📝 | 早期探索用的小型转录组，已证实与上面蛋白组无可用配对 |
| [hepg2-degrader-proteome-basu2026](hepg2-degrader-proteome-basu2026/README.md) | 蛋白组 | HepG2 等 | 78 种 FDA 药 + 204 个 AR 降解剂（部分未核实） | ❓ | 候选的 HepG2 蛋白组数据 |
| [tahoe-100m](tahoe-100m/README.md) | 单细胞转录组 | 50 个癌细胞系，含 HepG2/C3A | 1 亿个细胞，约 1,100 个药物‑剂量条件 | ⏳ | 候选的大规模药物扰动转录组 |

各数据集之间的关系、已核实的重叠情况，见 [docs/findings.md](../docs/findings.md)。
