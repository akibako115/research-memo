---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_improving_model_fairness_image_based_cad.pdf"
---

# Improving model fairness in image-based computer-aided diagnosis

この論文は，image-based computer-aided diagnosis における subgroup fairness を改善するため，marginal pairwise equal opportunity に基づく training method を提案する．著者らは，binary cross-entropy baseline と比較して，marginal ranking loss を用いることで Pairwise Fairness Difference (PFD) を下げつつ，overall AUC をほぼ維持できることを示す．

主な結果は，4つの large-scale cohort，4つの疾患タスクにおいて，individual subgroup と intersectional subgroup の fairness が改善し，baseline との relative PFD change が多くの条件で35%以上低下し，AUC の relative change は多くの場合1%以内だった，というものである．

## 評価タスクと dataset

評価対象は4つの publicly available datasets である．

| Task | Dataset | Modality | Size | Subgroups |
| --- | --- | --- | ---: | --- |
| COVID-19 detection | MIDRC | chest X-ray | 77,887 images / 27,799 individuals | age，sex，race |
| thorax abnormality detection | MIMIC-CXR | chest X-ray | 212,567 images / 227,827 studies | age，sex，race |
| POAG detection | OHTS | optic disc | 37,399 images / 1,636 individuals | age，sex，race |
| Late AMD detection | AREDS | color fundus photographs | 66,060 images / 4,566 individuals | age，sex，CFH，ARMS2 |

AREDS では Black subgroup が3.7%未満で信頼できる評価が難しいため，race は評価から除外される．Late AMD では，genotype として CFH rs1061170 と ARMS2 rs10490924 を扱う．

## Pairwise Fairness / PFD

著者らは，model fairness の評価に Pairwise Fairness を使う．これは，subgroup 内の positive sample が，dataset 全体の negative sample より高い score を持つ確率である．AUC を subgroup-wise ranking として見る criterion であり，臨床では risk score が resource triage や chronic disease prevention の意思決定補助に使われるため，threshold-dependent metrics より適していると主張される．

Pairwise Fairness Difference (PFD) は，subgroups の Pairwise Fairness の最大値と最小値の差である．PFD が大きいほど，individual / intersectional subgroup の ranking fairness に大きな disparity があることを示す．

## Training method

baseline は binary cross-entropy loss で学習した CNN である．提案手法は，batch ごとに各 subgroup の Pairwise Fairness を計算し，最も Pairwise Fairness が低い subgroup を選ぶ．その subgroup の positive sample と，negative sample の ranking order が margin を満たすように marginal ranking loss を計算する．

損失は，positive sample の prediction `xp` が negative sample の prediction `xn` より十分高くなるように，`max(0, -xp + xn + margin)` を平均する形である．この設計により，ranking order が誤っている sample に直接勾配をかけ，最も低い group fairness を batch ごとに改善する．

主な model は DenseNet-201 で，MIDRC では CheXpert-pretrained DenseNet-121 を使う．generalizability を見るため，MIDRC と OHTS では ResNet-152 でも評価している．

## Individual subgroup の結果

提案手法は，age，sex，race の subgroup に対して，多くの dataset で PFD を下げ，AUC を維持した．

| Task | 主な結果 |
| --- | --- |
| COVID-19 / MIDRC | age，sex で lower PFD and comparable AUC，race で lower PFD but lower AUC |
| Thorax abnormality / MIMIC-CXR | age，sex で lower PFD and comparable AUC，race では slightly higher PFD and comparable AUC |
| POAG / OHTS | age，sex，race で lower PFD and higher AUC |
| Late AMD / AREDS | age で lower PFD，sex で comparable PFD，AUC は baseline より高い |

各タスクでは，lowest AUC subgroup も報告される．MIDRC では male，>75，Other races，MIMIC-CXR では >60，male，Black，OHTS では <60，female，Other races，AREDS では <65 が misdiagnosis prone subgroup として挙げられる．

## Genotype と intersectional subgroup

Late AMD では，CFH と ARMS2 genotype に対しても fairness を評価する．提案手法は CFH と ARMS2 で lower PFD and comparable AUC を示した．CFH (TT) と ARMS2 (GG) は最低 AUC subgroup とされ，AMD misdiagnosis のリスクが高い可能性がある．

intersectional subgroup では，baseline で pairwise fairness disparity が大きい2属性を選んで評価する．COVID-19，thorax abnormality，POAG では age-race または age-sex，Late AMD では age-CFH を見る．提案手法は，これらの intersectional groups でも PFD を下げ，AUC は概ね comparable だった．baseline の intersectional PFD は4 dataset すべてで0.1を超え，single identity より大きかった．

## Relative change

Table 2 では，baseline と提案手法の relative change をまとめている．PFD は15ケースで低下し，そのうち12ケースでは35%以上低下した．AUC の relative change は多くの場合1%以内であり，fairness constraints がしばしば performance を落とすという既存の懸念に対して，提案手法は AUC を維持しながら PFD を改善できると主張している．

代表例として，COVID-19 では PFD relative change が age -40.25%，sex -53.79%，race -39.73%，age-race -47.69% だった．POAG では age -53.82%，sex -35.74%，race -43.85%，age-sex -35.10% だった．

## Discussion

著者らは，Pairwise Fairness は Equalized Odds，Demographic Parity，Equal Opportunity のような threshold-dependent / binarized metrics と異なり，positive examples を negative examples より高く rank するかを測るため，臨床 risk score の利用に近いと述べる．また，scale-invariant で classification threshold を必要としない点も利点とされる．

data imbalance は bias の重要な要因である．OHTS では POAG prevalence が ≥60 で <60 の約3倍あり，MIMIC-CXR の age subgroup，MIDRC の race subgroup でも subgroup prevalence や sample size の違いが bias に関係した．oversampling は一部で fairness を改善するが，提案手法の方が良いと報告されている．

limitation として，この研究は binarized models の fairness に焦点を当てており，predicted probabilities の calibration は評価していない．future work として，calibration bias，continuous attributes，multi-class settings への拡張が挙げられる．

## 関連概念

- [[Pairwise_Fairness]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Equalized_Odds]]
- [[Worst_Group_Performance]]
- [[Demographic_Imbalance]]
