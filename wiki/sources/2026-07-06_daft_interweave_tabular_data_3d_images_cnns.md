---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_daft_interweave_tabular_data_3d_images_cnns.pdf"
---

# DAFT: A universal module to interweave tabular data and 3D images in CNNs

Tom Nuno Wolf，Sebastian Pölsterl，Christian Wachinger らによる NeuroImage 2022 論文．Alzheimer’s Disease（AD）診断と time-to-dementia prediction において，3D MRI と tabular clinical information を CNN 内で統合する Dynamic Affine Feature Map Transform（DAFT）を提案する．

DAFT は，3D CNN の convolutional feature maps を，患者の画像特徴と tabular data の両方に条件づけて scale / shift する汎用 module である．AD diagnosis では mean balanced accuracy 0.622，time-to-dementia prediction では mean c-index 0.748 を達成し，論文中の全 baseline を上回った．

## 背景

AD の診断では，MRI から CNN が neuroanatomy の高次表現を抽出できる一方で，demographics，family history，CSF laboratory measurements，genetic alterations などの tabular biomarkers も重要である．tabular variables は低次元だが，各変数が rich clinical knowledge を持つ．一方，image information は high-dimensional で continuous-valued であり，voxel 単位では情報が少ない．

既存の deep learning approach では，latent image representation と tabular data を最後の fully-connected layer 付近で concatenation することが多い．しかしこの方法では，image-specific part と tabular-specific part の相互作用が final global descriptor に限定され，voxel / patch level の fine-grained interaction ができない．

著者らは，image と tabular data が相補的である一方，image feature と tabular feature には冗長性もあると指摘する．たとえば CNN が MRI から年齢に対応する特徴を抽出するなら，それは tabular data として既に利用可能な情報と重複している．したがって，片方の情報がもう片方を文脈づける bidirectional exchange が必要だとする．

## 関連手法

論文は既存の統合方法を以下のように整理する．

- two-stage approach: 画像 CNN を先に学習し，その prediction / latent representation と tabular data を結合して別の linear model を学習する．CNN は tabular data と冗長な image descriptor を学ぶ可能性がある．
- end-to-end concatenation: latent image representation と clinical information を最後の FC layer 前で結合する．tabular data の寄与は線形になりやすい．
- MLP after concatenation: concatenated vector を MLP に通すことで非線形関係を学習できるが，parameter が増えて overfitting しやすい．
- Duanmu et al. (2020): tabular data から scalar scaling factor を生成し，CNN feature maps を rescale する．ただし auxiliary network size が CNN depth とともに大きくなる．
- FiLM: conditioning input から scaling factor と offset を生成し，feature maps を affine transform する．visual question answering や cardiac segmentation で使われている．

FiLM や Duanmu et al. では，conditioning は tabular / meta information から image feature への one-way flow である．DAFT は image feature と tabular data の両方を auxiliary network に入れることで，image と tabular の bidirectional flow を意図する．

## DAFT の方法

DAFT は 3D convolutional layer の feature map `F_{i,c}` を，患者 `i` の tabular data `x_i` と image feature map 自身に基づいて affine transform する．

```text
F'_{i,c} = α_{i,c} F_{i,c} + β_{i,c}
α_{i,c} = f_c(F_{i,c}, x_i)
β_{i,c} = g_c(F_{i,c}, x_i)
```

実装では，単一の auxiliary neural network が `(α, β)` pair を出力する．処理手順は以下である．

1. feature map `F_i` の spatial dimensions を global average pooling で squeeze する．
2. 得られた image feature vector と tabular vector `x_i` を concatenation する．
3. FC layer と ReLU で bottleneck に圧縮する．圧縮率は `r = 7`．
4. 2つ目の FC layer で channel 数 `C` に対応する scale `α_i` と offset `β_i` を出力する．
5. `F_{i,c}` に `α_{i,c} F_{i,c} + β_{i,c}` を適用する．

DAFT は dataset size や feature map の spatial resolution に依存しないため，計算効率が良い．論文の主構成では ResNet backbone の最後の residual block に DAFT を入れる．著者らは，CNN の初期層は edge や blob のような primitive concept を扱うため，tabular data との level exchange は late convolutional layer の high-level concept に対して行うのが妥当だと述べる．

## 学習タスクとデータ

DAFT は T1 brain MRI を使う2つのタスクで評価された．

- diagnosis task: cognitively normal（CN），mild cognitively impaired（MCI），demented（AD）の multi-class classification．loss は cross-entropy．
- time-to-dementia task: MCI cohort の dementia onset time を予測する survival analysis．right censoring を考慮し，Cox model の negative partial log-likelihood を最小化する．

データは ADNI と AIBL から取得される．ADNI の baseline statistics は以下である．

| Task | Subjects | Age | Sex male | Education | MMSE | Diagnosis |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Diagnosis | 1341 | 73.9 ± 7.2 | 51.8% | 15.9 ± 2.9 | 27.2 ± 2.7 | Dementia 19.6%，MCI 40.1%，CN 40.3% |
| Progression | 755 | 73.5 ± 7.3 | 60.4% | 15.9 ± 2.9 | 27.5 ± 1.8 | Progressor 37.4%，median follow-up 2.01 years |
| AIBL | 653 | 72.9 ± 6.6 | 43.6% | N/A | 27.5 ± 3.5 | Dementia 11.6%，MCI 15.5%，CN 72.9% |

画像は T1-weighted MRI を minimal preprocessing し，FreeSurfer 5.3 で segmentation して，AD に強く影響される left hippocampus 周辺の `64^3` ROI を抽出する．

tabular features は ApoE4，CSF biomarkers `Aβ42`，`P-tau181`，`T-tau`，age，gender，education，FDG-PET summary，AV45-PET summary の9変数である．missing values には binary missing indicator を追加し，age / gender / education を除く missingness を表す．結果として `P = 15` features になる．ADNI と AIBL の repeatability / generalization 実験では，両方で利用可能な ApoE4，age，gender，ApoE4 missing indicator の4 features を使う．

## Baseline

比較対象は以下である．

- Linear Model: tabular information only．diagnosis では multinomial logistic regression，time-to-dementia では Cox proportional hazards model．
- ResNet: image information only．
- Linear Model with ResNet features: ResNet の latent image representation と tabular data を linear model に入れる two-stage approach．
- Concat-1FC: global average pooling 後の latent image feature と tabular vector を結合し，final classification layer に入れる．tabular transform は線形．
- Concat-2FC: concatenated vector を two-layer FC bottleneck with ReLU に入れる．
- 1FC-Concat-1FC: tabular data を two-layer FC bottleneck に通してから latent image representation と結合する．
- Duanmu et al. (2020): tabular data に条件づけて convolutional feature maps を scale する．
- FiLM: tabular data に条件づけて last residual block の convolutional feature maps を scale and shift する．
- DAFT: image feature と tabular data の両方に条件づけて scale and shift する．

ResNet に対する追加 parameter 数は，diagnosis task で Concat-1FC +45，Concat-2FC +108，1FC-Concat-1FC +76，Duanmu +328，FiLM +188，DAFT +252 である．

## 評価指標

diagnosis task では，class imbalance を考慮する balanced accuracy（bACC），micro / macro averaged F1，class-wise true positive fraction（TPF）を報告する．

time-to-dementia task では，discrimination を inverse probability of censoring weighted c-index で評価し，discrimination と calibration を integrated time-dependent Brier score（IBS）で評価する．IBS は初回 MCI diagnosis から 6-36 months の間の 31 time points で積分する．

## Diagnosis task の結果

balanced accuracy の主な結果は以下である．

| Model | Test bACC |
| --- | ---: |
| Linear Model | 0.552 ± 0.020 |
| ResNet | 0.504 ± 0.016 |
| Linear Model /w ResNet Features | 0.560 ± 0.055 |
| Concat-1FC | 0.587 ± 0.045 |
| Concat-2FC | 0.576 ± 0.036 |
| 1FC-Concat-1FC | 0.591 ± 0.024 |
| Duanmu et al. | 0.578 ± 0.019 |
| FiLM | 0.601 ± 0.036 |
| DAFT | 0.622 ± 0.044 |

DAFT は全比較手法を少なくとも +0.021 bACC 上回った．micro-F1 は 0.617 ± 0.040，macro-F1 は 0.600 ± 0.045 で，どちらも最高だった．FiLM は baseline の中では最良の bACC だが，DAFT はさらに上回った．

class-wise には，DAFT の TPF は CN 0.767 ± 0.080，MCI 0.449 ± 0.154，AD 0.651 ± 0.144 である．FiLM と比較した confusion matrix では，DAFT は MCI patients を AD と誤分類する数を 31 patients（19%）減らし，CN patients を MCI / AD と誤分類する数を 18 patients（12.5%）減らした．

## Time-to-dementia task の結果

time-to-dementia prediction の主な結果は以下である．

| Model | Test c-index | Test IBS |
| --- | ---: | ---: |
| Kaplan-Meier | N/A | 0.148 ± 0.007 |
| Linear Model | 0.719 ± 0.077 | 0.122 ± 0.013 |
| ResNet | 0.599 ± 0.054 | 0.145 ± 0.013 |
| Linear Model /w ResNet Features | 0.693 ± 0.044 | 0.135 ± 0.011 |
| Concat-1FC | 0.729 ± 0.086 | 0.122 ± 0.011 |
| Concat-2FC | 0.725 ± 0.039 | 0.130 ± 0.011 |
| 1FC-Concat-1FC | 0.723 ± 0.056 | 0.125 ± 0.008 |
| Duanmu et al. | 0.706 ± 0.086 | 0.128 ± 0.017 |
| FiLM | 0.712 ± 0.060 | 0.131 ± 0.022 |
| DAFT | 0.748 ± 0.045 | 0.122 ± 0.015 |

DAFT は全モデルを少なくとも +0.019 c-index 上回った．IBS では Linear Model と Concat-1FC と同等の 0.122 を示し，c-index の改善が calibration の大きな悪化を伴わないことを示す．著者らは，time-to-dementia task では image と tabular information の two-way exchange が重要だと述べる．

## Ablation

DAFT の location，scale activation，scale / shift の有無を変えた ablation の主な結果は以下である．

| Configuration | Balanced accuracy | Concordance index |
| --- | ---: | ---: |
| Before Last ResBlock | 0.598 ± 0.038 | 0.749 ± 0.052 |
| Before Identity-Conv | 0.616 ± 0.018 | 0.745 ± 0.036 |
| Before 1st ReLU | 0.622 ± 0.024 | 0.713 ± 0.085 |
| Before 2nd Conv | 0.612 ± 0.034 | 0.759 ± 0.052 |
| `α_i = 1` | 0.581 ± 0.053 | 0.743 ± 0.015 |
| `β_i = 0` | 0.609 ± 0.024 | 0.746 ± 0.057 |
| `σ(x) = sigmoid(x)` | 0.600 ± 0.025 | 0.756 ± 0.064 |
| `σ(x) = tanh(x)` | 0.600 ± 0.025 | 0.770 ± 0.047 |
| Proposed | 0.622 ± 0.044 | 0.748 ± 0.045 |

DAFT は location に対して比較的頑健であり，diagnosis task ではほとんどの location で他モデルを上回った．`α_i = 1` または `β_i = 0` にすると両タスクで性能が低下した．diagnosis では scaling の方が shifting より重要に見える一方，progression では scale / shift の片方だけでも variance の範囲内に収まる．scale に sigmoid / tanh をかけると diagnosis performance は下がるが，progression の mean c-index は上がる．

## Scale / shift の解析

著者らは，FiLM と DAFT の `α` / `β` の挙動を比較するため，標準 ResNet を convergence まで学習し，その重みで FiLM / DAFT block 付き ResNet を初期化して，last ResBlock と FC layer 以外を固定した．この設定により，FiLM / DAFT block への input feature maps を同一にして比較した．

FiLM が出す `α` / `β` は 0 付近に集まることが多い一方，DAFT の `α` / `β` はほぼ常に 0 から一貫して離れた値を取る．DAFT の clusters は compact で，両次元に比較的均等に散らばる．

training set mean で `α` または `β` を置き換えて conditioning information を除く test-time ablation では，DAFT は `β` を固定したときに大きく性能低下し，tabular information を shifting feature maps によって効果的に統合していることが示唆された．Gaussian noise を加えた実験でも，DAFT は `β` の distortion により敏感で，FiLM は `α` と `β` の両方に同程度に影響を受けた．また，FiLM は noise による性能劣化が DAFT より速かった．

## Tabular feature の寄与

DAFT の diagnosis task で，tabular features の marginal contribution を Baseline Shapley approach で推定した．Shapley values は，tabular feature subset を使う model の balanced accuracy 差から計算され，全 feature の寄与和が no-tabular model から full-tabular model への改善に対応する．

5 folds の DAFT-based models で最も重要だった features は FDG-PET，T-tau，Aβ42 だった．著者らは，FDG-PET による cortical metabolic activity の低下，CSF total tau 高値，CSF Aβ42 低値はいずれも AD の既知 marker であるため，この結果は妥当だと述べる．

## AIBL generalization と repeatability

ADNI と AIBL の両方で使える reduced tabular features（age，gender，ApoE4，ApoE4 missing indicator）で全モデルを再学習し，15 random initializations を含む repeatability study を行った．

| Model | ADNI Test bACC | AIBL Hold-out bACC |
| --- | ---: | ---: |
| Linear Model | 0.417 ± 0.033 | 0.417 ± 0.009 |
| ResNet | 0.514 ± 0.036 | 0.493 ± 0.021 |
| Linear Model /w ResNet Features | 0.536 ± 0.039 | 0.510 ± 0.021 |
| Concat-1FC | 0.534 ± 0.041 | 0.515 ± 0.029 |
| Concat-2FC | 0.491 ± 0.098 | 0.475 ± 0.084 |
| 1FC-Concat-1FC | 0.534 ± 0.042 | 0.515 ± 0.025 |
| Duanmu et al. | 0.513 ± 0.042 | 0.510 ± 0.039 |
| FiLM | 0.541 ± 0.036 | 0.523 ± 0.028 |
| DAFT | 0.550 ± 0.033 | 0.527 ± 0.024 |

DAFT は ADNI と AIBL の両方で最高 bACC だった．FiLM との差は ADNI で +0.009，AIBL で +0.004 である．ただし，FiLM との差については corrected p-values が ADNI で 0.12，AIBL で 0.297 であり，有意差は弱い．著者らは，channel-level feature merging が concatenation-based approaches より優れることを補強すると述べる．

## Backbone 変更

DAFT が任意の CNN に適用できることを確認するため，ResNet から skip connection を除いた ConvNet backbone でも診断タスクを評価した．

| Model | Test bACC |
| --- | ---: |
| Linear Model | 0.582 ± 0.044 |
| ConvNet | 0.519 ± 0.027 |
| Linear Model /w ConvNet Features | 0.534 ± 0.031 |
| Concat-1FC | 0.604 ± 0.039 |
| Concat-2FC | 0.580 ± 0.018 |
| 1FC-Concat-1FC | 0.579 ± 0.033 |
| Duanmu et al. | 0.571 ± 0.033 |
| FiLM | 0.604 ± 0.018 |
| DAFT | 0.617 ± 0.018 |

ConvNet backbone でも DAFT は全手法を +0.013 bACC 以上上回り，backbone に依存しない統合能力を示した．

## 結論

DAFT は，3D image feature maps を患者の image feature と tabular clinical information の両方に基づいて動的に scale and shift する module である．AD diagnosis と time-to-dementia prediction の両方で，concatenation-based approaches や tabular-only FiLM を上回った．著者らは，CNN が抽出する high-level image features は臨床 tabular biomarkers と部分的に冗長であり，DAFT はその冗長性を扱いながら complementary information を統合できると結論づける．

## 関連概念

- [[Image_Tabular_Fusion]]
- [[DAFT]]
- [[FiLM]]
- [[Conditional_Modulation]]
- [[Medical_Image_Tabular_Fusion]]
- [[Survival_Analysis]]
- [[Alzheimer_Disease_Prediction]]
