---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_gender_imbalance_medical_imaging_biased_classifiers]]"
  - "[[sources/2026-07-06_ai_recognition_patient_race_medical_imaging]]"
  - "[[sources/2026-07-06_how_fair_are_medical_imaging_foundation_models]]"
---

# Demographic Imbalance

医療画像 dataset で疾患ラベルの分布だけを揃えても，患者属性の分布が偏っていれば，モデルは少数属性群に対して弱くなりうる．Demographic imbalance は，sex，gender，age，race，insurance type など，target label とは別の demographic variable が training data 内で偏っている状態である．

この概念が重要なのは，demographic imbalance が class imbalance とは別の bias source だからである．ある疾患の positive cases が十分あっても，その症例が特定の属性群に偏っていれば，モデルは別の属性群で同じ疾患をうまく検出できない可能性がある．

## Class imbalance との違い

医療画像では，imbalance というと疾患陽性例の少なさを指すことが多い．しかし fairness の観点では，target class と demographic variable を分けて考える必要がある．

| 種類 | 偏るもの | 起こる問題 |
| --- | --- | --- |
| class imbalance | disease label の positive / negative | rare disease の検出性能が落ちる |
| demographic imbalance | sex，age，race などの患者属性 | under-represented group の性能が落ちる |
| joint imbalance | disease label と患者属性の組み合わせ | 特定属性の特定疾患だけ見逃す |

Larrazabal et al. は，pathology ごとの male/female image count を揃えたうえで training gender ratio を変えた．これは，性能低下が disease class distribution ではなく，gender distribution の偏りから生じるかを調べるためである．

## なぜ性能差が生まれるか

CNN は task に有用な visual representation を学習する．しかし患者属性が変わると，画像分布も変わることがある．胸部 X 線では anatomical structure，body habitus，撮影条件，疾患 prevalence，reporting practice などが属性と絡み，model が learned representation を別属性に generalize しにくくなる．

```text
training data の demographic imbalance
  -> learned representation が majority group に寄る
  -> minority group で distribution shift
  -> subgroup performance が低下
```

この失敗は，モデルに protected attribute を入力していなくても起こる．画像自体が demographic information を含む場合，image-only model でも demographic imbalance の影響を受ける．

ただし，[[Race_Recognition_In_Medical_Images]] が示すように，demographic signal は imbalance がなくても画像表現に含まれうる．したがって，demographic imbalance は data distribution の問題，race recognition は image representation が sensitive information を持つ問題として分けて扱う．

## Gender imbalance の実験から分かること

Larrazabal et al. は，NIH ChestX-ray14 と CheXpert を使い，male-only，female-only，25/75%，50/50% の training splits を作った．test は male patients と female patients に分け，AUC で評価した．

| Training condition | 観察された傾向 |
| --- | --- |
| male-only | female test images で性能低下 |
| female-only | male test images で性能低下 |
| 25/75% | minority gender の平均性能が balanced training より低い |
| 50/50% | 両 gender に対して最もよく generalize |

この結果は，単に「majority group の性能が高い」だけでなく，balanced and diverse dataset が両 group の generalization を支えることを示す．

## Dataset documentation の役割

demographic imbalance を評価するには，dataset が patient-level demographic attributes を持っている必要がある．しかし，多くの public medical imaging datasets や challenge datasets では，sex/gender などの情報が明示的に提供されていないことがある．

dataset documentation では，少なくとも次を記録する必要がある．

| 項目 | 理由 |
| --- | --- |
| patient-level demographic distribution | model performance を subgroup ごとに評価するため |
| disease label と demographic attribute の joint distribution | 特定属性で positive case が不足していないか見るため |
| missingness of demographic attributes | missing subgroup が bias を隠す可能性があるため |
| label source | report label や automatic labeler の bias を確認するため |

この記録がないと，[[Subgroup_Performance_Monitoring]] や [[Medical_Image_Fairness_Evaluation]] が後から実行できない．

[[Foundation_Model_Fairness]] では，demographic imbalance は fine-tuning dataset だけでなく pre-training dataset の問題になる．Khan et al. は，medical image pre-training dataset の skewed racial split が downstream race fairness を悪化させ，balanced fine-tuning だけでは完全には消えないことを示した．

## Model selection との関係

demographic imbalance がある dataset で overall AUC だけを最大化すると，validation set の majority group に適合した model が選ばれやすい．そのため，model selection では subgroup AUC，worst group AUC，underdiagnosis rate，calibration を併記する必要がある．

| Selection criterion | demographic imbalance 下のリスク |
| --- | --- |
| overall AUC | majority group に寄った model を選びやすい |
| group gap | gap は小さいが全 group 性能が低い model を選ぶ可能性 |
| worst group performance | minority group の性能低下を検出しやすい |
| subgroup calibration | threshold decision の偏りを検出しやすい |

これは [[Worst_Group_Performance]] と直結する．minority demographic group が最悪群になっている場合，平均性能だけでは実用上の failure を隠す．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| demographic imbalance | target label 以外の患者属性分布が偏っていること |
| gender imbalance | male/female などの gender/sex distribution が偏ること |
| joint imbalance | disease label と demographic attribute の組み合わせが偏ること |
| under-represented group | training data 内で相対的に少ない demographic subgroup |
| balanced dataset | demographic groups が一定以上の比率で含まれる dataset |
| diversity | model が複数 subgroup の variation を学習できる状態 |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Subgroup_Performance_Monitoring]]
- [[Worst_Group_Performance]]
- [[Underdiagnosis_Bias]]
- [[Race_Recognition_In_Medical_Images]]
- [[Foundation_Model_Fairness]]
- [[Bias_Amplification]]
