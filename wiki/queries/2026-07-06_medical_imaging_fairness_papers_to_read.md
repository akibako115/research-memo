# 医療画像 Fairness 系で最初に raw に入れて読むべき論文

作成日: 2026-07-06

## 背景

この wiki の研究方針は，Hypernetwork や画像 + テーブルデータのマルチモーダル学習を，医療画像分類の subgroup reliability / fairness と接続して整理することである．

まずは医療画像 Fairness 側の土台を作るため，以下の観点が揃う論文を優先して raw に保存する．

- 医療画像モデルでどのような subgroup gap / underdiagnosis が報告されているか
- protected attribute が画像からどの程度推定できてしまうか
- fairness をどの指標・データセット・モデル選択基準で評価するか
- pretraining / fine-tuning protocol が subgroup fairness にどう影響するか
- in-distribution の fairness と external generalization の関係

## 最優先で読む論文

### 1. Underdiagnosis bias of artificial intelligence algorithms applied to chest radiographs in under-served patient populations

- 種別: 論文
- 出版: Nature Medicine, 2021
- URL: https://www.nature.com/articles/s41591-021-01595-0
- raw 保存候補: `raw/papers/2026-07-06_underdiagnosis_bias_chest_radiographs.md`

読む理由:

胸部 X 線診断モデルにおける subgroup ごとの underdiagnosis を直接扱う代表的研究．医療画像 Fairness の問題設定を理解する最初の軸になる．

読後に抽出したい観点:

- underdiagnosis bias の定義
- subgroup の切り方
- 使用データセット
- fairness 指標と臨床的意味
- intersectional subgroup での性能差

### 2. AI recognition of patient race in medical imaging: a modelling study

- 種別: 論文
- 出版: The Lancet Digital Health, 2022
- URL: https://www.thelancet.com/journals/landig/article/PIIS2589-7500(22)00063-2/fulltext
- raw 保存候補: `raw/papers/2026-07-06_ai_recognition_patient_race_medical_imaging.md`

読む理由:

医療画像から race などの protected attribute が推定できてしまうことを示す重要論文．患者属性を条件として明示的に使う研究では，属性が「入れなくても漏れる」問題を把握する必要がある．

読後に抽出したい観点:

- どの modality で protected attribute が推定可能か
- 人間には見えない属性情報をモデルが拾う可能性
- shortcut / leakage との関係
- 属性を使わないモデル設計の限界
- 属性を明示的に使うことのリスクと正当化条件

### 3. MEDFAIR: Benchmarking Fairness for Medical Imaging

- 種別: 論文 / ベンチマーク
- 出版: arXiv, 2022
- URL: https://arxiv.org/abs/2210.01725
- raw 保存候補: `raw/papers/2026-07-06_medfair_benchmarking_fairness_medical_imaging.md`

読む理由:

医療画像 Fairness の評価におけるデータセット，fairness metric，bias mitigation，model selection criterion をまとめて扱うベンチマーク．今後の実験設計の基準にしやすい．

読後に抽出したい観点:

- 使用される fairness 指標
- 対象データセットと modality
- ERM と mitigation 手法の比較
- model selection criterion が fairness に与える影響
- in-distribution / out-of-distribution 評価

### 4. How Fair are Medical Imaging Foundation Models?

- 種別: 論文
- 出版: ML4H / PMLR, 2023
- URL: https://proceedings.mlr.press/v225/khan23a.html
- raw 保存候補: `raw/papers/2026-07-06_how_fair_are_medical_imaging_foundation_models.md`

読む理由:

医療画像 foundation model の subgroup fairness を調べた研究．ImageNet 初期化 ResNet と医療画像 pretraining の比較，pretraining / fine-tuning protocol と fairness の関係を考える材料になる．

読後に抽出したい観点:

- natural image pretraining と medical image pretraining の違い
- overall performance と subgroup fairness の trade-off
- sex / race などの protected attribute ごとの評価
- fine-tuning protocol の影響
- 自分の実験で baseline protocol をどう設計すべきか

## 次に読む論文

### 5. Gender imbalance in medical imaging datasets produces biased classifiers for computer-aided diagnosis

- 種別: 論文
- 出版: PNAS, 2020
- URL: https://www.pnas.org/doi/10.1073/pnas.1919012117
- raw 保存候補: `raw/papers/2026-07-06_gender_imbalance_medical_imaging_biased_classifiers.md`

読む理由:

データセット内の gender imbalance が classifier bias を生むことを示す基本論文．データ分布の偏りと subgroup performance の関係を押さえるために読む．

### 6. The limits of fair medical imaging AI in real-world generalization

- 種別: 論文
- 出版: Nature Medicine, 2024
- URL: https://www.nature.com/articles/s41591-024-03113-4
- raw 保存候補: `raw/papers/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization.md`

読む理由:

in-distribution で公平に見えるモデルが，external test set や real-world generalization でどう振る舞うかを考えるために重要．subgroup reliability を単一データセット内の gap だけで判断しないための材料になる．

### 7. Addressing fairness issues in deep learning-based medical image analysis: a systematic review

- 種別: サーベイ
- 出版: npj Digital Medicine, 2024
- URL: https://www.nature.com/articles/s41746-024-01276-5
- raw 保存候補: `raw/papers/2026-07-06_addressing_fairness_issues_deep_learning_medical_image_analysis.md`

読む理由:

医療画像 Fairness 研究の evaluation / mitigation の分類を作るための地図として使う．個別論文を articles に蒸留するときの概念整理に向いている．

### 8. Addressing fairness in artificial intelligence for medical imaging

- 種別: 論文 / 解説
- 出版: Nature Communications / PMC, 2022
- URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC9357063/
- raw 保存候補: `raw/papers/2026-07-06_addressing_fairness_ai_medical_imaging.md`

読む理由:

fairness の意味，bias の発生源，医療画像 AI における対策の全体像を押さえる導入として有用．用語と問題意識の整理に使う．

## 推奨する読む順

1. Underdiagnosis bias of artificial intelligence algorithms applied to chest radiographs in under-served patient populations
2. AI recognition of patient race in medical imaging: a modelling study
3. MEDFAIR: Benchmarking Fairness for Medical Imaging
4. How Fair are Medical Imaging Foundation Models?
5. Gender imbalance in medical imaging datasets produces biased classifiers for computer-aided diagnosis
6. The limits of fair medical imaging AI in real-world generalization
7. Addressing fairness issues in deep learning-based medical image analysis: a systematic review
8. Addressing fairness in artificial intelligence for medical imaging

最初の 4 本で，医療画像 Fairness の主要な論点である underdiagnosis，protected attribute leakage，評価プロトコル，pretraining の影響を押さえる．

## raw 追加後に作るべき source / article 候補

raw に保存した後は，各論文ごとに `wiki/sources/` へ source を作成する．その後，複数 source を横断して以下の記事候補を育てる．

- `[[Medical_Imaging_Fairness]]`
- `[[Subgroup_Reliability]]`
- `[[Underdiagnosis_Bias]]`
- `[[Protected_Attribute_Leakage]]`
- `[[Fairness_Metrics_for_Medical_Imaging]]`
- `[[Medical_Imaging_Foundation_Model_Fairness]]`
- `[[Dataset_Imbalance_in_Medical_Imaging]]`

## 注意

このリストは raw に原文を保存するための候補であり，この query 自体は一次情報ではない．実際の source / article 作成時には，必ず raw に保存された原文を入力として使う．
