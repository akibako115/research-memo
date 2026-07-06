---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_fairread_demographic_refusion_medical_image_classification.pdf"
---

# FairREAD: Re-fusing Demographic Attributes after Disentanglement for Fair Medical Image Classification

この論文は，医療画像分類において sensitive demographic attributes を画像表現から単純に除去すると，臨床的に有用な情報まで失われる可能性があるという問題に対し，Fair Re-fusion After Disentanglement (FairREAD) を提案する．FairREAD は，まず image representation から demographic information を disentangle し，その後 controlled re-fusion mechanism で demographic attributes を再統合する．

著者らは，CheXpert の chest X-ray classification で，gender，age，race を sensitive attributes として扱い，Cardiomegaly，Pleural Effusion，Pneumonia，Fracture の4疾患を評価する．FairREAD は fairness metrics を改善しつつ AUC を保ち，CheXpert で学習して MIMIC-CXR で評価する OOD setting でも baseline methods より良い performance-fairness trade-off を示したと報告している．

## 背景

医療画像 model は race，gender，age などの sensitive information を内部に encode し，demographic subgroups 間で performance disparities を生むことがある．既存の fairness mitigation は，sensitive attributes を image representation から suppress / remove する方向が多い．しかし sensitive attributes は疾患 prevalence や manifestation と関係する場合があり，単純な除去は diagnostic performance を損なう可能性がある．

FairREAD の中心的な発想は，demographic attributes に関係する potentially spurious correlations を画像表現から除いたうえで，demographic attributes 自体は controlled に再注入して診断に使うことである．

## FairREAD の構成

FairREAD は3つの component からなる．

| Component | 役割 |
| --- | --- |
| Fair Image Encoder (FIE) | image representation から demographic information を除く |
| Re-fusion mechanism | fair image representation に demographic attributes を controlled に融合する |
| subgroup-specific threshold | subgroup ごとに threshold を調整して decision disparity を減らす |

Figure 1 では，chest X-ray image が FIE により demographic attribute-invariant representation `z_T` に変換され，adversarial demographic attribute classifier により demographic attributes が recoverable でないように訓練される．その後，`z_T` は re-fusion blocks と convolution blocks を含む re-fusion module に渡され，demographic information が latent space の rescaling として統合される．最後に subgroup-specific threshold で classification result が得られる．

## Fair Image Encoder

FIE は，target representation `z_T` と sensitive representation `z_A` を分けるため，orthogonality constraints と adversarial training を使う．

| Loss | 目的 |
| --- | --- |
| column space orthogonality loss | target latent features が sensitive space に射影されないようにする |
| row space orthogonality loss | target representation の各 feature dimension と sensitive representation を orthogonal にする |
| adversarial loss | `z_T` から demographic attributes を予測できないようにする |

first stage では，image-to-demographic-attribute classifier `f_A` を学習し，image-to-target classifier `f_T` を classification loss と column / row orthogonality loss で学習する．second stage では，FairREAD 全体を cross-entropy loss で学習しつつ，adversarial classifier を反復的に訓練して FIE が demographic attributes を再び encode しないようにする．

## Re-fusion mechanism

re-fusion では，demographic attributes `a` を MLP に入力し，feature rescaling 用の `mu` と `sigma^2` を出力する．fair image representation `z_T` は低次元へ projection され，`mu` と `sigma^2` により rescale され，元の次元へ戻される．

```text
z_T = FairImageEncoder(x)
mu, sigma^2 = MLP(a)
z_fused = Re-fusion(z_T, mu, sigma^2)
```

re-fusion block は，fair representation を demographic attributes で rescale する latent-space fusion として機能する．この sequence は re-fusion block + convolution block として `N` 回繰り返され，最後に fully-connected layer が logit を出す．

## Subgroup-specific threshold

FairREAD は，logit から binary classification を得る際に subgroup-specific threshold を使う．各 subgroup `g` に対して，TPR と TNR の差が最小になる threshold を選ぶ．

```text
theta_g = argmin_s |TPR_g,s - TNR_g,s|
```

著者らはこれを Min-gap strategy と呼ぶ．threshold fitting は training set 上で行われ，label imbalance と subgroup imbalance が存在する状況で subgroup-specific threshold を決める．

## Dataset

CheXpert を用いる．CheXpert は 224,316 chest X-ray images，65,240 patients を含む public dataset である．評価対象 pathology は Cardiomegaly，Pleural Effusion，Pneumonia，Fracture の4つである．

sensitive attributes は gender，age，primary race の3つで，binary values に離散化する．age は <60 / >=60，race は White / Non-white，gender は Male / Female を用いる．著者らは fairness mitigation の効果を見やすくするため，CheXpert を subsampling して subgroup disparity を拡大している．Cardiomegaly と Pleural Effusion では positive rate disparity を約16%，Pneumonia と Fracture では約10% にする．

Table 1 では，たとえば Cardiomegaly の sample ratio は Male 75.28% / Female 24.72%，White 64.57% / Non-White 35.43%，>=60 59.73% / <60 40.27% であり，positive rates は Male 14.86% / Female 30.12%，White 13.46% / Non-White 28.05%，>=60 24.31% / <60 10.21% と報告されている．

## Baselines and metrics

baselines は ERM，FCRO，Learning Not To Learn (LNTL)，FairAdaBN，Adversarial Learning (AL) である．fair comparison のため，すべての baseline methods にも Min-gap subgroup-specific threshold selection を適用する．

performance metrics は accuracy と AUC，fairness metrics は `Delta EO` と `Delta AUC` である．また performance-fairness trade-off を測る comprehensive metrics として `FATE_EO` と `FATE_AUC` を用いる．

## 結果

Table 2 では，FairREAD が平均で AUC 0.839，Delta AUC 0.076，Delta EO 0.129，FATE_EO 0.196，FATE_AUC 0.197 を示し，accuracy 以外の全平均 metric で baseline methods を上回った．FCRO は平均 accuracy 0.782 と高いが，AUC は0.788，FATE_AUC は -0.029 であり，FairREAD より performance-fairness trade-off が悪い．

疾患別には，Cardiomegaly で FairREAD は AUC 0.880，Delta EO 0.113，FATE_EO 0.318 を示し，Pleural Effusion では AUC 0.901，Delta EO 0.077，Fracture では AUC 0.770，FATE_AUC 0.364 を示した．Pneumonia でも AUC 0.804，Delta EO 0.146，FATE_EO 0.237 であった．

Table 3 では threshold selection strategy を比較し，Min-gap が average Delta EO 0.129，FATE_EO 0.197 で最良だった．Youden's J は Delta EO 0.176，FATE_EO 0.055，G-Means は Delta EO 0.155，FATE_EO 0.108，default threshold 0.5 は accuracy 0.871 と高いが Delta EO 0.377，FATE_EO -0.493 と悪い．default threshold の高 accuracy は class imbalance によりほぼ negative と判定することで得られる表面的な値だと説明されている．

## Representation analysis

t-SNE visualization では，FIE 出力 `z_T` の embedding space では demographic subgroups が明確な clusters を作らず，disentanglement が demographic information を除いていることを示す．一方，re-fusion の `mu` と `sigma^2` は demographic attributes ごとに分離し，re-fusion blocks を通るにつれて demographic subgroups が再び表現に現れる．同時に target classes の分離も `z_T` より明確になるため，re-fusion mechanism が demographic information を診断に有用な形で統合していると解釈される．

## OOD testing

CheXpert で Cardiomegaly と Pleural Effusion を学習し，MIMIC-CXR を OOD test set として評価する．Pneumonia と Fracture は，MIMIC-CXR test set の subgroup sample 数が少なすぎて accuracy / AUC の信頼できる計算が難しいため除外する．

Table 4 では，Cardiomegaly OOD で FairREAD は accuracy 0.722，AUC 0.790，Delta AUC 0.113，Delta EO 0.378，FATE_EO 0.298，FATE_AUC 0.148 を示す．Pleural Effusion OOD では accuracy 0.823，AUC 0.911，Delta AUC 0.085，Delta EO 0.166，FATE_EO 0.519，FATE_AUC 0.401 を示し，baseline methods より良い performance-fairness balance を示した．

## Limitations

本論文では，age，gender，race を binary values に discretize している．これは subgroup sample size を確保するには実用的だが，subgroup 内の潜在的な unfairness を隠す可能性がある．また，Native American samples は curated CheXpert dataset 内で31 samples，test set で4 samples しかなく，accuracy，AUROC，Delta EO，Delta AUC を信頼して計算することが難しい．

著者らは，dataset resampling と subgroup-specific threshold の組み合わせ，より詳細な demographic attributes への拡張，FIE construction の改善，cross-attention など他の modality fusion methods の適用を future work として挙げている．

## 関連概念

- [[FairREAD]]
- [[Image_Tabular_Fusion]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Demographic_Imbalance]]
- [[Equalized_Odds]]
- [[Race_Recognition_In_Medical_Images]]
