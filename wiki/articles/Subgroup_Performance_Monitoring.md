---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_subgroup_performance_analysis_hidden_stratifications]]"
  - "[[sources/2026-07-06_no_subclass_left_behind_george]]"
  - "[[sources/2026-07-06_domino_systematic_errors_cross_modal_embeddings]]"
  - "[[sources/2026-07-06_underdiagnosis_bias_chest_radiographs]]"
  - "[[sources/2026-07-06_gender_imbalance_medical_imaging_biased_classifiers]]"
  - "[[sources/2026-07-06_how_fair_are_medical_imaging_foundation_models]]"
  - "[[sources/2026-07-06_fairness_beyond_demographics_hidden_cohorts]]"
---

# Subgroup Performance Monitoring

医療AIを安全に使うには，モデル全体の平均性能だけでなく，どの患者群・画像群で性能が落ちるかを継続的に監視する必要がある．Subgroup performance monitoring は，評価データや運用データを subgroup に分け，性能差，最悪群性能，calibration，drift を追跡するための考え方である．

従来の subgroup analysis は，sex，age，ethnicity など既知 metadata による分割に依存する．しかし実際の性能変動は，metadata にない lesion appearance，artifact，image quality，device，label ambiguity，治療状態などで起こることがある．そのため，[[Hidden_Stratification]] を見つけるには，metadata-based analysis に加えて algorithmic subgroup discovery を使う必要がある．

## 監視対象を metadata だけに限定しない

| 分割方法 | 例 | 見つけやすい gap | 見落としやすい gap |
| --- | --- | --- | --- |
| demographic metadata | sex，age，race | 既知属性ごとの fairness gap | phenotype や artifact による gap |
| clinical metadata | comorbidity，device，facility | 既知 clinical context の gap | 未記録の画像特徴 |
| visual trait metadata | lesion color，size，view | annotation された visual factor | annotation されていない hidden factor |
| subgroup discovery | CLIP features，model predictions，clustering | 未知の systematic error | 意味解釈できない cluster |

performance monitoring では，metadata subgroup と discovered subgroup を競合させるのではなく，両方を使う．metadata は解釈しやすく，regulatory reporting に向く．discovered subgroup は，metadata が表していない失敗 mode を見つける補助になる．

metadata subgroup analysis の前提として，dataset 側に patient-level demographic attributes が記録されている必要がある．[[Demographic_Imbalance]] がある場合，training data の majority group に性能が寄り，under-represented group の failure が aggregate metric に隠れる．

## Subgroup discovery を使う流れ

Subgroup discovery は，モデルの failure mode を見つけるために，画像特徴や予測を使って test / validation / deployed data を cluster に分ける．Bissoto et al. の設定では，DOMINO を簡略化して classification labels と metadata を使わず，post-deployment の unlabeled test set でも使えるようにしている．

```text
images
  |
  +--> external feature extractor (CLIP / BiomedCLIP) --> representation
  |
  +--> target model --> softmax predictions
                       |
representation + predictions
                       |
                       v
                 subgroup discovery
                       |
                       v
        subgroup-wise performance report
```

外部 feature extractor は task-agnostic な visual factor や artifact を捉え，target model prediction は分類タスクに関係する要素を反映する．両者を使うことで，単なる visual cluster ではなく，性能差に関係する subgroup を見つけやすくする．

[[DOMINO]] はこの流れを，cross-modal embeddings と error-aware mixture model で実装する代表的手法である．DOMINO は発見した slice に自然言語 description を付けられるため，human auditor が低性能 subgroup の意味を確認する入口として使いやすい．

## 発見した subgroup を改善に使う

monitoring で低性能 subgroup を見つけた後は，その subgroup を training objective に戻すこともできる．GEORGE は，ERM model の feature space を clustering して proxy subclass labels を作り，その cluster assignments を Group DRO の group labels として使う．これにより，true subclass labels がなくても [[Worst_Group_Performance]] を改善できる．

この流れは，subgroup discovery を「監査だけ」に閉じず，data collection，reweighting，Group DRO，targeted augmentation などの改善策へつなぐ設計である．

[[Hidden_Cohort_Fairness]] の LHCF も同じ流れを fairness 文脈に拡張する．LHCF は demographic labels を使わず，image appearance から hidden cohorts を発見し，その cohort labels を sensitive attributes として fairness-aware training に使う．HIDFairBench では，hidden cohorts と demographics の Average Purity が低くても，visible demographic groups と intersectional groups の fairness が改善した．

## 評価指標

Subgroup discovery の目的は，ただ cluster を作ることではない．性能差を露出しつつ，その subgroup が何らかの shared characteristic を持つ必要がある．

| 指標 | 意味 | 注意 |
| --- | --- | --- |
| performance gap | subgroup 間の最高性能と最低性能の差 | 大きいほど failure mode を露出する |
| average purity | subgroup が known attributes とどの程度 align するか | metadata にない factor では低くてもよい |
| worst-group performance | 最低性能 subgroup の性能 | deployment safety に直結する |
| underdiagnosis rate | 疾患ありを no finding と扱う率 | triage や screening で特に重要 |
| subgroup size | subgroup の症例数 | 小さすぎる subgroup は不安定 |
| interpretability | human auditor が subgroup の共通性を説明できるか | actionability に必要 |

performance gap だけを最大化すると，偶然の小集団や incoherent cluster を拾う可能性がある．そのため，purity，subgroup size，human review を併用する．

## Synthetic と real-world の役割

hidden subgroup は実データでは ground truth label が存在しないため，評価が難しい．そのため，synthetic artifact による controlled setting と real-world data の両方が必要になる．

synthetic setting では，artifact を label と相関させ，known artifact と hidden artifact を作ることで，subgroup discovery が本当に hidden subgroup を回収できるかを検証できる．real-world setting では，ground truth がない代わりに，metadata-based subgroup analysis より大きな performance gap を一貫して見つけるか，human review で意味ある subgroup かを確認する．

## 医療画像 fairness での意味

医療画像 fairness では，protected attributes ごとの performance gap を見るだけでは不十分である．性別や人種で stratify して gap が小さくても，特定の lesion color，image artifact，disease subtype，treatment status で大きな gap が残る可能性がある．

Subgroup performance monitoring は，次の2つを同時に満たす必要がある．

| 要件 | 理由 |
| --- | --- |
| known subgroup reporting | 既知の protected attribute / clinical attribute で公平性を確認する |
| hidden subgroup discovery | metadata にない systematic error を検出する |

特に条件付きモデルや multimodal model では，患者属性や tabular data を使うことで一部 subgroup の性能が改善しても，別の hidden subgroup に failure が移る可能性がある．そのため，[[Image_Tabular_Fusion]] や [[HyperFusion]] の評価にも subgroup discovery を組み込むべきである．

胸部 X 線の [[Underdiagnosis_Bias]] のように，known subgroup でも failure direction を明示する必要がある．単に subgroup AUC を見るだけでなく，`no finding` FPR/FNR のような threshold-dependent metrics を追うことで，ある subgroup が選択的に健康扱いされていないかを監視できる．

[[Foundation_Model_Fairness]] では，subgroup monitoring を downstream model だけでなく pre-training stage の選択にも拡張する必要がある．pre-training data source や objective によって，fine-tuning 後にどの sex / race subgroup が underperform するかが変わるためである．

## 運用手順

**Step 1 — 既知 metadata で stratify する**

sex，age，race，facility，device，view，comorbidity など利用可能な metadata で performance report を作る．

**Step 2 — algorithmic subgroup discovery を行う**

external embedding と target model prediction を使い，validation set で subgroup discovery を fit し，test / deployment data に infer する．

**Step 3 — subgroup-wise metric を出す**

accuracy，AUROC，sensitivity，specificity，calibration，worst-group performance を subgroup ごとに計算する．

**Step 4 — human review で共通性を確認する**

低性能 subgroup の画像を review し，artifact，view，severity，label quality，phenotype など説明可能な共通要因を探す．

**Step 5 — 報告と改善に使う**

発見した subgroup を reporting，追加 annotation，retraining，data collection，deployment guardrail に使う．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| subgroup performance monitoring | subgroup ごとの性能を継続的に測定・報告すること |
| subgroup discovery | learned representation や model output から systematic subgroup を探索する手法 |
| performance gap | subgroup 間の最大性能差 |
| average purity | subgroup が既知 attribute とどの程度対応するか |
| hidden stratification | 明示ラベルにない subclass が aggregate metric に隠れる現象 |
| worst-group performance | 最も性能が低い subgroup の performance |

## 関連概念

- [[Hidden_Stratification]]
- [[DOMINO]]
- [[Medical_Image_Fairness]]
- [[Fairness_Evaluation]]
- [[Worst_Group_Performance]]
- [[Underdiagnosis_Bias]]
- [[Demographic_Imbalance]]
- [[Foundation_Model_Fairness]]
- [[Hidden_Cohort_Fairness]]
- [[Image_Tabular_Fusion]]
