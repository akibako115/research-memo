---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization]]"
---

# Fairness Under Distribution Shift

Fairness under distribution shift は，in-distribution validation で公平に見える医療画像モデルが，別施設・別地域・別 population で同じ subgroup fairness を保てるかを扱う概念である．医療 AI では，overall AUC は ID から OOD へ比較的よく相関しても，fairness gap は一貫して転移しないことがある．

この概念が重要なのは，clinical deployment はほぼ常に distribution shift を含むからである．ある施設で underdiagnosis gap を消した model が，別施設では特定 subgroup により大きく悪化するなら，ID fairness は deployment safety の証明にならない．

## ID fairness と OOD fairness は別物

ID fairness は，training / validation と同じ dataset distribution で subgroup gap が小さいかを見る．OOD fairness は，別 dataset，別施設，別国，別撮像 protocol，別 population に出したとき，subgroup gap が保たれるかを見る．

| 評価 | 見ること | リスク |
| --- | --- | --- |
| ID performance | 同一 distribution の AUC | OOD に移るとは限らない |
| ID fairness | 同一 distribution の FPR/FNR gap | OOD fairness を保証しない |
| OOD performance | 外部 dataset の AUC | subgroup 別の悪化を隠す |
| OOD fairness | 外部 dataset の subgroup gap | deployment safety に直結する |

Yang et al. は，ID と OOD の overall AUROC は高く相関する一方で，ID fairness と OOD fairness の相関は不安定だと示した．`Pneumothorax` / sex-race のように，ID fairness と OOD fairness が負に相関する設定もある．

## Demographic shortcut

medical image model は，disease classification のための representation に age，race，sex，intersectional attribute を encode しうる．この demographic encoding は，必ずしも fairness violation を意味しないが，強い encoding は FPR/FNR gap と相関しやすい．

```text
image representation
  -> demographic attribute を予測できる
  -> disease prediction が demographic shortcut に依存する可能性
  -> subgroup FPR/FNR gap が大きくなる
```

Yang et al. は，attribute prediction AUROC と fairness gap の相関を複数 task で確認した．例として，`No Finding` / age で R=0.82，`Cardiomegaly` / age で R=0.81，`Effusion` / race で R=0.71 だった．これは [[Race_Recognition_In_Medical_Images]] の問題が，deployment fairness にも接続することを示す．

## Local optimality

ID setting では，ReSample，GroupDRO，DANN，CDANN などの shortcut mitigation / robustness methods が fairness gap を下げ，AUC を大きく落とさない model を作れる．performance-fairness Pareto front 上の model は，その training distribution では locally optimal と言える．

しかし local optimality は，他の metric や OOD setting で崩れる．fairness gap を下げると ECE gap，average precision，F1 score が悪化する場合があり，ID Pareto front 上の model が OOD Pareto front に残る保証もない．

## OOD fairness gap の分解

OOD fairness gap は，ID fairness gap だけでなく，各 subgroup が distribution shift でどれだけ別々に悪化するかで決まる．

```text
OOD fairness gap
  = ID fairness gap
  + subgroup A の performance change
  - subgroup B の performance change
```

たとえば CheXpert で `No Finding` を学習し MIMIC-CXR に移した model では，ID の sex FPR gap はほぼ0だったが，OOD では female patients の FPR increase が male patients より大きく，female underdiagnosis gap が生じた．これは，fairness degradation の主因が「ID で不公平だったから」ではなく，「shift が subgroup に不均一に効いたから」である可能性を示す．

## Model selection

OOD data が事前にない deployment では，ID data だけで model を選ばなければならない．Yang et al. は，ID fairness gap を最小化する model より，ID representation に demographic information を少なく encode する model を選ぶ方が，OOD fairness で良いことを示した．

| Selection criterion | OOD fairness への示唆 |
| --- | --- |
| minimum ID fairness gap | OOD で最適とは限らない |
| maximum ID AUROC | fairness を見落とす |
| maximum worst-attribute AUROC | performance 寄りの基準 |
| minimum attribute prediction accuracy / AUROC | OOD fairness に有利だった |
| minimum calibration gap | fairness とは別 trade-off |

algorithm 別では，DANN のように embedding から demographic encoding を減らす method が，OOD fairness で良い傾向を示した．これは，globally optimal model selection では，ID fairness outcome だけでなく representation-level demographic encoding を監査する必要があることを意味する．

## 実務での評価手順

deployment 前後の fairness 評価では，次を分けて記録する．

| Step | 内容 |
| --- | --- |
| ID subgroup audit | validation set で FPR/FNR gap，AUC gap，calibration gap を測る |
| encoding audit | frozen representation から sensitive attributes が予測できるかを見る |
| external validation | 複数施設・国・dataset で subgroup gap を測る |
| shift decomposition | subgroup ごとの performance change を分解する |
| model selection | ID fairness gap だけでなく demographic encoding も使う |
| post-deployment monitoring | per-group performance と clinical outcome を継続監視する |

単一の「fair model」を作って終わりにするのではなく，運用 population が変わるたびに fairness を再評価する必要がある．

## Caveat: demographic signal は常に悪ではない

demographic variables は，疾患に直接または間接的に関係することがある．たとえば sex が breast cancer risk に関係する場合，demographic information を完全に除去することは望ましくない．問題は demographic reliance の有無だけではなく，model の reliance が真の causal effect や clinical use に合っているかである．

したがって，fairness under distribution shift では，単に protected attribute encoding をゼロにするのではなく，臨床的に正当な signal と shortcut を分ける必要がある．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| ID fairness | training / validation distribution 内での subgroup fairness |
| OOD fairness | 外部 distribution / deployment setting での subgroup fairness |
| demographic shortcut | model が disease prediction に demographic signal を heuristic に使うこと |
| locally optimal model | ID Pareto front 上で performance-fairness trade-off が良い model |
| globally optimal model | OOD setting でも performance と fairness を保つ model |
| attribute prediction AUROC | representation に sensitive information がどれだけ含まれるかの proxy |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Race_Recognition_In_Medical_Images]]
- [[Foundation_Model_Fairness]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Subgroup_Performance_Monitoring]]
- [[Equalized_Odds]]
