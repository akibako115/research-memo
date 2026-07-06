---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_fairness_beyond_demographics_hidden_cohorts]]"
---

# Hidden Cohort Fairness

Hidden cohort fairness は，sex，age，race のような visible demographic attributes ではなく，画像 appearance から発見した latent cohorts に対して fairness を最適化する考え方である．狙いは，demographic labels に依存せず，model error とより強く関係する hidden subpopulations を使って worst-group performance を改善することである．

この概念が重要なのは，demographic subgroup だけを fairness の単位にすると，metadata にない lesion appearance，image quality，artifact，disease subtype，severity などの failure mode を見落とすからである．さらに，sex x age x race のような intersectional groups は subgroup 数が急増し，training data が sparse になりやすい．

## Demographic fairness から hidden-cohort fairness へ

従来の fairness training は，visible demographic attributes を sensitive attribute として使う．しかし，visible attributes は必ずしも model failure の最も良い説明変数ではない．

| Fairness unit | 強み | 弱み |
| --- | --- | --- |
| demographic cohort | 解釈しやすく reporting に向く | hidden phenotype / artifact を見落とす |
| intersectional demographic cohort | 複数属性の重なりを見られる | subgroup sparsity が起きる |
| appearance-based hidden cohort | visual failure mode を捉えやすい | 意味づけに human review が必要 |

hidden cohort fairness は，[[Hidden_Stratification]] を監査対象として見るだけでなく，training objective の group として使う点が特徴である．

## LHCF

Label-free Hidden-Cohort Fairness (LHCF) は，demographic annotation なしで hidden cohorts を作り，その cohort labels を fairness-aware training に使う．

```text
images + diagnostic labels
  -> encoder embeddings
  -> GMM clustering
  -> hidden cohort labels
  -> fairness-aware training over hidden cohorts
```

LHCF では，pre-trained encoder の embedding に Gaussian Mixture Model を fit し，Bayesian Information Criterion で cluster 数を選ぶ．各 sample は最大 responsibility の cluster に割り当てられる．その後，hidden cohort ごとの worst loss または best-worst loss gap を fairness loss として追加する．

この設計は model / loss に依存しないため，SWAD，FIS，FEBS，FairCLIP，FaMI，FairDi のような既存 fairness method と組み合わせられる．

## なぜ visible fairness に効くのか

Masroor et al. は，visible cohort が hidden clusters の union として表せるなら，worst hidden-cohort loss は任意の visible cohort loss の upper bound になると説明する．

つまり，hidden cohorts の最悪 loss を下げることは，demographic group の最悪 loss も間接的に抑える可能性がある．この仮定が完全に成り立たなくても，hidden cohorts が model failure に近い appearance structure を捉えるなら，demographic label に直接合わせるよりも robust な改善になりうる．

## HIDFairBench

HIDFairBench は，hidden cohorts と visible demographics の両方で fairness method を評価する benchmark である．

| Dataset | Task | Visible cohorts |
| --- | --- | --- |
| HAM10000 | benign vs malignant dermatology | Gender，Age_binary，Age_multi4，Gender x Age |
| Fitzpatrick17K | benign vs malignant dermatology | Fitzpatrick skin type |
| CMMD | non-cancer vs cancer mammography | Age_binary |

評価指標は Overall AUC，AUC Gap，Worst-Case AUC，ES-AUC，Performance-Scaled Disparity (PSD) である．hidden cohort quality は Brier Score と Average Purity で見る．Average Purity が低い場合，hidden cohorts は demographic labels とは違う visual structure を捉えていると解釈できる．

## 実験からの示唆

LHCF は demographic labels を training に使わないにもかかわらず，single demographic attributes と intersectional cohorts の両方で fairness を改善した．FairDi との組み合わせでは，Classic demographic training より Overall AUC，Min AUC，ES-AUC が上がり，AUC Gap が下がった．

| FairDi setting | Overall AUC | Min AUC | ES-AUC | AUC Gap |
| --- | ---: | ---: | ---: | ---: |
| Classic | 0.9014 | 0.8511 | 0.8744 | 0.0824 |
| LHCF | 0.9050 | 0.8686 | 0.8817 | 0.0666 |

HAM10000 では，hidden cohorts は malignancy risk と calibration error を stratify した一方，gender / age との alignment は弱かった．これは，hidden cohorts が demographic proxy ではなく，clinical risk と visual structure に近い単位を捉えている可能性を示す．

## 実装上の注意

hidden cohort fairness は，cluster の品質に依存する．cluster 数が少なすぎると heterogeneous な failure mode を潰し，多すぎると sample sparsity や unstable clusters を生む．Masroor et al. では，HAM10000 で BIC が選んだ `K=7` が多くの metric で良かった．

backbone choice も重要である．ResNet18 と MedCLIP は良い accuracy-fairness trade-off を示したが，CLIP と DINOv2 は cohort complexity が増えると worst-case performance が落ち，disparity が増えた．したがって，hidden cohort discovery では，強い foundation representation を使えば必ず良いわけではなく，cohort granularity と clinical relevance を確認する必要がある．

## 既存概念との関係

Hidden cohort fairness は，[[Subgroup_Performance_Monitoring]] と [[Fairness_Mitigation_In_Medical_Imaging]] をつなぐ概念である．monitoring は hidden subgroup を見つけるところまでだが，LHCF はそれを training objective に戻す．

[[DOMINO]] や GEORGE は systematic error / hidden subclass を発見・利用する先行系である．LHCF は demographic labels を使わず，appearance-based cohorts を fairness group として扱う点で，medical fairness の文脈により直接接続される．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| hidden cohort fairness | appearance-based hidden cohorts に対して fairness を最適化する考え方 |
| LHCF | Label-free Hidden-Cohort Fairness |
| hidden cohort | image embedding の clustering で得られる latent subgroup |
| HIDFairBench | hidden cohort と visible demographic fairness を評価する benchmark |
| Average Purity | hidden cohort と visible attribute の alignment を測る指標 |
| Brier Score | calibration と cohort reliability を見る指標 |

## 関連概念

- [[Hidden_Stratification]]
- [[Subgroup_Performance_Monitoring]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Worst_Group_Performance]]
- [[DOMINO]]
- [[Demographic_Imbalance]]
