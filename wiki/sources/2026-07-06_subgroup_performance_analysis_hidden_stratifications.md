---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_subgroup_performance_analysis_hidden_stratifications.pdf"
---

# Subgroup Performance Analysis in Hidden Stratifications

Alceu Bissoto，Trung-Dung Hoang，Tim Flühmann，Susu Sun，Christian F. Baumgartner，Lisa M. Koch による論文．医療画像分類モデルの performance monitoring に subgroup discovery を適用し，metadata-based subgroup analysis では見えない hidden stratification による performance disparity を発見できることを示す．対象は chest x-ray と skin lesion classification である．

著者らは，DOMINO を簡略化した subgroup discovery method を用い，classification labels や metadata にアクセスせずに learned feature representation から subgroups を見つける．synthetic artifacts による controlled setting と real-world medical image setting の両方で評価し，traditional metadata-based subgroup analysis より大きな performance gap を露出できると報告する．

## 問題設定

ML models は patient subgroups 間で systematic performance difference を持つことがある．metadata-based subgroup analysis は，patient sex，age，ethnicity，image quality，artifacts，device manufacturer などの metadata が存在し，かつ性能変動の主因を十分に反映する場合には disparity を発見できる．しかし，現実の metadata は限られており，available metadata が data variability や model に重要な concept を十分に捉えるとは限らない．

このため hidden stratifications が存在し，ML model evaluation では performance disparities が見落とされる可能性がある．著者らは，subgroup discovery を performance monitoring に使うことで，hidden stratification を発見し，より granular な subgroup performance report を作れると考える．

## Contribution

論文の主な contribution は以下である．

- subgroup discovery が medical imaging における performance gaps を系統的に露出できることを，synthetic と real-world の両方で示す．
- discovered subgroups の quality を評価する novel metrics として performance gap と average purity を導入する．
- discovered subgroups が conventional demographic metadata より大きな performance disparities を示し，traditional fairness auditing が見落とす gap を明らかにすることを示す．

## Subgroup discovery algorithm

著者らは subgroup discovery に DOMINO を使う．まず，外部 pretrained model（CLIP など）から image `x` の feature representation `z(x)` を抽出し，PCA で次元削減する．target classification model から softmax predictions `ŷ(x)` も取得する．

外部 model は artifacts など task-agnostic features を捉える役割を持ち，target model predictions は classification task に重要な characteristics を反映する．これらを使い，generalised Gaussian Mixture Model（GMM）で samples を subgroups `S` に clustering する．

original DOMINO と異なり，本論文では GMM から classification labels を除き，unlabeled test set を使う post-deployment scenario でも subgroup discovery を可能にする．DOMINO は validation set に fit し，test set に subgroup を infer する．

## Synthetic scenario

synthetic setting では，ground truth subgroups と subgroup performances が既知になるよう，positive disease label と spuriously correlated な synthetic artifacts を追加する．2つの artifacts を独立に label と相関させ，一方は traditional subgroup analysis が使える known attribute，もう一方は hidden stratification とする．

artifacts は positive samples に probability / bias level `p` で挿入され，negative samples には `1 - p` で挿入される．これにより4つの ground truth subgroups ができる．training / validation は biased data で生成され，test は unbiased test set（`p = 0.5`）を使う．bias level は `p ∈ {0.6, 0.7, 0.8}` である．

CheXpertPlus に対して，hyperintensities を known attribute，hospital tags を hidden stratification とした．

## Real-world scenario

real-world setting では hidden stratification の ground truth labels が存在しない．著者らは measured metadata（patient age，sex など）を baseline stratification method として使い，現在の subgroup performance analysis の標準的実務と比較する．

metadata attribute ごとに subgroup division を作り，各 sample に対応する attribute performance を割り当てる．複数 metadata attributes の performance values を平均して，sample ごとの overall performance metric を得る．subgroup discovery では random seed による stochastic effects を周辺化するため，同じ考え方で discovered subgroup performances をより robust に推定する．

## Evaluation metrics

理想的な stratification は，cohesive subgroups の間に systematic performance difference を生む．著者らは2つの評価指標を導入する．

### Performance gap

subgroup division `S` の performance gap は以下で定義される．

```text
Δ(S) = max_{s ∈ S} M(s) - min_{s ∈ S} M(s)
```

`M(s)` は subgroup `s` における model performance，たとえば accuracy である．

### Average purity

average purity は subgroup cohesion を測る指標であり，subgroups が known attributes（artifact presence や patient characteristics）とどの程度 align するかを計算する．各 subgroup について majority attribute の fraction を使い，小さい subgroup に対する robustness のため correction term `c` を入れる．

## Datasets

CheXpertPlus は CheXpert の拡張であり，patient demographics（sex，age），comorbidities（edema，fracture），artifacts など計20 attributes の metadata を持つ．train / validation / test は 80 / 10 / 10 で，178,684 / 22,263 / 22,281 images である．task は “cardiomegaly vs. all”．

SLICE-3D は skin lesion classification dataset であり，patient details（sex，age）に加え，lesion hue / size など diagnostic-relevant visual traits を含む．dataset imbalance のため，validation / test に多めに sample を割り当て，Patient IDs を 60 / 20 / 20 に分割する．images は 252,047 / 80,516 / 68,496．task は “malignant vs. benign”．

## Experimental setup

classification model は ResNet-50 で，SGD を使い，learning rate `{10^-5, 10^-4, 10^-3}`，weight decay `10^-4` を探索した．model selection は CheXpertPlus では validation balanced accuracy，SLICE-3D では thresholded AUC に基づく．

subgroup discovery では常に 15 subgroups を使った．external model は全 scenario で pretrained CLIP を使い，real-world CheXpertPlus では BiomedCLIP も比較した．primary metric は subgroup performance gap と subgroup performance の accuracy である．

## Synthetic results

synthetic setting では，subgroup discovery は bias level `0.6, 0.7, 0.8` のすべてで，traditional subgroups より大きな performance gaps を露出し，cohesion も保った．DOMINO の hyperparameter `γ` を上げると performance gap と purity には trade-off があり，gap は増えるが，ある点を超えると purity が急に下がる．著者らは elbow point を選び，synthetic と real-world CheXpertPlus では `γ = 10`，SLICE-3D では `γ = 50` とした．

known artifact に基づく subgroup analysis は bias level が上がるにつれて performance gap を示したが，hidden second artifact によるより大きな performance gap を見逃した．classification labels や artifact annotations にアクセスしない subgroup discovery は，hidden subgroup performance を捉える subgroups を発見した．

## Real-world results

real-world chest x-ray と skin lesion analysis では，subgroup discovery は traditional metadata-based analysis より大きな performance gaps を見つけた．

CheXpertPlus では，subgroup discovery は accuracy 60% 未満の underperforming subgroups を一貫して見つけた一方，多くの subgroups は約90% accuracy だった．metadata-based analysis はこのような low-performing subgroups を露出せず，全体として performance range が狭かった．

SLICE-3D では，subgroup discovery が 721 negatives と 17 positives を含む subgroup を見つけ，accuracy は 5% だけだった．

## Discovered subgroup の性質

CheXpertPlus では，discovered subgroups は patient sex，age，ethnicity など available metadata で記述される concept とあまり align せず，これらの attribute に対する purity は低かった．これは，available metadata が real-world data distribution の main factors of variability を反映しないことを示す．

SLICE-3D では，lesion area や color などの visual features によって discovered subgroups がよく stratified された．これらは melanoma diagnosis に関連する feature だが，これらの annotated lesion characteristics に基づく subgroup analysis だけでは，subgroup discovery が観察した performance disparities は露出しなかった．

## CLIP と BiomedCLIP

CheXpertPlus で BiomedCLIP を feature extractor として使い，biomedical data で学習した representation が disease-related features の stratification を改善するかを調べた．結果として，BiomedCLIP と original CLIP は subgroup purity と performance disparities が類似していた．著者らは，natural images で訓練された feature extractor でも，real-world data distribution における meaningful performance gaps を露出できると述べる．

## 結論

hidden stratifications は synthetic / real-world data の両方で performance disparities を生み，traditional metadata-based subgroup analysis では検出できないことが多い．subgroup discovery は cohesive subgroups 間の substantial and systematic performance disparities を露出した．著者らは，subgroup discovery を performance monitoring and reporting tool として重視し，traditional subgroup analysis に加える safeguard として real-world ML validation / deployment に伴わせるべきだと主張する．

## 関連概念

- [[Subgroup_Performance_Monitoring]]
- [[Hidden_Stratification]]
- [[Algorithmic_Subgroup_Discovery]]
- [[Worst_Group_Performance]]
- [[Medical_Image_Fairness_Audit_Loop]]
- [[DOMINO]]
