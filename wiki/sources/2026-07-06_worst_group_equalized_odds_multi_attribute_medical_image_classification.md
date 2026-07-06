---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_worst_group_equalized_odds_multi_attribute_medical_image_classification.pdf"
---

# Worst-Group Equalized Odds Regularization for Multi-Attribute Fair Medical Image Classification

この論文は，医療画像分類において subgroup AUC では見えにくい operating-point 上の fairness disparity を緩和するために，worst-group equalized-odds margin regularizer を提案する．固定 threshold では，ある subgroup が over-diagnostic pattern（高 TPR・高 FPR）を示し，別 subgroup が under-diagnostic pattern（低 TPR・低 FPR）を示すことがあり，これらは aggregate AUC では相殺されうる．

著者らは，age，sex，race など複数 demographic attributes を同時に扱う multi-attribute setting で，mini-batch ごとに TPR-side / FPR-side の最悪 subgroup を特定し，logit margin に対する differentiable regularization を行う．RNFL-OCT と MIMIC-CXR の2つの医療画像 dataset で，AUC への影響を小さく保ちながら Equalized Odds と Equalized Opportunity の disparity を減らすと報告している．

## 背景

医療 AI の診断性能は demographic groups によって系統的に変わることがある．subgroup AUC が似ていても，固定された inference-time operating point では，Black patients の sensitivity が低く White patients の false-positive rate が高い，といった TPR/FPR disparity が残りうる．そのため，fairness は AUC だけでなく Equalized Odds (EO) や Equalized Opportunity (EOpp) で評価する必要がある．

既存の fairness mitigation には，GDRO，JTT，FairBatch，FaMI，adversarial training などがあるが，多くは average predictive risk や log-loss の修正に基づく．また，多くの研究は単一 demographic attribute に注目しており，複数属性を同時に扱うと，intersectional subgroup の sample size が小さくなる，attribute ごとの constraint が増える，task-relevant information まで消す，といった問題が生じる．

## 問題設定

入力画像 `x_i`，binary label `y_i`，demographic attributes `a_i = (age, sex, race)` を持つ binary classification dataset を考える．各 attribute-value pair，たとえば female，White，age >= 60 を subgroup `g` とし，すべての subgroup を unified set `G` に集める．1 sample は複数 subgroup に属しうる．

neural network `f_theta` は logit `l_i` を出し，sigmoid で probability `p_i` に変換する．multi-label setting では，この binary head を各 class に対して平均する．

## Worst subgroup identification

mini-batch ごとに，positives と negatives で別々に worst subgroup を特定する．

| 対象 | 特定する subgroup | 意味 |
| --- | --- | --- |
| positives (`y=1`) | mean predicted probability が最も低い subgroup | low TPR，under-diagnosis risk |
| negatives (`y=0`) | mean predicted probability が最も高い subgroup | high FPR，over-diagnosis risk |

positives では，`mu_g+ = mean{p_i | y_i=1, g_i=g}` を計算し，最小の subgroup `g_min+` を選ぶ．negatives では，`mu_g- = mean{p_i | y_i=0, g_i=g}` を計算し，最大の subgroup `g_max-` を選ぶ．この worst subgroup は attribute-agnostic であり，age，sex，race のどの軸でもよい．

## Log-sum-exp margin regularization

理想的には，worst subgroup の positive samples の最低 logit が全 negative samples の最高 logit より高く，worst subgroup の negative samples の最高 logit が全 positive samples の最低 logit より低いことが望ましい．

```text
under-diagnosis 側:
  min logit(positive in g_min+) > max logit(all negatives)

over-diagnosis 側:
  max logit(negative in g_max-) < min logit(all positives)
```

hard min/max は non-differentiable で single extreme sample に依存するため，著者らは log-sum-exp (LSE) による smooth relaxation を用いる．

| Margin | 何を比較するか | 対応する violation |
| --- | --- | --- |
| `margin_EO+` | all negatives の LSE max と，`g_min+` positives の LSE min | TPR-side violation / under-diagnosis |
| `margin_EO-` | `g_max-` negatives の LSE max と，all positives の LSE min | FPR-side violation / over-diagnosis |

hinge mechanism により positive margin のみを罰し，`L_EO+ = max(0, margin_EO+)`，`L_EO- = max(0, margin_EO-)` とする．最終 objective は base BCE loss と2つの fairness regularizer の和である．

```text
L = L_base + lambda_EO+ * L_EO+ + lambda_EO- * L_EO-
```

必要な sample pool が mini-batch 内で空の場合，対応する loss term は0にする．regularizer は post-hoc threshold adjustment を必要とせず，training 中に worst-case EO violations を直接対象にする．

## Dataset

2つの医療画像 dataset を用いる．

| Dataset | 内容 | Task | Sensitive attributes |
| --- | --- | --- | --- |
| RNFL-OCT | 3,300 retinal nerve fiber layer thickness 2D projection maps | binary glaucoma classification，52% positive | age，race，sex |
| MIMIC-CXR | frontal chest radiographs with reports | Pleural Effusion，Cardiomegaly，Atelectasis の multi-label classification | age，race，sex |

MIMIC-CXR では，Pleural Effusion (25% positive)，Cardiomegaly (20%)，Atelectasis (20%) のいずれかを持つ患者に限定し，82,282 images を用いる．

Table 1 では subgroup size が報告されている．RNFL-OCT は age <60 が1,532，age >60 が1,768，White/Black/Asian が各1,100，Female 1,812，Male 1,488 である．MIMIC-CXR は age 18-36 が3,211，36-50 が6,981，50-65 が22,592，65+ が49,498，White 65,858，Black 13,196，Asian 3,228，Female 37,310，Male 44,972 である．

## Baselines

standard cross-entropy baseline に加え，JTT，FairBatch，GDRO，FaMI，Adversarial Training と比較する．RNFL-OCT では ResNet-34，MIMIC-CXR では DenseNet-121 を使い，6 independent random seeds で実験する．training は30 epochs，batch size 64，learning rate 0.001 である．`lambda_EO+` と `lambda_EO-` は RNFL-OCT で0.5，MIMIC-CXR で0.6 とする．test-time operating point は validation set 上で Youden's J statistic を最大化して選ぶ．

## Evaluation metrics

overall accuracy は AUC で評価する．fairness metrics は EOdds と EOM である．

EOdds は TPR/FPR disparity を worst-to-best group ratio で測る．lower is better である．

```text
EOdds = 1 - 1/2 * (min_g TPR_g / max_g TPR_g + min_g FPR_g / max_g FPR_g)
```

EOM は Equality of Opportunity across Multiple Subclasses であり，per-class balance を worst-to-best ratio の平均として測る．higher is better である．

```text
EOM = 1/K * sum_i min_g Pr(y_hat=i | y=i,g) / max_g Pr(y_hat=i | y=i,g)
```

`g` は評価対象 attribute の demographic subgroups を表す．Joint は Age，Race，Sex の平均として報告される．

## 結果

RNFL-OCT では，baseline が最高 AUC 0.845 を達成するが，joint EOdds 0.354，joint EOM 0.874 と大きな demographic disparity を示した．提案手法は joint EOdds 0.226，joint EOM 0.926 を達成し，AUC drop は -0.006 に留まった．FaMI などは fairness gap を減らすが，AUC drop が -0.061 と大きい．

MIMIC-CXR でも同様の傾向が見られた．baseline は最高 AUC 0.749 だが，joint EOdds 0.254，joint EOM 0.849 を示した．提案手法は joint EOdds を0.127まで下げ，joint EOM を0.916まで上げ，AUC drop は -0.007 だった．他の mitigation strategies と比べ，fairness improvement と diagnostic performance の balance が良いと報告されている．

Table 2 の MIMIC-CXR では，提案手法が Age EOdds 0.153，Race EOdds 0.174，Sex EOdds 0.054，Joint EOdds 0.127 を示し，Joint EOM は0.916だった．

## Ablation

RNFL-OCT で `L_EO+` と `L_EO-` の ablation を行う．どちらか一方だけでも部分的な fairness improvement が得られるが，両方を有効にすると最も強い改善が得られる．これは，under-diagnosis 側の TPR disparity と over-diagnosis 側の FPR disparity が相補的に働くことを示している．

## 結論

著者らは，multi-label medical image classification に対して，multi-attribute demographic groups の worst-case subgroup disparities を緩和する worst-group equalized-odds margin regularizer を提案した．この regularizer は，over-diagnostic / under-diagnostic fairness violations に関係する localized score discrepancies を直接罰し，診断性能を大きく損なわずに EO / EOpp disparity を改善する．

## 関連概念

- [[Equalized_Odds]]
- [[Worst_Group_Performance]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Underdiagnosis_Bias]]
- [[Demographic_Imbalance]]
- [[Multi_Attribute_Fairness]]
