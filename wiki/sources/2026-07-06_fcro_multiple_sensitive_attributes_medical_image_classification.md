---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_fcro_multiple_sensitive_attributes_medical_image_classification.pdf"
---

# On Fairness of Medical Image Classification with Multiple Sensitive Attributes via Learning Orthogonal Representations

この論文は，医療画像分類において複数の sensitive demographic attributes を同時に扱う fairness representation learning 手法 FCRO (Fairness via Column-Row space Orthogonality) を提案する．既存研究の多くは単一 sensitive attribute に対する公平性を扱うが，実臨床では race，sex，age など複数属性の組み合わせが discrimination を悪化させうる．

FCRO は，target representation と multi-sensitive representation の independence を，finite vector space における orthogonality として緩和する．具体的には，column space orthogonality により target information を low-rank sensitive space の complement に置き，row space orthogonality により target / sensitive representations の feature dimensions 間 covariance を抑える．CheXpert の Pleural Effusion classification で，joint と individual の両方の fairness-utility trade-off を改善したと報告している．

## 問題設定

binary classification で，入力 `x`，label `y`，複数 sensitive attributes `a = (a_1, ..., a_m)` を考える．sensitive attributes は binary attributes の Cartesian product から来る vector として扱われる．classification model は target encoder `phi_T` と classifier `h_T` からなり，sensitive attribute model は sensitive encoder `phi_A` と各 attribute classifier `h_Ai` からなる．

論文では group fairness の criterion として Equalized Difference / Equalized Odds (ED) を扱う．multiple sensitive attributes に関する ED は，属性組み合わせ `pi_1` と `pi_2` の間で，真の label `Y=y` を条件に prediction probability が等しいこととして書かれる．

```text
P(Y_hat = y | A = pi_1, Y = y)
  =
P(Y_hat = y | A = pi_2, Y = y)
```

これは，prediction `Y_hat` と sensitive attributes `A` が，label `Y` を条件に independent であることに対応する．

## Fair representation

target embedding `z_T` と multi-attribute embedding `z_A` を導入し，`z_T` は disease diagnosis など target task 用の fair representation とみなす．複数 sensitive attributes それぞれに対して `z_T` を独立にするのは難しいため，FCRO は複数 attributes を single compact encoding `z_A` にまとめる．

この compact sensitive representation は，属性分類には十分 predictive でありつつ，target representation `z_T` とは orthogonal になるように訓練される．

## Column space orthogonality

column space orthogonality の目的は，target representation `Z_T` が sensitive space `S_A` への projection を小さくし，同時に target prediction ability を保つことである．

FCRO は sensitive representation `Z_A` に SVD を適用し，重要な `k` 個の left singular vectors から low-rank sensitive space `S_A` を作る．そのうえで，target representation が `S_A` の complement に入るように，`Z_T` の `S_A` への projection を penalize する．

この low-rank sensitive space は，複数 sensitive attributes を同じ `Z_A` で共有するため，sensitive attribute の数に agnostic である．また，low-rank にすることで target representation が使える complement space の自由度を保ち，utility loss を抑える．

## Row space orthogonality

row space orthogonality は，target representation `Z_T` と sensitive representation `Z_A` の feature dimensions 間の covariance を小さくする．column space と異なり，row vectors は sample index で alignment されているため，target feature dimension と sensitive feature dimension の inner product / covariance を直接 penalize できる．

論文では，target / sensitive representation から row-wise mean vector を引き，feature dimensions 間の covariance loss として row orthogonal loss を定義している．この loss は，sensitive-encoded covariances を抑えることで unfairness の原因になる representation coupling を弱める．

## Training

training は sensitive branch と target branch を分ける．shared encoder を使うと sensitive-related features が target classification に使われる risk があるため，FCRO は複数 sensitive attributes 用の separate sensitive branch を事前学習する．

target branch は classification objective `L_T` に column / row orthogonality losses を加えて学習する．

```text
L_targ = L_T + lambda_c * L_corth + lambda_r * L_rorth
```

`lambda_c` と `lambda_r` は fairness と utility の balance を制御する hyperparameters である．

## Dataset and setup

CheXpert dataset を用い，chest X-rays から Pleural Effusion を予測する．subgroups は self-reported race and ethnicity，sex，age の3つの binarized sensitive attributes に基づく．

original dataset では positive rate gap が比較的小さいため，bias mitigation の効果を示す目的で data bias を増幅している．まず multiple sensitive labels の conjunction で group を分け，各 subgroup の positive rate を計算し，patients を sampling out して positive rate gap を 0.12 に増やす．

Table 1 では，Pleural Effusion の original dataset は 127,130 samples，White/Non-white positive rate 0.410/0.393/gap 0.017，Male/Female 0.405/0.408/gap 0.003，>60/<=60 0.440/0.359/gap 0.081 と報告されている．augmented dataset は 88,215 samples，Race gap 0.122，Sex gap 0.125，Age gap 0.122 である．

images は 224 x 224 に resize し，15% test set と 85% 5-fold cross-validation set に分ける．backbone は DenseNet-121 で，final layer を 128-dimensional representations を抽出する linear layer に置き換える．optimizer は Adam，learning rate 1e-4，weight decay 4e-4，40 epochs，batch size 128 である．FCRO では `lambda_c=80`，`lambda_r=500`，`k=3` を用いる．

## Baselines and metrics

baselines は ERM，G-DRO，JTT，Adv，BR-Net，PARADE，Orth である．G-DRO と JTT は multi-sensitive attribute conjunction による subgroups で拡張され，Adv，BR-Net，PARADE，Orth は single sensitive attribute 用の fair representation learning を multiple attributes に拡張して比較される．

utility metric は AUC である．fairness は `Delta ED` と `Delta AUC` で評価する．joint disparities は複数 sensitive attributes の組み合わせ subgroups 上で計算し，individual disparities は Race，Sex，Age それぞれの binary attribute 上で計算する．

## 結果

Table 2 では，ERM の AUC は0.863，Joint Delta AUC は0.119，Joint Delta ED は0.224 だった．FCRO は AUC 0.858 と小さい utility drop に留めながら，Joint Delta AUC 0.057，Joint Delta ED 0.107 を達成した．

individual attributes でも，FCRO は Race Delta AUC 0.012 / Delta ED 0.033，Sex Delta AUC 0.015 / Delta ED 0.024，Age Delta AUC 0.013 / Delta ED 0.019 を示した．これは他の baselines と比べて，joint と individual の両面で良い fairness-utility trade-off である．

著者らは，medical applications は classification thresholds に敏感であるとして，race，sex，age の conjunction subgroups に対する calibration curves も示す．ERM は subgroup 間の biased calibration を示すが，FCRO はより調和した deviation と trustworthy classification を示したと述べている．

class activation map では，ERM が lung region 外，たとえば breast など sensitive evidence を見に行く傾向がある一方，FCRO は Pleural Effusion classification に関係する pathology-related part に注目すると報告されている．

## Ablation

`lambda_c` と `lambda_r` を増やすと AUC はわずかに低下するが，fairness gains が得られる．column orthogonality または row orthogonality のどちらかを外すと，joint Delta ED がそれぞれ2.4% と1.8% 低下するため，両方が重要な component である．

training with different sensitive attributes の ablation では，単一 sensitive attribute でも ERM より改善するが，FCRO は discriminated attributes の union，たとえば Sex x Age で訓練した場合により大きな benefit を示す．

rank `k` については，lower rank が convergence と accuracy に有利であり，`k=3` で sensitive information の95%以上を捉え，それ以上増やしても fairness benefit は大きく増えないと報告されている．

## 結論

FCRO は，複数 sensitive attributes を持つ医療画像分類に対し，target representation と sensitive representation の orthogonality を学習する fair representation learning 手法である．CheXpert の chest X-ray 実験で，joint / individual の両方で fairness-utility trade-off を改善し，multiple sensitive attributes に対して安定して機能することを示した．future work として，より多くの sensitive attributes に対する scalability の検証が挙げられている．

## 関連概念

- [[FCRO]]
- [[Equalized_Odds]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Demographic_Imbalance]]
- [[FairREAD]]
- [[Race_Recognition_In_Medical_Images]]
