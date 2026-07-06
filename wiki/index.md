# Wiki Index

## Reading Paths

### Path 1: 医療画像 Fairness の全体像

医療画像で何が不公平になるか → どう測るか → どう直すか → 何が未解決か．

1. [[Medical_Image_Fairness_Evaluation]] — 評価指標の全体像
2. [[Underdiagnosis_Bias]] — 最も臨床的に危険な失敗方向
3. [[Equalized_Odds]] — threshold-based fairness の基本
4. [[Pairwise_Fairness]] — ranking fairness
5. [[Demographic_Imbalance]] — bias source としてのデータ不均衡
6. [[Race_Recognition_In_Medical_Images]] — 画像から属性が漏れる問題
7. [[Worst_Group_Performance]] — 最悪群性能の最適化
8. [[Fairness_Mitigation_In_Medical_Imaging]] — 介入手法の整理
9. [[Fairness_Under_Distribution_Shift]] — ID fairness の限界

### Path 2: Hidden subgroup と監視

known subgroup を超えた failure mode の発見と監視．

1. [[Hidden_Stratification]] — 問題提起
2. [[DOMINO]] — embedding-based slice discovery
3. [[Subgroup_Performance_Monitoring]] — 継続的監視の枠組み
4. [[Hidden_Cohort_Fairness]] — hidden cohort を fairness optimization に使う

### Path 3: 条件付きモデルと画像+テーブル融合

患者属性を明示的に使う条件付きモデルの技術と fairness への接続．

1. [[FiLM]] — feature-wise affine modulation の基本形
2. [[DAFT]] — image + tabular の two-way exchange
3. [[Metadata_Conditioning]] — 医療画像 segmentation への応用
4. [[Hypernetwork]] — 重み生成の一般概念
5. [[HyperFusion]] — hypernetwork による画像+テーブル融合
6. [[Image_Tabular_Fusion]] — 融合方式の比較と使い分け

### Path 4: Foundation model と fairness

事前学習済みモデルの fairness 問題．

1. [[Foundation_Model_Fairness]]
2. [[Vision_Language_Model_Fairness]]

## Articles

### 医療画像 Fairness: 評価

- [[Medical_Image_Fairness_Evaluation]]
- [[Equalized_Odds]]
- [[Pairwise_Fairness]]
- [[Worst_Group_Performance]]
- [[Underdiagnosis_Bias]]
- [[Demographic_Imbalance]]

### 医療画像 Fairness: 介入・緩和

- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[FairREAD]]
- [[FCRO]]
- [[Hidden_Cohort_Fairness]]

### Subgroup 発見・監視

- [[Hidden_Stratification]]
- [[DOMINO]]
- [[Subgroup_Performance_Monitoring]]

### Robustness・Distribution Shift・Foundation Model

- [[Fairness_Under_Distribution_Shift]]
- [[Foundation_Model_Fairness]]
- [[Vision_Language_Model_Fairness]]
- [[Race_Recognition_In_Medical_Images]]

### 条件付きモデル・画像+テーブル融合

- [[FiLM]]
- [[DAFT]]
- [[Hypernetwork]]
- [[HyperFusion]]
- [[Metadata_Conditioning]]

## Synthesis

- [[Medical_Image_Fairness_Audit_Loop]] — fairness 監査を loop として統合
- [[Image_Tabular_Fusion]] — 融合方式の比較と使い分け

## Article Backlog

参照数が多く，独立記事として作成すべき未作成概念．

| 概念 | 参照数 | 備考 |
|---|---|---|
| [[Conditional_Modulation]] | 12 | FiLM / Hypernetwork / Metadata_Conditioning の上位概念．conditioning 系の技術を束ねる記事 |
| [[Fairness_Evaluation]] | 8 | 一般的な fairness 評価の枠組み．Medical_Image_Fairness_Evaluation の上位概念の可能性 |
| [[Bias_Amplification]] | 6 | データ不均衡やモデル学習でバイアスが増幅される現象 |
| [[Subgroup_Reliability]] | 6 | subgroup 単位の信頼性．Worst_Group_Performance と補完的 |
| [[Spurious_Correlation]] | 4 | shortcut learning / confounding の概念 |
| [[Algorithmic_Subgroup_Discovery]] | 4 | DOMINO / GEORGE 系の手法を束ねる概念 |
| [[Intersectional_Fairness]] | 3 | 複数属性の交差による fairness |
