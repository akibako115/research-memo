---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_medfair_benchmarking_fairness_medical_imaging.pdf"
---

# MEDFAIR: Benchmarking Fairness for Medical Imaging

Yongshuo Zong，Yongxin Yang，Timothy Hospedales による ICLR 2023 論文．医療画像における fairness benchmark である MEDFAIR を提案し，11 algorithms，10 datasets，4 sensitive attributes，3 model selection strategies を横断して，bias mitigation algorithms を in-distribution / out-of-distribution の両方で評価する．

著者らは，医療画像 fairness では単一の fairness criterion に合意がなく，既存研究は datasets，model selection，backbones，fairness metrics が異なるため直接比較できないと指摘する．MEDFAIR の大規模実験では，model selection criterion が fairness outcome に大きく影響する一方，state-of-the-art bias mitigation algorithms は ERM を統計的有意に上回らなかった．

## 背景

医療画像診断モデルは race，gender，age，health insurance type などで定義される subgroup に対して systematic bias を持つことが報告されている．bias は chest X-rays，CT scans，skin dermatology images など複数 modality で見られる．

入力画像 `x`，sensitive attribute `s`，target `y` があるとき，診断モデルは `x -> y` の mapping を学ぶ．しかし training data に含まれる data imbalance，attribute-class imbalance，label noise などが sensitive attribute と関連していると，ML model はこれらの bias / confounding factors を増幅しうる．

著者らは，医療画像に特化した systematic and rigorous benchmark が必要だとする．理由は以下である．

- fairness metric に合意がない．
- 既存研究は dataset / setting / backbone / metric が異なり直接比較できない．
- tabular data と low-capacity models での結論が，high-capacity deep image models に一般化するとは限らない．
- model selection strategy が研究ごとに曖昧・不統一である．
- clinical deployment では in-distribution fairness が domain shift 下で保たれるかが重要である．

## Fairness definitions

論文は healthcare において特に重要な fairness definition として group fairness と Max-Min fairness を扱う．

### Group fairness

group fairness は protected subgroups 間で predictive performance parity を目指す．ICU allocation のような limited resources の zero-sum resource allocation では，subgroup 間の disparity を小さくする group fairness が重要になる．

MEDFAIR では，advantaged subgroup と disadvantaged subgroup の diagnosis AUC gap を group fairness の指標として測る．これは sensitive attribute と prediction score が diagnostic label 条件付きで独立であるべきという separability criterion（`Ŷ ⟂ S | Y`）に対応する．

ただし，group fairness は advantaged group の性能を下げることで parity を改善する leveling down を起こしうる．これは beneficence / non-maleficence の原則を損なう可能性があるため，group fairness だけでは utility との trade-off を評価するには不十分だとする．

### Max-Min fairness

Max-Min fairness は，subgroups 間の error rates を equalize するのではなく，worst-case group の utility を最大化する．診断のように全 subgroup を保護すべき医療応用では，beneficence / non-maleficence の観点から group fairness より適切な場合がある．

モデル `h` の subgroup utility を `U_s(h)` とすると，Max-Min fair model は以下で定義される．

```text
h* = argmax_h min_s U_s(h)
```

MEDFAIR では，worst-case group AUC を Max-Min fairness の指標として扱う．

## Datasets

MEDFAIR は reproducibility のため，すべて publicly available な10 datasets を含む．

| Dataset | Modality | # Images / Scans | Sensitive Attributes | Bias Sources |
| --- | --- | ---: | --- | --- |
| CheXpert | Chest X-ray (2D) | 222,793 | Age, Sex, Race | LN, CI, DI |
| MIMIC-CXR | Chest X-ray (2D) | 370,955 | Age, Sex, Race | LN, CI, DI |
| PAPILA | Fundus Image (2D) | 420 | Age, Sex | DI, CI |
| HAM10000 | Skin Dermatology (2D) | 9,948 | Age, Sex | DI, CI |
| Fitzpatrick17k | Skin Dermatology (2D) | 16,012 | Skin type | LN, DI, CI |
| OL3I | Heart CT (2D) | 8,139 | Age, Sex | DI, CI, SC |
| COVID-CT-MD | Lung CT (3D) | 308 | Age, Sex | DI, CI |
| OCT | SD-OCT (3D) | 384 | Age | DI, CI |
| ADNI 1.5T | Brain MRI (3D) | 550 | Age, Sex | SC |
| ADNI 3T | Brain MRI (3D) | 110 | Age, Sex | SC |

LN は label noise，CI は class imbalance，DI は data imbalance，SC は spurious correlation を表す．datasets は X-ray，fundus photography，CT，MRI，SD-OCT，skin dermatology images を含む．dataset size は 2D images で 420 から 370,955，3D scans で 110 から 550 と幅がある．

out-of-distribution evaluation では，同じ modality だが collection location / imaging protocol が異なるペアを使う．具体的には CheXpert / MIMIC-CXR の chest X-ray pair と，ADNI 1.5T / ADNI 3T の brain MRI pair である．

## Algorithms

MEDFAIR は 11 algorithms を5 categories で評価する．

| Category | Method | 内容 |
| --- | --- | --- |
| Baseline | ERM | sensitive attributes を使わず average error を最小化 |
| Subgroup Rebalancing | Resampling | minority groups を upsample して subgroups が同確率で出るようにする |
| Domain-independence | DomainInd | shared encoder と subgroup-specific classifiers |
| Adversarial Training | LAFTR | sensitive attribute が認識できない representation を学習 |
| Adversarial Training | CFair | balanced error rate と conditional representation alignment を促す |
| Adversarial Training | LNL | feature representation と bias の mutual information を下げる |
| Disentanglement | EnD | information bottleneck で confounders を disentangle |
| Disentanglement | ODR | useful / sensitive representations に orthogonality constraint |
| Domain Generalization | GroupDRO | worst-case training loss を regularization 付きで最小化 |
| Domain Generalization | SWAD | dense stochastic weight averaging で robust flat minima を探す |
| Domain Generalization | SAM | neighborhood 全体で低 loss になる sharpness-aware optimization |

## Model selection strategies

fairness と utility の trade-off があるため，hyperparameter selection / early stopping は fairness outcome に影響する．MEDFAIR は3つの model selection strategy を比較する．

| Strategy | 選ぶ model | 特徴 |
| --- | --- | --- |
| Overall performance-based | validation set 全体の loss / accuracy / AUC が最良 | majority group performance に寄りやすい |
| Minimax Pareto selection | Pareto front 上で best worst-case AUC | subgroup trade-off の中で worst group を重視 |
| DTO-based selection | subgroup AUC の utopia point に最も近い | subgroup ごとの最大 AUC への normalized distance を最小化 |

著者らは，bias mitigation algorithm なしでも，selection criterion の変更だけで max-min fairness が改善しうることを検証する．

## Evaluation metrics

主要 metric は AUC である．MEDFAIR は以下の3観点で評価する．

- utility: all subgroups across overall AUC．
- group fairness: maximum subgroup AUC と minimum subgroup AUC の gap．
- Max-Min fairness: worst-case group AUC．

さらに subgroup ごとに BCE，ECE，FPR，FNR，TPR at 80% TNR，Equalized Odds（EqOdd）も報告する．AUC gap と worst-case AUC を特に重視し，group fairness と max-min fairness をそれぞれ評価する．

統計検定には Friedman test と Nemenyi post-hoc test を使い，datasets / sensitive attributes ごとの相対 rank を平均して critical difference diagram で可視化する．p-value < 0.05 を有意とする．

## Implementation

2D datasets には 2D ResNet-18，3D datasets には 3D ResNet-18 backbone を使う．small datasets での overfitting を避け，既存文献の backbone と整合させるため light backbone を採用する．主要 objective は binary cross entropy loss．各 experiment は3つの random seeds で実行し，mean と standard deviation を報告する．

全体では 7,000 models 以上を training し，6,800 GPU-hours を使った．

## Results: ERM bias

overall performance-based selection で ERM を training し，各 dataset / sensitive attribute について subgroup 間の maximum / minimum AUC と underdiagnosis rate を比較した．Figure 3 では，多くの点が equality line から外れており，performance gap が広く存在することを示した．著者らは，bias が多様な modality，diagnosis task，sensitive attribute にわたって存在することを systematic に quantification したと述べる．

## Results: model selection

ERM に対して3つの model selection strategies を比較したところ，worst-case AUC metric では Pareto-optimal model selection strategy が average rank 約 1.5 で最良であり，overall AUC model selection strategy の average rank 約 2.5 より統計的に有意に良かった．

一方，overall AUC metric では Pareto selection strategy は overall model selection strategy と比べて有意に悪くなかった．したがって，明示的な bias mitigation algorithm がなくても，standard overall strategy の代わりに対応する model selection strategy を使うだけで max-min fairness を有意に改善でき，overall AUC に大きなコストを課さない可能性がある．

## Results: bias mitigation algorithms

Pareto model selection strategy を使い，全 methods を in-distribution / out-of-distribution で評価した．結果として，どの bias mitigation algorithm も ERM を統計的有意に上回らなかった．in-distribution では一部 significant performance differences があるが，ERM は常に highest-rank group に含まれ，どの metric でも ERM より有意に良い method はなかった．out-of-distribution でも結論は同じである．

いくつかの methods は一貫して良い傾向を示した．特に SWAD は worst-case AUC と overall AUC の両方で in-distribution / out-of-distribution ともに clear first rank だったが，統計的には ERM より有意に良いとは言えなかった．また，in-distribution で ERM より rank が高い method が unseen domain では悪化する場合があり，domain shift 下で fairness を保つことの難しさを示す．

## Discussion

著者らは，medical imaging fairness の評価では clinical application に応じて fairness definition を選ぶべきだとする．diagnosis のように全 subgroup を保護したい応用では Max-Min fairness が重要であり，resource allocation のような場面では group fairness が重視される場合がある．

また，bias mitigation algorithms が benchmark 全体で consistently effective ではないことは，それらを否定するものではなく，dataset / setting によって効果が異なることを示す．MEDFAIR は，future methods を複数 datasets / sensitive attributes / model selection strategies / OOD settings で評価する platform として位置づけられる．

## 結論

MEDFAIR は，医療画像 fairness を systematic に benchmark する framework である．主な発見は，bias は多 modality / task / sensitive attribute に広く存在すること，model selection strategy が fairness outcome に大きく影響すること，既存の state-of-the-art bias mitigation algorithms は ERM を統計的有意に上回らないことである．

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Medical_Image_Fairness_Audit_Loop]]
- [[Worst_Group_Performance]]
- [[Subgroup_Performance_Monitoring]]
- [[Max_Min_Fairness]]
- [[Group_Fairness]]
- [[Out_Of_Distribution_Fairness]]
