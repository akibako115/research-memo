---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_hyperfusion_hypernetwork_multimodal_tabular_medical_imaging.pdf"
---

# HyperFusion: A Hypernetwork Approach to Multimodal Integration of Tabular and Medical Imaging Data for Predictive Modeling

Daniel Duenias，Brennan Nichyporuk，Tal Arbel，Tammy Riklin Raviv らによる arXiv 論文．medical imaging と EHR 由来の tabular data を統合するために，tabular values から image-processing network の一部パラメータを生成する hypernetwork framework，HyperFusion を提案する．

HyperFusion は，tabular information を image analysis network の prior として使い，test time でも入力 tabular attributes に応じて primary network の重みを動的に調整する．brain age prediction conditioned by sex と，AD / MCI / CN の multi-class Alzheimer’s Disease classification conditioned by clinical / demographic / genetic tabular data で評価され，single-modality models と既存の MRI-tabular fusion methods を上回ったと報告される．

## 背景

医療の意思決定では，clinical，genetic，demographic，imaging information を統合して患者状態を理解する．しかし DNN は medical imaging と non-imaging data を統合する能力では人間専門家に及ばない．画像は high-dimensional，continuous，spatial であり，EHR 由来の numerical tabular data は low-dimensional で diverse types / scales / ranges を持つ．

Vision-Language Models は image-text の対応を contrastive learning で捉えるが，medical domain では image と concept の対応が non-uniform であり，一対一の semantic mapping がない場合が多い．image-tabular fusion ではさらに，body temperature のような tabular variable と chest X-ray の間に「正しい semantic match」があるわけではない．それでも組み合わせれば pneumonia assessment のようなタスクに有用である．

著者らは，clinical measurements と demographic data を image analysis network の結果に影響する prior として扱う．hypernetwork により，primary image-processing network の重みと bias の一部を tabular input に応じて生成する．

## Fusion methods との関係

医療画像と tabular data の fusion は，early fusion，joint / intermediate fusion，late fusion に分けられる．

- early fusion: original / extracted features を input level で concatenation する．end-to-end な mutual learning には不十分になりやすい．
- late fusion: predictions または pretrained high-level features を decision level で統合する．modalities 間の mutual learning が起きにくい．
- joint fusion: feature extraction phase を fusion model の一部として学習する．modalities が中間表現で相互作用できる．

HyperFusion は joint fusion に属する．既存の joint fusion では，image branch と tabular branch を別々に埋め込み，feature vector を concatenation する方法が多い．しかし concatenation は tabular data と imaging の interaction を high-level descriptor に限定し，spatial context が残る CNN layer での fusion を扱いにくい．

FiLM や DAFT は intermediate CNN layers に affine transformation を適用するが，著者らは，これらの方法では interaction が特定の処理段階と linear transformation に制限されると述べる．HyperFusion は，primary network の任意の layer parameter を hypernetwork が生成できるため，より general transformation を学習できるとする．

## HyperFusion の方法

HyperFusion は hypernetwork `H_φ` と primary network `P_θ` からなる．入力は tabular vector `T ∈ R^d` と multidimensional image `I`，具体的には 3D MRI である．

```text
T -> H_φ(T) = θ_H
I -> P_θ(I)
θ = {θ_H, θ_P}
```

hypernetwork `H_φ` は tabular vector `T` から data-specific な network parameters `θ_H` を生成する．primary network の全パラメータ `θ` は，hypernetwork が生成する external parameters `θ_H` と，通常の backpropagation で学習される internal parameters `θ_P` に分かれる．

hypernetwork block は `K` 個の subnetworks `{h_k}` からなり，各 `h_k` が tabular attributes を embedding し，primary network の対応する layer の weights / biases を生成する．training では loss が primary network と hypernetwork の両方に backpropagate するが，external primary parameters `θ_H` 自体は gradient descent で直接更新されず，hypernetwork output として間接的に変わる．

tabular dependency の強さは，external parameters と internal parameters の比率で決まる．全パラメータが internal なら予測は tabular information に依存しない．全パラメータを external にすると，tabular attribute combinations ごとに別 network を使う状況に近づく．著者らは，low-level image features には tabular attributes が関係しにくいと仮定し，low-level layers は internal，より後段の layers を external にする．

## Tabular embedding

hypernetwork は2段階で weights / biases を生成する．まず tabular data を embedding network に入力して latent vector を作る．次に，この latent vector を2つの linear layers に通し，1つは weights，もう1つは biases を生成する．embedding function は `ζ: R^d -> R^l`，`l < d` である．

著者らは tabular data に spatial context がないため，embedding network として MLP を使う．embedding は，tabular data の hidden patterns や interactions を保ちながら低次元表現にするための重要な fusion step とされる．

## Hyperlayer selection と initialization

primary network のどの layer を hypernetwork によって生成するかは，application ごとに決める必要がある．著者らは，untrained backbone network で各 layer を個別に random initialization し，loss distribution の entropy を計算することで hyperlayer candidate を選ぶ．最終的な layer selection は ablation によって経験的に決める．

hypernetwork output として生成される primary layer parameters は直接初期化できないため，Chang et al. (2019) に基づく variance analysis を用いて hypernetwork parameters を初期化する．目的は，生成された external primary parameters が，対象 layer の input variance と output variance を安定させる分布になることである．

## Loss と missing values

regression task では task loss は MSE，classification task では class imbalance を考慮した Weighted Cross-Entropy（WCE）を使う．全 loss は task-specific loss と weight decay regularization の和である．regularization は hypernetwork parameters `φ` と internal primary parameters `θ_P` に適用される．external primary parameters `θ_H` は gradient descent を直接受けないため regularize されない．

missing values は iterative imputation で補完し，imputed values を示す indicator / NaN flag を追加する．著者らは，missingness indicator が class-specific に欠測する属性を通じて unfair cue になりうること，ある class の imputation が別 class の値に強く依存しうることを注意点として述べる．

## Brain age prediction conditioned by sex

brain age prediction では，primary network は healthy subjects の T1w 3D brain MRI を入力し，hypernetwork は subject sex を表す 2D one-hot vector を入力する．primary network は VGG backbone variant で，final four linear layers の parameters が hypernetwork によって生成される．task は regression であり，loss は MSE と weight decay regularization の和である．

データは 19 sources からなる 26,691 brain MRI scans である．train / validation / test は 80% / 10% / 10% に分割し，age と sex distribution を保つ．評価指標は chronological age と predicted age の Mean Absolute Error（MAE）である．test は validation で選んだ5つの best-performing models の ensemble average で評価する．

著者らはまず，male-only，female-only，mixed data で training した imaging-only CNN を比較し，sex information が brain age prediction に有用であるという仮説を確認する．次に HyperFusion を image-only baseline と，sex と image features を各 linear layer で結合する concatenation model と比較する．Figure 4 の結果では，HyperFusion は male-only，female-only，mixed test の全条件で image-only network と concatenation framework を上回ったと述べられる．また female age prediction の方が male age prediction より正確であり，男性の brain age variability が大きい可能性が示唆される．

## AD classification

AD classification では，ADNI1，ADNI2，ADNI GO，ADNI3 から各個人の first visit の T1 MRI と対応する EHR を使い，CN / MCI / AD の3クラス分類を行う．データ統計は以下である．

| Diagnosis | N (%) | Age mean ± std | Sex M:F |
| --- | ---: | ---: | ---: |
| AD | 365 (17.2%) | 75.1 ± 7.8 | 198:167 |
| CN | 740 (34.9%) | 72.2 ± 6.8 | 309:431 |
| MCI | 1015 (47.9%) | 72.8 ± 7.6 | 569:446 |
| Overall | 2120 (100%) | 73.0 ± 7.4 | 1076:1044 |

MRI は左右 hippocampus 周辺の 3D sub-images `64 × 96 × 64` に crop される．tabular features は9つであり，demographic attributes（age，sex，education），CSF biomarkers（Aβ42，P-tau181，T-tau），PET由来 composite measures（FDG，AV45）を含む．cognitive scores は AD diagnosis に直接使われるため除外された．binary / discrete attributes は one-hot，continuous attributes は zero mean / unit std に正規化された．

primary network は pre-activation ResNet blocks と2つの linear layers からなる．最後の ResNet block（HyperRes block）の convolutional layer の一部 parameter が hypernetwork から生成される．hypernetwork は single-layer MLP with P-ReLU embedding を使い，primary network の weights / biases を生成する．

## Training と evaluation

AD classification は Adam optimizer，250 epochs，batch size 32，weight decay `1e-5`，learning rate `1e-4` で学習される．class imbalance には WCE loss を用いる．embedding MLP は training tabular data のみで事前学習され，convergence を速める．

各 subject の imaging data は left / right hippocampus の2つの 3D subimages を含む．training では feed-forward ごとに一方を random に選ぶ data augmentation を行い，validation / testing では左右を両方処理して soft decisions を平均する．さらに ensemble model を用いる．

robustness のため，3つの split seeds と，各 split seed につき3つの random initializations（versions）を使う cross-validation を行う．各 cross-validation iteration では4モデルを train / validate し，特定 version / split seed の4モデルを aggregation して shared unseen test set で評価する．

metrics は balanced accuracy（BA），precision（PRC），macro AUC，macro F1，class-wise true positive rates（TP-CN，TP-MCI，TP-AD）である．

## AD classification results

主な結果は以下である．`DAFT-like` と `FiLM-like` は著者らが同じ primary backbone / training regimen で適応実装したものを指す．

| Model | BA | PRC | F1 macro | AUC macro | TP-CN | TP-MCI | TP-AD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Imaging only | 0.579 ± 0.018 | 0.527 ± 0.016 | 0.534 ± 0.016 | 0.721 ± 0.018 | 0.627 ± 0.078 | 0.395 ± 0.063 | 0.714 ± 0.028 |
| Tabular only | 0.602 ± 0.011 | 0.555 ± 0.011 | 0.554 ± 0.018 | 0.775 ± 0.011 | 0.668 ± 0.048 | 0.418 ± 0.060 | 0.721 ± 0.024 |
| Concatenation | 0.638 ± 0.008 | 0.582 ± 0.009 | 0.589 ± 0.011 | 0.792 ± 0.008 | 0.751 ± 0.044 | 0.408 ± 0.039 | 0.755 ± 0.025 |
| FiLM-like implementation | 0.635 ± 0.014 | 0.592 ± 0.016 | 0.600 ± 0.017 | 0.804 ± 0.007 | 0.733 ± 0.040 | 0.477 ± 0.049 | 0.696 ± 0.032 |
| DAFT-like implementation | 0.658 ± 0.014 | 0.608 ± 0.012 | 0.614 ± 0.014 | 0.815 ± 0.005 | 0.765 ± 0.041 | 0.462 ± 0.042 | 0.748 ± 0.060 |
| HyperFusion | 0.673 ± 0.012 | 0.624 ± 0.012 | 0.630 ± 0.011 | 0.822 ± 0.006 | 0.759 ± 0.053 | 0.495 ± 0.052 | 0.764 ± 0.052 |
| Reported DAFT results | 0.622 ± 0.044 | - | 0.600 ± 0.045 | - | 0.767 ± 0.080 | 0.449 ± 0.154 | 0.651 ± 0.144 |
| Reported late-fusion results | 0.6330 | 0.6473 | 0.6240 | - | - | - | - |

全 multimodal methods は unimodal models を上回った．HyperFusion は global metrics と class-specific metrics の多くで最良であり，Mann-Whitney U tests で他手法との差の統計的有意性を評価した．特に MCI の TP rate は 0.495 ± 0.052 で，imaging only，tabular only，concatenation，DAFT-like より高い．

class imbalance 対応については，appendix の ablation で WCE loss，CE with upsampling，CE without upsampling を比較している．結果は WCE loss が BA 0.673，PRC 0.624，F1 macro 0.630，AUC macro 0.822 で最良だった．

## 結論

HyperFusion は，tabular data に基づいて medical image processing network の一部重みを生成する hypernetwork-based fusion framework である．著者らは，EHR を通して患者の画像を見るように image analysis を conditioning する方法だと説明する．brain age prediction と AD classification の2つの clinical applications で，image-only，tabular-only，concatenation，FiLM-like，DAFT-like を上回った．

今後の方向として，EHR が image analysis を condition するだけでなく，image が EHR analysis を condition する逆方向の設計や，CNN / MLP 以外の architecture への hypernetwork integration が挙げられる．

## 関連概念

- [[HyperFusion]]
- [[Hypernetwork]]
- [[Image_Tabular_Fusion]]
- [[Conditional_Modulation]]
- [[Medical_Image_Tabular_Fusion]]
- [[Alzheimer_Disease_Prediction]]
- [[Brain_Age_Prediction]]
