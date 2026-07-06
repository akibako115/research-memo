---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_fairness_beyond_demographics_hidden_cohorts.pdf"
---

# Fairness Beyond Demographics: Optimizing Performance Across Appearance-Based Hidden Cohorts in Medical Imaging

この論文は，visible demographic attributes ではなく，画像 appearance から発見した hidden cohorts に対して fairness optimization を行う Label-free Hidden-Cohort Fairness (LHCF) を提案する．問題意識は，sex，age，ethnicity などの demographic attribute だけでは model error の深い原因を捉えきれず，複数属性を組み合わせると subgroup 数が増えて sample sparsity が起きる，という点である．

主な主張は，appearance-based latent cohorts は demographic labels なしでも臨床的 risk stratification を捉え，その cohort を sensitive attribute として fairness-aware training すれば，single demographic attributes と intersectional demographic attributes の両方で fairness が改善する，というものである．

## LHCF training

LHCF は2段階で構成される．

1. pre-trained model の image embeddings から hidden cohorts を教師なしに発見する．
2. 発見した cohort label を sensitive attribute とみなし，fairness-aware training を行う．

入力 dataset は demographic annotation を持たない `D = {(xi, yi)}` であり，画像 `xi` と diagnostic label `yi` だけを使う．model は encoder `eθe` と decoder `dθd` からなる `fθ = dθd ◦ eθe` として表される．encoder embedding `zi = eθe(xi)` に対して Gaussian Mixture Model (GMM) を fit し，cluster 数 `K` は Bayesian Information Criterion (BIC) で選ぶ．各 sample は最大 responsibility を持つ cluster に割り当てられ，hidden cohort label `ci` を得る．

その後，classification loss に fairness loss を加えて training する．fairness loss は worst-cohort classification loss を最小化するもの，または best / worst cohort loss gap を最小化するものとして定義できる．LHCF は model や fairness loss に依存せず，SWAD，FIS，FEBS，FairCLIP，FaMI，FairDi などの FairAI method と組み合わせられる．

## 理論的直観

論文は，visible cohort が hidden clusters の union として表せるという仮定の下で，worst hidden-cohort loss が任意の visible cohort loss の upper bound になることを示す．

直観的には，overlap する visible demographic cohorts の average loss を直接最小化すると，intersectional groups を過度に強調したり，sample sparsity に弱くなったりする．一方，appearance-based hidden cohorts の worst loss を下げると，demographic labels を使わずに visible demographic cohorts の loss も上から抑えられる可能性がある．

## HIDFairBench

著者らは，LHCF を評価するために HIdden-Demographic Fairness Benchmark (HIDFairBench) を提案する．対象 dataset は3つである．

| Dataset | Task | Visible cohorts |
| --- | --- | --- |
| HAM10000 | dermoscopic image の benign vs malignant | Gender，Age_binary (≤60 / >60)，Age_multi4 (≤39, 40-59, 60-79, ≥80)，Gender x Age |
| Fitzpatrick17K | lesion の benign vs malignant | Fitzpatrick skin type 0-5 |
| CMMD | mammography の non-cancer vs cancer | Age_binary (≤55 / >55) |

HAM10000 と Fitzpatrick17K は 80/10/10 split，CMMD は 70/10/20 split を使う．visible cohort evaluation では Overall AUC，AUC Gap，Worst-Case AUC，ES-AUC，Performance-Scaled Disparity (PSD) を報告する．統計検定には Friedman test と Nemenyi post-hoc comparison を使う．

hidden-cohort quality は Brier Score (BS) と Average Purity (AP) で測る．BS は calibration と under/over-performing cohorts を捉え，AP は hidden cohorts が visible demographic attributes とどの程度 align するかを測る．

## Hidden cohorts の性質

HAM10000 の ERM-trained ResNet18 では，hidden clusters は malignancy risk と calibration error による risk stratification を示した．low malignancy-rate clusters は低い BS，中間 risk clusters は中程度の BS，高 malignancy-rate clusters は高い BS を示し，clinically severe cases で reliability が低くなる pattern が見える．

一方で，hidden cohorts と visible demographics の alignment は弱かった．HAM10000 では AP が gender で 0.4919±0.0183，age で 0.2234±0.0065，Fitzpatrick17K では skin type で 0.0998±0.0161，CMMD では age で 0.3517±0.0067 だった．AP < 0.5 であることから，hidden cohorts は demographic attributes そのものではなく，主に visual structure を反映すると解釈される．

## Classic vs LHCF

Table 2 では，HAM10000，Fitzpatrick17K，CMMD の visible cohorts に対して，Classic demographic fairness training と LHCF を比較している．全体として，LHCF は Overall AUC と fairness metrics を改善し，特に intersectional cohorts で改善が大きい．

FairDi は Classic でも最も強いが，LHCF と組み合わせるとさらに改善する．FairDi の平均結果は，Classic で Overall AUC 0.9014，Min AUC 0.8511，ES-AUC 0.8744，AUC Gap 0.0824 だったのに対し，LHCF では Overall AUC 0.9050，Min AUC 0.8686，ES-AUC 0.8817，AUC Gap 0.0666 になった．

この結果は，demographic labels を training に使わなくても，appearance-based hidden cohort optimization が visible demographic fairness に一般化しうることを示す．

## Ablation

hidden cohort 数 `K` については，HAM10000 で `K ∈ {3, 5, 7, 9}` を比較し，BIC が選んだ `K=7` が AUC と fairness measures の多くで最良だった．大きすぎる，または小さすぎる `K` は performance を悪化させる傾向がある．

embedding backbone では，ResNet18 と MedCLIP が Overall AUC で良く，fairness metrics では ResNet18 が特に強かった．CLIP と DINOv2 は cohort complexity が増えると worst-case performance 低下と disparity 増加が大きかった．著者らは，ResNet18 (`K=7`) や MedCLIP (`K=6`) のように moderate hidden-cohort granularity を作る backbone が，accuracy-fairness trade-off に有利だと述べる．

Demographic-Aware Clustering (DAC) との比較では，embedding に demographic attributes を加えて clustering する DAC より，appearance-driven label-free の LHCF がほぼ全 metric / cohort complexity で良かった．これは，demographic information に依存しない hidden-cohort optimization の robustness を示す．

## 限界と future work

著者らは，LHCF の再現性を高めるためには unsupervised clustering stage の安定化が必要だと述べる．また，Lemma 1 はより多様な fairness losses に拡張する余地がある．それでも，data-driven latent stratification は，demographic-label-based fairness optimization より generalizable で deployable な方向性だと位置づけられる．

## 関連概念

- [[Hidden_Cohort_Fairness]]
- [[Hidden_Stratification]]
- [[Subgroup_Performance_Monitoring]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Worst_Group_Performance]]
- [[DOMINO]]
