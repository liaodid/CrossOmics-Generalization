# MultiPert：PBMC 的 Multiome 与 ASAP-seq 数据

## 是什么

MultiPert 的扩展实验使用的两种单细胞多组学测量：10x Multiome 的 RNA–染色质，以及 ASAP-seq 的染色质–ADT。它们不是每个细胞都同时有三种模态的一个统一矩阵。

## 内容

论文说明以 IL2 和 anti-CD3/CD28 孵育 16 h 产生响应。细胞数、各对象的特征数、对照与刺激组、donor 和批次关系需从原始数据逐一核对，本次不填写未验证数字。

## 来源与获取

- [GEO GSE156478](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE156478)。
- [MultiPert PDF](../../../pdf/multipert.pdf)：Datasets 及额外模态实验。
- [MultiVI 数据说明](../../multivi/README.md)也引用该 GEO 项目；共享原始来源，但不能默认作者选择的细胞与处理结果相同。

## 状态与存放

⏳ 未下载。按 `raw/multiome/` 与 `raw/asap/` 分开登记文件；处理结果放 `processed/`。这些是建议路径，本次未创建数据文件。

## 使用注意

刺激响应、遗传扰动和小分子响应是不同任务。跨实验模态对应关系需要 donor、样本或条码等证据，不能因为同属 GSE156478 就逐行拼接。
