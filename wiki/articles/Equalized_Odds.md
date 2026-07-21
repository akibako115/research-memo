---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_worst_group_equalized_odds_multi_attribute_medical_image_classification]]"
  - "[[sources/2026-07-06_fairread_demographic_refusion_medical_image_classification]]"
  - "[[sources/2026-07-06_fcro_multiple_sensitive_attributes_medical_image_classification]]"
  - "[[sources/2026-07-06_addressing_fairness_issues_deep_learning_medical_image_analysis]]"
  - "[[sources/2026-07-06_improving_model_fairness_image_based_cad]]"
---

# Equalized Odds

医療画像モデルの subgroup AUC が同じでも，実際の threshold で片方の group は見逃され，別の group は過剰に陽性判定されることがある．Equalized Odds は，subgroup 間で TPR と FPR の両方を揃えることで，operating point 上の診断エラーの偏りを見る fairness criterion である．

この概念が重要なのは，AUC が ranking performance を測る一方，臨床運用では固定 threshold の decision が患者の扱いを決めるからである．同じ AUC でも，ある subgroup では low TPR / low FPR の under-diagnostic pattern，別 subgroup では high TPR / high FPR の over-diagnostic pattern が起こりうる．

## 何を揃えるか

Equalized Odds は，protected subgroup `g` ごとに true positive rate と false positive rate が等しいことを求める．

| Rate | 意味 | 医療画像での読み方 |
| --- | --- | --- |
| TPR | 疾患ありを陽性と判定する率 | sensitivity，見逃しに関係 |
| FPR | 疾患なしを陽性と判定する率 | false alarm，過剰診断に関係 |
| EO gap | subgroup 間の TPR/FPR 差 | operating point 上の fairness gap |

Equalized Opportunity は，このうち TPR 側だけを見る緩い criterion として扱われることが多い．疾患見逃しが主要な害である場合，TPR parity は特に重要になる．

Xu et al. の review では，Equalized Odds は広く使われる group fairness criterion の1つとして整理される．ただし，Demographic Parity，Accuracy Parity，Equalized Odds，Equal Opportunity は同時に満たせない場合があり，臨床 task に対応する harm に合わせて選ぶ必要がある．

## AUC では見えない理由

AUC は threshold-free な ranking 指標である．しかし Equalized Odds は fixed threshold での TPR/FPR を見る．そのため，subgroup AUC が近くても，threshold の位置によって臨床 decision の偏りが出る．

```text
subgroup AUC:
  score ranking 全体を見る

Equalized Odds:
  fixed operating point での TPR/FPR を見る
```

Kurian et al. は，subgroup AUC が aggregate では似ていても，global threshold では一部 subgroup が over-diagnosis，高 TPR・高 FPR，別 subgroup が under-diagnosis，低 TPR・低 FPR を示しうると整理している．

[[Pairwise_Fairness]] は，Equalized Odds と補完関係にある．Equalized Odds が fixed threshold の error parity を見るのに対し，Pairwise Fairness は subgroup positive sample と dataset negative sample の ranking parity を見る．operating point が決まっている診断では EO，score ordering が triage に使われる場合は PFD が有用である．

## Worst-group EO の考え方

multi-attribute setting では，age，sex，race など複数軸の subgroup がある．すべての intersectional constraints を明示的に置くと sample size が小さくなり，constraint 数も増える．Worst-group EO は，mini-batch ごとに最も悪い subgroup を探し，そこに regularization をかける．

| 側 | worst subgroup | 対応する clinical failure |
| --- | --- | --- |
| positive samples | mean predicted probability が最も低い group | low TPR，under-diagnosis |
| negative samples | mean predicted probability が最も高い group | high FPR，over-diagnosis |

この設計では，worst group が age group でも sex group でも race group でもよい．attribute ごとに別々の制約を管理する代わりに，unified subgroup set から最悪の deviation を拾う．

## Logit margin で罰する

Worst-group EO regularization は，worst subgroup の positive samples が all negatives より低い logit を持つこと，または worst subgroup の negative samples が all positives より高い logit を持つことを罰する．

```text
TPR-side violation:
  worst-group positives が negatives より低く score される

FPR-side violation:
  worst-group negatives が positives より高く score される
```

hard min/max ではなく log-sum-exp を使うことで，single outlier だけに依存せず，differentiable な worst-case margin を作る．これは training 中に EO violation を直接小さくする方法であり，post-hoc threshold adjustment とは異なる．

## 医療画像 fairness での使い方

Equalized Odds は，[[Medical_Image_Fairness_Evaluation]] で AUC と並べて見るべき指標である．特に [[Underdiagnosis_Bias]] を見る場合，TPR/FPR の両方を確認しないと，単なる random noise と selective underdiagnosis を区別できない．

| 評価観点 | 見ること |
| --- | --- |
| subgroup AUC | threshold-free discrimination |
| TPR parity | 見逃し率が subgroup 間で偏らないか |
| FPR parity | false alarm / overdiagnosis が subgroup 間で偏らないか |
| EO joint metric | age，race，sex を横断した disparity |
| AUC drop | fairness regularization が診断性能を壊していないか |

EO を改善する方法は fairness-accuracy trade-off を持つ．そのため，model selection では EO gap だけでなく，overall AUC，worst-group AUC，calibration，clinical operating point を同時に見る必要がある．

[[FairREAD]] は，subgroup-specific threshold によって EO disparity を下げる例である．Min-gap strategy は subgroup ごとに TPR と TNR の差が小さい threshold を選び，CheXpert 実験で default threshold より Delta EO と FATE_EO を改善した．ただし subgroup threshold は，deployment 時に demographic attributes が利用可能であることを前提にする．

[[FCRO]] は，representation learning 側から Equalized Odds disparity を下げる例である．Race，Sex，Age の conjunction subgroup に対して Joint Delta ED を計算し，target representation と sensitive representation の orthogonality によって disparity を抑える．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| Equalized Odds | subgroup 間で TPR と FPR の両方を揃える fairness criterion |
| Equalized Opportunity | subgroup 間で主に TPR を揃える criterion |
| TPR-side violation | 疾患あり subgroup の sensitivity が低い状態 |
| FPR-side violation | 疾患なし subgroup の false positive が高い状態 |
| worst-group EO | 最も EO violation が大きい subgroup を対象にする考え方 |
| operating point | threshold を固定した臨床 decision point |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Worst_Group_Performance]]
- [[Underdiagnosis_Bias]]
- [[Demographic_Imbalance]]
- [[Subgroup_Performance_Monitoring]]
- [[FairREAD]]
- [[FCRO]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Pairwise_Fairness]]
- [[Subgroup_Separability]]
