---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_medfair_benchmarking_fairness_medical_imaging]]"
  - "[[sources/2026-07-06_underdiagnosis_bias_chest_radiographs]]"
  - "[[sources/2026-07-06_gender_imbalance_medical_imaging_biased_classifiers]]"
  - "[[sources/2026-07-06_ai_recognition_patient_race_medical_imaging]]"
  - "[[sources/2026-07-06_worst_group_equalized_odds_multi_attribute_medical_image_classification]]"
  - "[[sources/2026-07-06_fairread_demographic_refusion_medical_image_classification]]"
  - "[[sources/2026-07-06_fcro_multiple_sensitive_attributes_medical_image_classification]]"
  - "[[sources/2026-07-06_how_fair_are_medical_imaging_foundation_models]]"
  - "[[sources/2026-07-06_demographic_bias_vision_language_foundation_models_medical_imaging]]"
  - "[[sources/2026-07-06_addressing_fairness_issues_deep_learning_medical_image_analysis]]"
  - "[[sources/2026-07-06_improving_model_fairness_image_based_cad]]"
  - "[[sources/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization]]"
---

# Medical Image Fairness Evaluation

医療画像モデルの公平性を評価するとき，単に「患者群ごとの差が小さいか」だけを見ると，臨床的に重要な失敗を見落とすことがある．診断では，どの患者群でも一定以上の性能を守ることが重要な場面が多い．差を小さくするために，もともと性能が高かった群の性能を下げるだけでは，患者にとって有害になりうる．

医療画像の公平性評価は，平均的な診断性能，患者群ごとの性能差，最も弱い患者群の性能，確率の信頼性，施設や装置が変わったときの崩れ方を同時に見る評価設計である．ここでいう患者群は，性別，年齢，人種，保険種別，またはそれらの組み合わせで分けた集団を指す．

MEDFAIR の重要な示唆は，公平化手法の比較以前に，**どの基準でモデルを採用するか自体が，公平性の結論を大きく変える**という点である．同じ学習手法でも，平均 AUC が最も高いモデルを選ぶのか，最も低性能な患者群を守るモデルを選ぶのかで，評価結果は変わる．医療画像の公平性では，学習手法，データセット，患者群の分け方，評価指標，モデル選択基準，外部データでの評価を揃えて比較しないと，実用的な結論は出しにくい．

## 評価の3軸

MEDFAIR は，医療画像の公平性を次の3軸で評価する．

| 軸 | 指標 | 何を見るか |
| --- | --- | --- |
| 平均的な診断性能 | 全体 AUC | 患者全体で診断性能が高いか |
| 患者群間の公平性 | AUC gap | 患者群の間で性能差が小さいか |
| 最悪群の保護 | worst-case group AUC | 最も低性能な患者群が守られているか |

この3軸は同じではない．患者群間の AUC 差を小さくしても，両群の性能が下がれば臨床的には悪化する．逆に最も弱い患者群の AUC を上げても，別の群との差が広がる場合がある．どちらを優先するかは，診断，トリアージ，限られた医療資源の配分などの用途に依存する．

## 患者群間の差を見るか，最悪群を守るか

患者群間の公平性は，保護すべき患者群の間で「予測性能が同じくらいであること」を求める考え方である．たとえば ICU のベッド，専門医の診察枠，追加検査の優先順位のように，限られた医療資源を割り当てる場面では，ある患者群だけが一貫して不利にならないよう，患者群間の差を減らすことが重要になる．

一方，Max-Min fairness は，最も性能が低い患者群の診断性能をできるだけ高くする考え方である．医療画像診断では，全患者群に対して最低限の安全性を守る必要があるため，最悪群の AUC は特に重要になる．

```text
患者群間の公平性:
  患者群どうしの性能差を小さくする

Max-Min fairness:
  最も性能が低い患者群の性能を高くする
```

この違いを明示しないと，「公平性が改善した」という主張が，実際には高性能だった患者群を悪化させただけなのか，低性能だった患者群を改善したのかが分からない．前者は差を小さくしていても，臨床的には望ましくない．

## モデルの選び方も評価対象に含める

公平性評価では，学習手法だけでなく，ハイパーパラメータや early stopping の基準も評価対象に含める必要がある．同じ通常学習（ERM）でも，全体 AUC で選ぶか，最悪群 AUC で選ぶか，平均性能と公平性の両方を見て選ぶかによって，公平性の結論が変わる．

| モデル選択基準 | 選ぶもの | リスク |
| --- | --- | --- |
| 全体性能で選ぶ | 検証データ全体で最も AUC が高いモデル | 多数派や簡単な患者群に寄る |
| minimax Pareto | 平均性能と公平性の候補集合の中で，最悪群 AUC が最も高いモデル | 患者群ごとの指標が不安定だと選択も不安定になる |
| DTO-based | 全患者群が理想的に高性能だった場合に最も近いモデル | 理想点の置き方に依存する |

ERM は empirical risk minimization の略で，訓練データ全体の平均誤差を小さくする通常の学習を指す．MEDFAIR では，この通常学習でも minimax Pareto selection を使うだけで最悪群 AUC が改善し，全体 AUC は有意に悪化しなかった．これは，公平化手法を追加する前に，モデル選択方針を固定・報告する必要があることを示す．

## In-distribution と OOD

医療画像モデルは，training data と同じ施設・装置・集団でだけ使われるとは限らない．そのため，in-distribution fairness と out-of-distribution fairness を分けて評価する．

| 設定 | 意味 | 例 |
| --- | --- | --- |
| in-distribution | train / test が同じ domain から来る | CheXpert 内 split |
| out-of-distribution | train domain と test domain が異なる | CheXpert で train，MIMIC-CXR で test |

OOD では，overall performance だけでなく subgroup gap や worst-case group AUC も崩れる可能性がある．MEDFAIR では，in-distribution で rank が良い method が unseen domain で悪化する場合があり，fairness を domain shift 下で保つ難しさが示された．

[[Fairness_Under_Distribution_Shift]] は，この問題をさらに強く示す．Yang et al. は，ID と OOD の overall AUROC は高く相関する一方，ID fairness と OOD fairness は一貫して相関しないことを示した．したがって，ID fairness gap が小さい model を選ぶだけでは deployment fairness を保証できない．

## 評価指標セット

医療画像 fairness 評価では，AUC だけでなく，threshold-dependent metrics と calibration も見る必要がある．

| 指標 | 役割 |
| --- | --- |
| subgroup AUC | threshold に依存しない discrimination |
| AUC gap | subgroup 間の discrimination disparity |
| worst-case AUC | 最低 subgroup の discrimination |
| FPR / FNR | false alarm / underdiagnosis の subgroup 差 |
| TPR at fixed TNR | 臨床運用点に近い sensitivity |
| EqOdd | [[Equalized_Odds]]，TPR / FPR の subgroup parity |
| PFD | [[Pairwise_Fairness]]，ranking fairness の subgroup gap |
| ECE | subgroup calibration / sufficiency の確認 |
| BCE | training objective と probabilistic quality |

特に [[Underdiagnosis_Bias]] は医療画像 fairness で重要である．同じ AUC でも threshold や calibration が異なると，実際に「疾患ありを no finding と扱う率」は subgroup 間で大きくずれる．

Xu et al. の systematic review は，Demographic Parity，Accuracy Parity，[[Equalized_Odds]]，Equal Opportunity のような group fairness criteria は互いに矛盾しうるため，task に応じて選ぶ必要があると整理している．また，sex では fairness criterion を満たしても race では満たさないように，grouping scheme の選び方で結論が変わる．

## 数理的 fairness と臨床的 fairness

医療画像では，metric の numerical parity がそのまま clinical equity を意味しない．たとえば Demographic Parity は subgroup ごとの positive prediction rate を揃えるが，疾患 prevalence が age や sex と医学的に関係する場合，この要求は実世界の morbidity と衝突しうる．

したがって，fairness metric を選ぶときは，次を明示する必要がある．

| 問い | 確認すること |
| --- | --- |
| どの属性を sensitive attribute とするか | 統計的相関だけでなく，臨床的因果関係も考える |
| どの metric を採用するか | DP，AP，EqOdds，EqOpp のどれが clinical harm に対応するか |
| どの程度の差を unfairness と呼ぶか | subgroup size，confidence interval，臨床上許容できる差を併記する |
| disparity は害か，医学的差か | anatomy，prevalence，annotation practice を切り分ける |

## Underdiagnosis を別枠で評価する

胸部 X 線のような multi-label classification では，`no finding` prediction が臨床 triage に使われる可能性がある．この場合，疾患を持つ患者に `no finding` を出す失敗は，単なる false negative ではなく，受診優先度や治療開始を遅らせる underdiagnosis になる．

| 指標 | 意味 | なぜ必要か |
| --- | --- | --- |
| `no finding` FPR | 疾患ありを no finding と予測する率 | underdiagnosis rate に対応する |
| `no finding` FNR | no finding 症例を疾患あり方向に予測する率 | random noise と selective underdiagnosis を区別する |
| intersectional FPR | 複数属性 subgroup の underdiagnosis | 単独属性では見えない bias を検出する |
| FDR of `no finding` | no finding 予測時に実際は疾患ありの確率 | no finding prediction の臨床リスクを測る |

Seyyed-Kalantari et al. は，CXR，CXP，NIH，ALL の胸部 X 線 dataset で，female patients，younger patients，Black patients，Hispanic patients，Medicaid insurance の患者などが選択的に underdiagnosed されることを示した．これは，fairness 評価では subgroup AUC だけでなく，臨床 decision threshold 上の失敗方向を明示する必要があることを示す．

Kurian et al. は，fixed operating point では，ある subgroup が高 TPR・高 FPR の over-diagnostic pattern を示し，別 subgroup が低 TPR・低 FPR の under-diagnostic pattern を示すことがあり，aggregate AUC ではこの差が隠れると整理している．このため，multi-attribute fairness では Age，Race，Sex の joint EOdds / EOM を AUC と一緒に見る必要がある．

## Bias source を記録する

MEDFAIR は bias source を label noise，class imbalance，data imbalance，spurious correlation に分けて整理している．fairness gap を見つけた後は，どの bias source が原因かを考える必要がある．

| Bias source | 医療画像での例 |
| --- | --- |
| label noise | subgroup ごとに report label の質が違う |
| class imbalance | ある属性群に positive case が少ない |
| data imbalance | dataset が特定 population に偏る |
| demographic imbalance | target label とは別の患者属性が偏る |
| spurious correlation | device，scanner，treatment artifact が label と相関する |

この整理は [[Hidden_Stratification]] ともつながる．demographic subgroup だけでなく，label quality や artifact による hidden subgroup も fairness gap を作る．

[[Demographic_Imbalance]] は，class imbalance と分けて扱う必要がある．Larrazabal et al. は，pathology ごとの male/female count を揃えたうえで gender ratio を変え，25%/75% imbalance でも minority gender の性能が balanced training より低下することを示した．そのため fairness 評価では，disease label の分布だけでなく，patient attribute と disease label の joint distribution を記録する必要がある．

[[Race_Recognition_In_Medical_Images]] は，protected attribute を入力から外すだけでは fairness を保証できないことを示す．Gichoya et al. は，chest X-ray，CT，mammography などの pixel data だけから self-reported race が高 AUC で予測でき，BMI，disease labels，tissue density などでは説明しきれないことを示した．したがって，fairness 評価では race を model input から除くかどうかではなく，race subgroup ごとの outcome を監査する必要がある．

[[FairREAD]] は，この問題に対して「除去して終わり」ではなく「除去した後に controlled に再注入する」設計を取る．このような fairness-aware fusion では，AUC，Delta EO，Delta AUC，OOD fairness，subgroup-specific threshold の安全性を同時に見る必要がある．

[[FCRO]] は，複数 sensitive attributes を single compact sensitive representation にまとめ，target representation と orthogonal にすることで joint disparity を下げる．このような手法では，Race，Sex，Age の individual disparity だけでなく，それらの conjunction による joint disparity を必ず評価する必要がある．

[[Foundation_Model_Fairness]] では，fine-tuning 後の downstream metric だけでなく，pre-training data source，pre-training objective，pre-training data volume も評価対象になる．Khan et al. は，medical image pre-training が AUC を上げる一方で natural image pre-training より subgroup fairness を悪化させることを示した．これは，foundation model の fairness を downstream dataset balancing だけで保証できないことを示す．

[[Vision_Language_Model_Fairness]] では，zero-shot / self-supervised training でも underdiagnosis bias が残るかを見る必要がある．Yang et al. は，CheXzero が radiologists と同等以上の AUROC を示しても，sex，age，race，intersectional subgroup で radiologists より大きな underdiagnosis disparity を示すことを報告した．VLM では，prompt template，unseen radiographic findings，embedding からの demographic attribute prediction も評価対象に含める．

[[Fairness_Mitigation_In_Medical_Imaging]] は，fairness gap を見つけた後に，data，model，deployment のどこへ介入するかを選ぶ taxonomy である．評価時には，mitigation method の種類だけでなく，bias source，clinical justification，intersectional subgroup での残存 gap を記録する必要がある．

[[Pairwise_Fairness]] は，fixed threshold の TPR/FPR ではなく，subgroup positive cases が dataset-wide negative cases より高く rank されるかを見る．Lin et al. は，marginal ranking loss により PFD を多くの条件で35%以上下げつつ，AUC の変化を多くの場合1%以内に抑えた．risk score を triage や prioritization に使う CAD では，PFD を AUC / EqOdds / calibration と併用する価値がある．

[[Fairness_Under_Distribution_Shift]] では，demographic encoding と fairness gap の関係も評価対象になる．ID data だけで OOD deployment 用の model を選ぶ場合，minimum ID fairness gap よりも，representation から sensitive attributes が予測しにくい model を選ぶ方が OOD fairness に有利な場合がある．

## 条件付きモデルの評価に使う

患者属性や EHR を使う [[Image_Tabular_Fusion]] / [[HyperFusion]] モデルは，subgroup reliability を改善する可能性がある一方，protected attribute 依存を強める可能性もある．評価では次を最低限見る．

| 比較 | 見ること |
| --- | --- |
| image-only vs attribute-conditioned | worst-case AUC が改善するか |
| known subgroup vs discovered subgroup | metadata にない failure が残るか |
| ID vs OOD | 外部 dataset でも fairness 改善が残るか |
| group gap vs worst-case | leveling down ではなく worst group が改善しているか |
| calibration | subgroup ごとの threshold decision が安全か |

## リファレンス

| 用語 | 意味 |
| --- | --- |
| subgroup | 性別，年齢，人種などで分けた患者群 |
| sensitive attribute | 公平性を監査するために使う患者属性．例: sex，age，race |
| group fairness | 患者群間の性能差を小さくする公平性 |
| Max-Min fairness | 最も性能が低い患者群の性能を最大化する公平性 |
| utility | モデルの診断性能．この記事では主に AUC を指す |
| ERM | 訓練データ全体の平均誤差を小さくする通常学習 |
| AUC gap | 患者群ごとの AUC の最大値と最小値の差 |
| worst-case AUC | 最も低い患者群 AUC |
| leveling down | 高性能な群を悪化させて，見かけ上の差だけを小さくすること |
| minimax Pareto selection | 平均性能と公平性の候補集合の中で，最悪群 AUC が最大のモデルを選ぶ方法 |
| DTO selection | 患者群ごとの性能が理想点にどれだけ近いかでモデルを選ぶ方法 |
| clinical fairness | 数理指標だけでなく，疾患 prevalence や臨床的因果関係を含めた公平性 |
| PFD | Pairwise Fairness Difference，ranking fairness の subgroup 間差 |
| OOD fairness | 施設，装置，患者集団が変わっても患者群ごとの公平性が保たれるかの評価 |

## 関連概念

- [[Worst_Group_Performance]]
- [[Subgroup_Performance_Monitoring]]
- [[Hidden_Stratification]]
- [[Underdiagnosis_Bias]]
- [[Equalized_Odds]]
- [[Demographic_Imbalance]]
- [[Race_Recognition_In_Medical_Images]]
- [[FairREAD]]
- [[FCRO]]
- [[Foundation_Model_Fairness]]
- [[Vision_Language_Model_Fairness]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Pairwise_Fairness]]
- [[Fairness_Under_Distribution_Shift]]
- [[Image_Tabular_Fusion]]
- [[HyperFusion]]
