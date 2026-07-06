---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_hidden_stratification_medical_imaging.pdf"
---

# Hidden Stratification Causes Clinically Meaningful Failures in Machine Learning for Medical Imaging

Luke Oakden-Rayner，Gustavo Carneiro，Jared Dunnmon，Christopher Ré による ML4H at NeurIPS 2019 extended abstract．医療画像分類で，粗い superclass label の内部に臨床的・視覚的に異なる subclass が隠れているため，aggregate performance が高くても重要な症例群で性能が大きく落ちる現象を hidden stratification と呼び，その測定方法と実例を示す．

著者らは，hidden stratification が低 prevalence，低 label quality，subtle discriminative features，spurious correlates を持つ subclass で起こりやすく，最大で約20%の clinically important subset performance difference を生むと述べる．schema completion，error auditing，algorithmic measurement の3つの測定法を提示し，hip fracture，MURA，CXR14 pneumothorax の例で検証する．

## Hidden stratification の定義

医療画像には dense visual information が含まれ，診断は複数の visual features / patterns の組み合わせで行われる．そのため，機械学習のために1つの class とされた pathology や variant は，視覚的・臨床的に異なる複数の subset を含みうる．たとえば lung cancer label には solid / subsolid tumors，central / peripheral neoplasms などが含まれる．

このように，data 内に認識されていない case subsets が存在し，model training，model performance，clinical outcome に影響する現象を hidden stratification と呼ぶ．test set で aggregate accuracy，sensitivity，ROC AUC が高くても，大きな subset が指標を支配し，少数だが重要な subclass の poor performance が隠れる可能性がある．

著者らは，重症疾患は軽症疾患より少ないことが多いため，minority subset の underperformance は患者への不均衡な harm につながりうると指摘する．

## 測定方法

### Schema completion

schema completion では，schema author が事前により完全な subclass set を定義し，test data に subclass labels を付与する．専門団体などが subclass definition と reporting expectation を標準化できる利点がある．

一方，schema completion は schema author の理解に制限される．重要 subclass が事前に想定されていなければ保護できない．また，臨床では diagnostic，demographic，clinical，descriptive characteristics の組み合わせで非常に多くの subclass が存在しうるため，すべてを exhaustively label するのは時間的・実務的に困難である．新しい治療の visual artifacts や未知の pathology により，既存 schema が obsolete になる可能性もある．

### Error auditing

error auditing では，auditor が model outputs を調べ，一貫して間違う recognizable subclass など，予期しない regularities を探す．schema author が事前に想定した subclass に限定されず，model function によって subclass search space が誘導されるため，すべての subclass を列挙する必要がない．

ただし，auditing は auditor が model output distribution の異常 pattern を視覚的に認識できるかに依存する．特に，low-prevalence だが high-discordance で clinically salient な subclass は稀にしか現れず，見落とされる可能性がある．

### Algorithmic measurement

algorithmic measurement では，developer が subclass を自動探索する方法を設計する．多くの場合，clustering などの unsupervised method が使われる．identified group が superclass 全体より低性能であれば，clinically relevant subclass の存在を示唆する．

algorithmic approach も最終的には human review が必要だが，最初の stratification 発見を特定 auditor に依存しにくくする．一方，重要 subclass を analyzed feature space で分離できるかが限界になる．

## 仮説

著者らは hidden stratification による性能低下に寄与する subclass characteristics として以下を挙げる．

1. low subclass prevalence
2. reduced label accuracy within the subclass
3. subtle discriminative features
4. spurious correlations

## Hip fracture dataset

schema completion により，Royal Adelaide Hospital の pelvic x-ray dataset で hidden stratification を評価した．DenseNet model は hip fracture detection で ROC AUC 0.994 を達成していた．board-certified radiologist が subclass labels を付与した．

hip fracture の superclass と subclass sensitivity は以下である．

| Subclass | Prevalence (Count) | Sensitivity |
| --- | ---: | ---: |
| Overall | 1.00 (643) | 0.981 |
| Subcapital | 0.26 (169) | 0.987 |
| Cervical | 0.13 (81) | 0.911 |
| Pertrochanteric | 0.50 (319) | 0.997 |
| Subtrochanteric | 0.05 (29) | 0.957 |
| Subtle | 0.06 (38) | 0.900 |
| Mildly Displaced | 0.29 (185) | 0.983 |
| Moderately Displaced | 0.30 (192) | 1.000 |
| Severely Displaced | 0.36 (228) | 0.996 |
| Comminuted | 0.26 (169) | 1.000 |

overall sensitivity は 0.981 だが，subtle fractures は 0.900，low-prevalence cervical fractures は 0.911 であり，どちらも overall task より有意に低かった（p < 0.01）．著者らは，subtle visual features と low prevalence が clinically relevant stratification に寄与することを支持すると述べる．

## MURA dataset

MURA musculoskeletal x-ray dataset は，case が “normal” / “abnormal” の binary label を持つ．この binary labels は過去に board-certified radiologist によって subclass identifiers 付きで再ラベルされ，subclass ごとに prevalence と superclass label sensitivity が大きく異なることが示されていた．

MURA abnormal label の subclass prevalence と superclass label sensitivity は以下である．

| Subclass | Subclass Prevalence | Superclass Label Sensitivity |
| --- | ---: | ---: |
| Fracture | 0.30 | 0.92 |
| Hardware | 0.11 | 0.85 |
| Degenerative joint disease (DJD) | 0.43 | 0.60 |

著者らは DenseNet-169 を normal / abnormal labels で学習した．training は 13,942 cases，test は 714 cases．overall ROC AUC は 0.91 だった．easy-to-detect subclass である hardware は AUC 0.98 で aggregate より高く，degenerative disease は AUC 0.76 で低かった．degenerative disease は label sensitivity が低く，subtle visual features を持つため，hidden stratification が生じたと解釈される．

## CXR14 pneumothorax

error auditing により，CXR14 chest radiograph dataset の pneumothorax class における hidden stratification を示した．CXR14 は 30,805 unique patients からの 112,120 frontal chest films を含み，14 thoracic pathologies の labels を持つ．著者らは Rajpurkar et al. の手順と結果を再現する Zech の pretrained DenseNet-121 model を使った．

false positives / false negatives を board-certified radiologist が visually reviewed したところ，chest drain のない pneumothorax cases が false negatives に多いことが観察された．chest drain は pneumothorax の治療器具であり，診断に causal な image feature ではない．治療済み pneumothorax は通常 benign で，未治療 pneumothorax は life-threatening であるため，この spurious correlate は臨床的に重要である．

pneumothorax test set に chest drain / no chest drain subclass labels を付与した結果，overall pneumothorax ROC AUC は 0.87 だったが，chest drains あり subclass は AUC 0.94，chest drains なし subclass は AUC 0.77 だった．test set の pneumothoraces の 80% は chest drain を含んでいた．positive predictive value は chest drains ありで 0.90，なしで 0.60 であり，30% 高かった．

## Unsupervised clustering

schema completion と error auditing は clinician effort を必要とするため，著者らは simple k-means clustering が hidden subclass 検出に役立つかを調べた．各 superclass について，test set examples の pre-softmax feature vector に k-means を適用し，`k ∈ {2, 3, 4, 5}` を試す．各 `k` について 100 points より大きい clusters の中から error rate difference が最大の2 cluster を選び，high error cluster と low error cluster とする．最後に centroid distance が最大の pair を返す．

結果は以下である．

| Dataset-Superclass (Subclass) | Difference in Subclass Prevalence (High Error Cluster, Low Error Cluster) | Overall Subclass Prevalence |
| --- | ---: | ---: |
| CXR14-Pneumothorax (Drains) | 0.68 (0.17, 0.84) | 0.80 |
| MURA-Abnormal (Hardware) | 0.03 (0.29, 0.26) | 0.11 |
| MURA-Abnormal (Degenerative) | 0.04 (0.12, 0.08) | 0.43 |

simple k-means は MURA では必ずしも意味のある separation を返さなかったが，CXR14 では chest drains の割合が大きく異なる clusters を生成した．著者らは，このような approach は human auditors が salient stratifications を見つける補助や，schema completion が成功したかの確認に使える可能性があると述べる．

## 臨床的含意

hidden stratification の clinical implications は task によって異なる．MURA の degenerative disease は臨床的に重大でないことが多く，急速な complication も少ないため，hidden stratification が臨床的に重大とは限らない．一方，CXR14 の pneumothorax では，chest drain のない未治療 pneumothorax が生命に関わるため，overall task result だけを根拠に臨床使用や regulatory approval を正当化すると患者 harm につながりうる．

著者らは，医療画像システムが rare，dangerous，subtle disease variants を見逃す可能性は，人間専門家との比較において特に問題だと述べる．人間専門家はまさにそのような症例を識別するために多くの訓練を行うためである．

## 結論

hidden stratification は clinical imaging datasets における largely unrecognized problem であり，clinical image analysis systems を planning，building，evaluating，regulating する際に考慮されるべきである．著者らは，hidden stratification effects の測定と報告が，医療機械学習 deployment の critical component になるべきだと主張する．

## 関連概念

- [[Hidden_Stratification]]
- [[Subgroup_Performance_Monitoring]]
- [[Spurious_Correlation]]
- [[Error_Auditing]]
- [[Schema_Completion]]
- [[Algorithmic_Subgroup_Discovery]]
- [[Medical_Image_Fairness_Audit_Loop]]
