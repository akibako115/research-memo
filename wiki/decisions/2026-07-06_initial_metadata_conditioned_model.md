---
created: 2026-07-06
updated: 2026-07-06
---

# 最初の医療画像 + メタデータ条件付きモデルは軽量 modulation から始める

## Context

研究テーマは，患者属性や臨床メタデータを明示的に使う条件付きモデルが，医療画像分類の subgroup fairness / reliability に与える影響を調べることである．

この段階で必要なのは，最も表現力の高い hypernetwork を最初から作ることではなく，比較しやすく，説明しやすく，ablation しやすい初期モデルを作ることである．

## Decision

最初の研究モデルは，full hypernetwork ではなく，ImageNet 初期化 ResNet-50 に小さな metadata encoder を接続した lightweight conditional modulation とする．

主軸モデルは次の構成にする．

```text
image ── ImageNet pretrained ResNet-50 ── feature ── classifier ── prediction
                         ↑
metadata ── metadata MLP ── gamma, beta
```

最初の本命モデルは，stage4-only FiLM / DAFT-like modulation とする．

## Model Progression

実験は，単純なモデルから複雑なモデルへ段階的に進める．

1. ResNet-50 end-to-end baseline
   - ImageNet pretrained
   - backbone は freeze しない
   - metadata は使わない

2. Late fusion baseline
   - image feature と metadata embedding を concat して classifier に入れる
   - 条件付き modulation の比較対象にする

3. FC-only modulation
   - 最終分類器または分類直前 feature だけを metadata で条件付ける
   - 属性を入れるだけで subgroup fairness が変わるかを見る最小モデルにする

4. Stage4-only FiLM / DAFT-like modulation
   - ResNet stage4 の高次特徴だけを metadata で affine modulation する
   - 初期研究モデルの主役にする

5. Stage3+4 modulation
   - 中高次特徴まで条件付ける
   - stage4-only で効果が見えた後の拡張にする

6. HyperAdapter / HyperFusion-like model
   - selected layers の weight / bias generation や per-sample adapter を使う
   - 強い複雑モデル，比較対象，上限モデルとして扱う

## Metadata Encoding

メタデータは，まず確立した素朴な表現に落とし，小さな MLP で embedding 化する．

```text
categorical attributes -> one-hot encoding
continuous attributes  -> z-score normalization
missingness            -> binary missing indicator
concat                 -> 2-layer MLP -> metadata embedding
```

初期設定:

- categorical attributes: sex，race，ethnicity，insurance などは one-hot encoding
- continuous attributes: age，BMI，検査値などは training set statistics で z-score normalization
- ordinal attributes: まず数値化し，必要なら embedding table と比較する
- missing values: 単純な 0 埋めだけにせず，missing indicator を追加する
- metadata encoder: 2-layer MLP
- metadata embedding dimension: 64 または 128
- regularization: dropout と weight decay

FiLM / DAFT-like modulation では，metadata embedding から affine parameter を生成する．

```text
gamma, beta = Linear(metadata_embedding)
feature' = gamma * feature + beta
```

## Rationale

- stage4-only modulation は，高次特徴だけを条件付けるため，属性ごとの別モデル化になりにくく，説明しやすい．
- late fusion，FC-only，stage4-only の順に比較すれば，どの複雑度から subgroup fairness / reliability が変わるかを切り分けやすい．
- full hypernetwork や per-sample convolution weight generation は表現力が高い一方で，公平性改善なのか group-specific specialization なのかが曖昧になりやすい．
- frozen backbone + adapter only を主 protocol にすると，baseline checkpoint の品質，学習 budget，adapter の効果の切り分けが複雑になる．
- 医療画像 + tabular data の既存研究でも，DAFT や FiLM 系は metadata encoder MLP から affine parameter を生成する設計を採っており，最初の比較基準として妥当である．

## Avoid Initially

初期モデルでは次を避ける．

- 全層 HyperAdapter
- per-sample convolution weight generation
- frozen backbone + adapter only を主 protocol にすること
- HyperFusion 風の selected conv weight generation を最初から主役にすること
- Transformer encoder for metadata
- 大きすぎる metadata embedding dimension
- metadata だけで強い予測器を作れるほど深い MLP
- race，sex，site ID などを無制限に強く使わせる設計
- missing indicator なしの単純な欠損値 0 埋め

## Review Conditions

次の場合は，初期モデル方針を見直す．

- stage4-only modulation では改善がなく，stage3+4 または selected weight generation でのみ一貫した改善が出た場合
- metadata 欠損や施設差により，単純な MLP encoding が不安定だと分かった場合
- モデル解析で，metadata conditioning が疾患関連特徴ではなく protected attribute shortcut を強めていると示された場合
- fairness 改善が known subgroup では見えるが latent subgroup / hidden cohort で悪化する場合
