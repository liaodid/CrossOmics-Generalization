# MultiPert：THP-1 RNA–ADT 基因扰动数据

## 是什么

Papalexi 等产生、MultiPert 复用的 ECCITE-seq 数据，同一细胞具有 RNA、少量表面蛋白 ADT 和基因扰动信息。

## 内容

MultiPert Datasets 小节报告 8,984 个细胞、16,826 个基因、4 个蛋白和 10 种单基因敲除扰动。去掉细胞数少于 10 的扰动条件后，后续评估涉及 9 种扰动。上述数字不代表 Zenodo 包的所有对象都具有相同维度。

## 来源与获取

- [Zenodo 7041849](https://zenodo.org/records/7041849)。
- [MultiPert PDF](../../../pdf/multipert.pdf)：Datasets、Data availability statement。
- 获取与通用格式见[父目录](../README.md)。

## 状态与存放

⏳ 未下载。原始矩阵与元数据放 `raw/`；条码对齐、质量过滤和划分后的结果放 `processed/`。下载后登记文件名、大小、日期与 SHA-256。

## 使用注意

RNA/ADT 是配对观测，但对照细胞和扰动细胞不是同一细胞的前后测量。论文同时研究随机细胞划分和留扰动验证；不能把前者当作新扰动泛化。4 个抗体蛋白不能代表质谱全蛋白组覆盖。
