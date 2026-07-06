---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_fcro_multiple_sensitive_attributes_medical_image_classification]]"
---

# FCRO

医療画像モデルは，race，sex，age など複数の sensitive attributes を同時に持つ患者を扱う．単一属性だけで fairness を評価・制御しても，複数属性の組み合わせで起こる disparity は残る．FCRO は，target representation と multi-sensitive representation を orthogonal にすることで，複数 sensitive attributes に対する fair representation を学習する手法である．

FCRO の重要な点は，複数 attributes を別々に消すのではなく，single compact sensitive representation にまとめ，その representation と target representation の関係を column / row space の両方で弱めることである．これにより，attribute 数が増えても representation space を過度に圧迫しにくい．

## 何を分離するか

FCRO は2つの representation を分ける．

| Representation | 役割 |
| --- | --- |
| target representation `z_T` | disease diagnosis など target task に使う |
| sensitive representation `z_A` | race，sex，age など sensitive attributes を予測する |

理想的には，target prediction は sensitive attributes に依存せず，label を条件に prediction と sensitive attributes が independent になる．これは [[Equalized_Odds]] の考え方とつながる．

## Column space orthogonality

column space orthogonality は，target representation が sensitive space に射影されないようにする．FCRO は sensitive representation に SVD を適用し，重要な `k` 個の basis から low-rank sensitive space を作る．target representation はその complement に置かれるように penalize される．

```text
sensitive representation Z_A
  -> SVD
  -> low-rank sensitive space S_A

target representation Z_T
  -> penalize projection onto S_A
```

low-rank にする理由は，sensitive space を大きくしすぎると target representation が使える空間が狭くなり，utility が落ちるからである．

## Row space orthogonality

row space orthogonality は，feature dimension 間の covariance を小さくする．target feature と sensitive feature が sample axis 上で共変動していると，target representation が sensitive information を保持している可能性がある．

FCRO は，target / sensitive representation の row-wise mean を引いたうえで covariance loss を計算し，sensitive-encoded covariances を抑える．column space が「どの subspace を使うか」を制御するのに対し，row space は「feature dimensions がどれだけ一緒に動くか」を制御する．

## Multi-sensitive attributes での利点

複数 sensitive attributes を扱うとき，attribute ごとに別々の adversary や constraint を置くと，gradient conflict や interference が起こりやすい．また intersectional subgroup を直接扱うと sample size が急速に小さくなる．

FCRO は，複数 attributes を `z_A` にまとめることで，次の利点を持つ．

| 問題 | FCRO の対応 |
| --- | --- |
| attribute ごとの constraint が増える | compact sensitive representation にまとめる |
| target space が圧迫される | low-rank sensitive space の complement を使う |
| feature covariance に sensitive signal が残る | row space orthogonality で抑える |
| joint subgroup disparity | Race x Sex x Age の joint Delta ED / Delta AUC で評価する |

## FairREAD との関係

[[FairREAD]] は，FCRO に近い orthogonality と adversarial training を使って fair image encoder を作るが，その後に demographic attributes を re-fusion する．つまり FCRO は「sensitive information を target representation から分離する」手法であり，FairREAD は「分離したあと，明示属性として controlled に使い直す」手法である．

```text
FCRO:
  image -> target representation orthogonal to sensitive representation -> prediction

FairREAD:
  image -> fair image representation -> demographic re-fusion -> prediction
```

この違いは，protected attributes を使わない model を目指すのか，protected attributes を制御された臨床 context として使うのか，という設計判断につながる．

## 評価で見るべき点

FCRO は AUC と subgroup disparity を同時に見る必要がある．CheXpert の Pleural Effusion では，ERM が AUC 0.863，Joint Delta ED 0.224 だったのに対し，FCRO は AUC 0.858，Joint Delta ED 0.107 だった．utility drop を小さく抑えながら joint disparity を下げたことが主張である．

| 指標 | 意味 |
| --- | --- |
| AUC | diagnostic utility |
| Delta AUC | subgroup 間の AUC disparity |
| Delta ED | Equalized Difference / Equalized Odds disparity |
| joint disparity | multiple sensitive attributes の conjunction subgroup で測る disparity |
| individual disparity | Race，Sex，Age それぞれで測る disparity |

## リファレンス

| 用語 | 意味 |
| --- | --- |
| FCRO | Fairness via Column-Row space Orthogonality |
| column space orthogonality | target representation の sensitive space への projection を抑える |
| row space orthogonality | target / sensitive features の covariance を抑える |
| low-rank sensitive space | SVD で作る compact sensitive representation subspace |
| joint disparity | 複数 sensitive attributes の組み合わせ subgroup 上の disparity |

## 関連概念

- [[Equalized_Odds]]
- [[FairREAD]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Demographic_Imbalance]]
- [[Race_Recognition_In_Medical_Images]]
