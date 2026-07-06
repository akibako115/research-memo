---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_no_subclass_left_behind_george]]"
  - "[[sources/2026-07-06_subgroup_performance_analysis_hidden_stratifications]]"
  - "[[sources/2026-07-06_medfair_benchmarking_fairness_medical_imaging]]"
  - "[[sources/2026-07-06_underdiagnosis_bias_chest_radiographs]]"
  - "[[sources/2026-07-06_gender_imbalance_medical_imaging_biased_classifiers]]"
  - "[[sources/2026-07-06_worst_group_equalized_odds_multi_attribute_medical_image_classification]]"
---

# Worst Group Performance

医療画像モデルの平均性能が高くても，最も性能が低い患者群や疾患 subclass で失敗するなら，臨床安全性は保証されない．Worst group performance は，subgroup ごとの性能のうち最悪値を明示的に評価・改善する考え方である．

これは，平均性能を最大化する ERM とは違う目的を持つ．ERM は多数派や簡単な subgroup に引っ張られ，rare，subtle，clinically important な subgroup を under-serve しやすい．worst group performance を見ることで，[[Hidden_Stratification]] や fairness gap が aggregate metric に隠れるのを防ぐ．

## 平均性能と最悪群性能

| 目的 | 最適化するもの | 起こりやすい失敗 |
| --- | --- | --- |
| average performance | 全症例の平均 loss / accuracy | 少数 subgroup の性能低下を隠す |
| subgroup reporting | subgroup ごとの性能 | 改善まではしない |
| worst group performance | 最も低い subgroup performance | 平均性能との trade-off がある |
| Group DRO | group loss の最大値 | group label が必要 |

GEORGE 論文では，observed superclass label `y` の背後に latent subclass label `z` があると考える．通常の分類では `y` を正しく予測する平均 accuracy を最大化するが，worst group performance では，全 subclass の中で最悪の expected accuracy を最大化する．

```text
average objective:
  maximize E[correct]

robust objective:
  maximize min_subclass E[correct | subclass]
```

## Group DRO の役割

Group Distributionally Robust Optimization（Group DRO）は，既知の group ごとの average loss を計算し，その最大値を小さくするように学習する．group labels が正しく与えられていれば，minority subgroup や hard subgroup の loss が最適化で無視されにくくなる．

問題は，医療画像では重要な subgroup がしばしば unlabeled であることにある．疾患 subtype，治療状態，artifact，image quality，lesion appearance などは，training label に含まれていないことが多い．そのため，worst group performance を改善するには，group label を発見する段階が必要になる．

## GEORGE の考え方

GEORGE は，group label がない状況で worst group performance を改善するための2段階手法である．

```text
1. ERM model を superclass task で学習する
2. 各 superclass 内の feature representation を clustering する
3. cluster assignment を proxy subclass label とみなす
4. proxy groups を使って Group DRO で再学習する
```

この設計の前提は，coarse label で学習した deep model の feature space にも，unlabeled subclass の情報が残っていることが多い，という観察である．subclass が feature space で分離できるなら，cluster assignment は noisy group label として使える．

## 測定としての cluster-robust performance

GEORGE の Step 1 は，training 改善だけでなく測定にも使える．cluster ごとの performance を測り，その最悪値を cluster-robust performance と呼ぶ．

| 指標 | 意味 |
| --- | --- |
| overall performance | 全体平均の性能 |
| robust performance | true subclass labels 上の worst-case performance |
| cluster-robust performance | discovered clusters 上の worst-case performance |

true subclass labels がない場合，cluster-robust performance は robust performance の近似になる．GEORGE 論文では，多くの場合，cluster-robust performance は overall performance より true robust performance に近かった．これは，subclass labels なしに hidden stratification の存在と大きさを推定できることを示す．

## 医療画像での意味

worst group performance は，医療画像 fairness と clinical safety の接点にある．protected attribute ごとの fairness gap だけでなく，疾患 phenotype や treatment status ごとの failure を評価するために使える．

たとえば pneumothorax classifier では，chest drain ありの treated cases で高性能でも，chest drain なしの untreated cases で低性能なら，臨床上の worst group は後者である．skin lesion classifier では，colored patch の有無だけでなく，histopathology が必要だった難症例群が worst group になる可能性がある．

MEDFAIR は，医療画像 fairness の評価で worst-case group AUC を Max-Min fairness の主要指標として扱う．これは，診断のように全 subgroup を保護したい応用では，subgroup gap の小ささだけでなく，最も低性能な subgroup の性能自体が重要だからである．

[[Underdiagnosis_Bias]] は，worst group performance を threshold-dependent failure として見る具体例である．平均 AUC が高くても，ある subgroup で `no finding` FPR が高ければ，その subgroup は臨床的には worst group になりうる．そのため，worst group performance は AUC だけでなく，underdiagnosis rate，sensitivity，calibration でも測る必要がある．

[[Demographic_Imbalance]] は，worst group を作る data-level cause である．training data の sex/gender ratio が偏ると，under-represented group が worst group になりうる．この場合，Group DRO や model selection だけでなく，dataset construction と subgroup-balanced validation split が重要になる．

[[Equalized_Odds]] の文脈では，worst group は単に低 AUC の group ではない．fixed operating point で TPR が最も低い subgroup，または FPR が最も高い subgroup が臨床的な worst group になる．Kurian et al. の worst-group EO regularizer は，age，race，sex の unified subgroup set から mini-batch ごとに最悪 subgroup を選び，under-diagnosis 側と over-diagnosis 側の logit margin を同時に罰する．

## 条件付きモデル評価への使い方

[[FiLM]]，[[HyperFusion]]，[[Image_Tabular_Fusion]] のような条件付きモデルは，属性や EHR を使って平均性能を上げるかもしれない．しかし，研究上重要なのは，平均性能ではなく worst group performance が改善するかである．

評価では次を比較する．

| 比較 | 問い |
| --- | --- |
| ERM vs 条件付きモデル | 平均性能だけでなく worst group も改善するか |
| metadata groups vs discovered groups | 既知属性では見えない worst group が残るか |
| attributeあり vs attributeなし | protected attribute が worst group を助けるか，shortcut を強めるか |
| in-domain vs external dataset | worst group 改善が施設・dataset を越えて残るか |

## リファレンス

| 用語 | 意味 |
| --- | --- |
| worst group performance | subgroup ごとの性能の最小値 |
| robust accuracy | 全 subclass のうち最悪 subclass の accuracy |
| Group DRO | group-wise loss の最大値を最小化する robust optimization |
| Equalized Odds | subgroup 間で TPR/FPR を揃える fairness criterion |
| proxy subclass label | clustering などで推定した noisy subgroup label |
| cluster-robust performance | discovered cluster 上で測った worst-case performance |

## 関連概念

- [[Hidden_Stratification]]
- [[Subgroup_Performance_Monitoring]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Underdiagnosis_Bias]]
- [[Equalized_Odds]]
- [[Demographic_Imbalance]]
- [[Medical_Image_Fairness]]
- [[Fairness_Evaluation]]
- [[Image_Tabular_Fusion]]
