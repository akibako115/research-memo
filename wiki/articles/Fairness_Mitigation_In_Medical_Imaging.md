---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_addressing_fairness_issues_deep_learning_medical_image_analysis]]"
  - "[[sources/2026-07-06_fairness_beyond_demographics_hidden_cohorts]]"
  - "[[sources/2026-07-06_improving_model_fairness_image_based_cad]]"
  - "[[sources/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization]]"
---

# Fairness Mitigation In Medical Imaging

医療画像の fairness mitigation は，subgroup gap を見つけた後に，data，model，deployment のどこへ介入するかを選ぶ設計問題である．単に fairness loss を足すだけではなく，bias source が data distribution，annotation noise，anatomical difference，spurious correlation，pre-training bias，domain gap のどれかを切り分けてから，対応する mitigation を選ぶ必要がある．

この概念が重要なのは，医療画像では「数値上の parity」がそのまま臨床的 equity にならないからである．疾患 prevalence や診断難易度が subgroup ごとに違う場合，Demographic Parity のような指標を機械的に満たすことは，医学的に不自然な decision boundary を作る可能性がある．

## 介入箇所

fairness mitigation は，モデル学習 pipeline のどこに介入するかで大きく3つに分かれる．

| Stage | 介入 | 代表例 |
| --- | --- | --- |
| pre-processing | training data / input を変える | re-distribution，harmonization，aggregation，synthesis |
| in-processing | training objective / architecture を変える | adversarial learning，constraints，disentanglement，contrastive learning |
| post-processing | trained model の output / parameter を変える | calibration，subgroup threshold，pruning |

pre-processing は実装しやすいが，data artifact や label noise を残すことがある．in-processing は representation を直接変えられるが，optimization が不安定になりやすい．post-processing は既存モデルに適用しやすいが，deployment 時に subgroup attribute が必要になる場合がある．

## Pre-processing

pre-processing は，model training 前に dataset や input image を調整する．

| Method | 何をするか | リスク |
| --- | --- | --- |
| re-distribution | subgroup resampling / balanced mini-batch | rare subgroup の overfitting |
| harmonization | sensitive information を除去・正規化 | clinically relevant signal も消す可能性 |
| aggregation | external dataset や EHR を追加 | source domain の bias を持ち込む |
| synthesis | generative model で counterfactual / minority samples を作る | synthetic artifact や causal validity の問題 |

re-distribution は [[Demographic_Imbalance]] に直接対応するが，subgroup ratio を揃えるだけでは，annotation preference や image quality difference は解決しない．harmonization は dermatology の skin region removal や normalization，ComBat，differential privacy などを含むが，医療画像では sensitive signal と disease signal が絡み合うため，除去が常に安全とは限らない．

## In-processing

in-processing は，training 中に architecture や loss を変更する．

| Method | 目的 | 注意点 |
| --- | --- | --- |
| adversarial learning | latent space から sensitive attribute を予測しにくくする | sensitive information の完全除去は難しい |
| fairness constraints | GroupDRO，EqOdds proxy，margin loss などで gap を罰する | constraint choice に依存し，overfitting しうる |
| disentanglement | task-related / task-agnostic feature を分ける | 分離が本当に causal か検証が必要 |
| contrastive learning | same class / different attribute の距離を縮める | class と attribute の相関が強いと崩れる |
| adapters / PEFT | pre-trained model を小さく調整する | foundation model では評価範囲が広い |
| marginal ranking loss | worst subgroup の ranking fairness を直接改善する | calibration は別途評価が必要 |

fairness constraints は，単独属性では良く見えても，intersectional subgroup で破綻することがある．これは fairness gerrymandering と呼ばれ，sex と age それぞれでは fair でも sex x age では unfair になるような失敗である．したがって，in-processing method の評価では [[Subgroup_Performance_Monitoring]] と intersectional audit が必要になる．

[[Hidden_Cohort_Fairness]] は，visible demographic attributes ではなく，appearance-based hidden cohorts を group として fairness loss をかける in-processing approach と見なせる．これは demographic labels が欠けている場合や，intersectional group が sparse になる場合の代替になる．ただし，cluster の安定性，cohort size，human interpretability は別途監査する必要がある．

[[Pairwise_Fairness]] を使う mitigation では，batch ごとに最も Pairwise Fairness が低い subgroup を選び，positive sample が negative sample より高く rank されるように marginal ranking loss をかける．これは risk score ordering を直接改善するため，triage や prioritization を想定した CAD で使いやすい．

ただし，[[Fairness_Under_Distribution_Shift]] の観点では，ID で fairness gap を下げる mitigation が OOD で同じ効果を持つとは限らない．DANN のように demographic encoding を減らす方法は OOD fairness で有利な場合があるが，demographic signal が causal factor の proxy である場合には完全除去が望ましくないこともある．

## Post-processing

post-processing は，学習済み model の output や parameter を調整する．

| Method | 何をするか | 前提 |
| --- | --- | --- |
| calibration | subgroup ごとに threshold / output を調整する | deployment 時に subgroup attribute が必要 |
| reject option | decision boundary 付近で unprivileged group の output を変更する | operating point の妥当性が必要 |
| pruning | fairness に関わる neuron / feature を削る | performance degradation の監査が必要 |

subgroup-specific threshold は [[Equalized_Odds]] や Equal Opportunity を改善しやすいが，患者属性を inference 時に使う運用上の妥当性が必要である．また，threshold を subgroup ごとに変える場合，calibration と patient-level safety を同時に確認する必要がある．

## Bias source に合わせる

mitigation は，発見された bias source に対応して選ぶ．

| Bias source | 起きる場所 | 合う介入 |
| --- | --- | --- |
| skewed distribution | data | re-distribution，data augmentation |
| anatomy difference | data / clinical reality | causal image synthesis，clinical review |
| annotation noise | data / labeling | multi-annotator，label audit |
| ERM-based selection | model selection | DTO，minimax，worst-group selection |
| spurious correlation | model | confounder removal，shortcut testing |
| inherited bias | pre-training / deployment | model pruning，foundation model audit |
| domain gap | deployment | domain adaptation，external validation |

重要なのは，performance disparity が常に unfairness とは限らない点である．疾患 prevalence や anatomy が subgroup によって異なる場合，差が causal / clinically justified なのか，access / annotation / model shortcut 由来なのかを分ける必要がある．

## Foundation model での難しさ

医療画像 foundation models は，pre-training dataset が非公開または巨大で，再学習が難しいことが多い．そのため，従来の resampling や adversarial retraining をそのまま使いにくい．

| Foundation model の問題 | Mitigation の方向 |
| --- | --- |
| pre-training data の bias が見えにくい | downstream subgroup audit と embedding audit |
| model size が大きい | adapters，PEFT，feature perturbation |
| prompt が behavior を変える | prompt audit，prompt-based intervention |
| modality / site domain gap | external validation，domain adaptation |

[[Foundation_Model_Fairness]] と [[Vision_Language_Model_Fairness]] では，fine-tuning 後の subgroup metric だけでなく，pre-training data，prompt，embedding，zero-shot findings を含めて fairness を見る必要がある．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| fairness mitigation | subgroup disparity を減らすための介入 |
| pre-processing | model training 前に data / input を調整する方法 |
| in-processing | training objective / architecture に fairness を組み込む方法 |
| post-processing | trained model の output / parameter を調整する方法 |
| fairness gerrymandering | 単独属性では公平でも組み合わせ subgroup で不公平になること |
| clinical fairness | 数理指標だけでなく，臨床的因果関係と治療 equity を含めた公平性 |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Equalized_Odds]]
- [[Demographic_Imbalance]]
- [[Foundation_Model_Fairness]]
- [[Vision_Language_Model_Fairness]]
- [[Subgroup_Performance_Monitoring]]
- [[Hidden_Cohort_Fairness]]
- [[Pairwise_Fairness]]
- [[Fairness_Under_Distribution_Shift]]
