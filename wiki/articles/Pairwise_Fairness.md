---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_improving_model_fairness_image_based_cad]]"
---

# Pairwise Fairness

Pairwise Fairness は，subgroup 内の positive sample が dataset 全体の negative sample より高い risk score を与えられる確率を測る fairness criterion である．医療画像では，モデルの score が triage，screening，chronic disease prevention の decision aid として使われるため，fixed threshold の TPR/FPR だけでなく，ranking の公平性を見る価値がある．

この概念が重要なのは，臨床では「陽性か陰性か」だけでなく，どの患者をより高リスクとして扱うかが resource allocation に直結するからである．同じ AUC や sensitivity でも，ある subgroup の positive cases が全体の negative cases より低く rank されるなら，その subgroup は診断・優先順位付けで不利になる．

## 何を測るか

Pairwise Fairness は，ある subgroup `Gi` の positive examples と dataset 全体の negative examples のペアを考え，positive の score が negative の score を上回る確率として定義される．

```text
Pairwise Fairness:
  P( f(x_positive in subgroup) > f(x_negative in dataset) )
```

Pairwise Fairness Difference (PFD) は，subgroups の Pairwise Fairness の最大値と最小値の差である．

| 指標 | 意味 |
| --- | --- |
| Pairwise Fairness | subgroup positive が全体 negative より高く rank される確率 |
| PFD | subgroup 間の Pairwise Fairness gap |
| lower PFD | ranking fairness disparity が小さい |
| higher Pairwise Fairness | その subgroup の positive cases が見逃されにくい |

PFD は threshold を必要としないため，classification threshold が未確定の model development / validation 段階でも使える．

## Equalized Odds との違い

[[Equalized_Odds]] は fixed threshold における TPR と FPR の parity を見る．一方，Pairwise Fairness は score ranking を見る．

| Criterion | 見るもの | 向いている場面 |
| --- | --- | --- |
| Equalized Odds | fixed threshold の TPR / FPR | 明確な operating point がある診断 |
| Equal Opportunity | fixed threshold の TPR | underdiagnosis を減らしたい screening |
| Pairwise Fairness | positive-negative pair の ranking | risk score による triage / prioritization |
| subgroup AUC | subgroup 内 ranking | subgroup ごとの discrimination |

Pairwise Fairness は AUC と近い考え方だが，subgroup positive と dataset-wide negative の ranking を比較するため，subgroup の positive cases が全体の中でどれだけ適切に優先されるかを測る．

## Marginal ranking loss

Lin et al. は，Pairwise Fairness を改善するため，batch ごとに最も Pairwise Fairness が低い subgroup を選び，その subgroup の positive sample が negative sample より margin 以上高く score されるように学習する．

```text
loss = mean max(0, -score_positive + score_negative + margin)
```

この loss は，ranking order が誤っている sample に直接勾配をかける．また，最も低い group fairness を持つ subgroup を batch ごとに選ぶため，average performance ではなく worst subgroup の Pairwise Fairness を押し上げる方向に働く．

## 医療画像 CAD での結果

Lin et al. は，COVID-19 detection，thorax abnormality detection，POAG detection，Late AMD detection の4タスクで，binary cross-entropy baseline と marginal ranking loss を比較した．

| Task | Dataset | 評価 subgroup |
| --- | --- | --- |
| COVID-19 | MIDRC | age，sex，race，age-race |
| thorax abnormality | MIMIC-CXR | age，sex，race，age-sex |
| POAG | OHTS | age，sex，race，age-sex |
| Late AMD | AREDS | age，sex，CFH，ARMS2，age-CFH |

提案手法は，15ケースで PFD を下げ，12ケースでは PFD relative change が35%以上低下した．AUC の relative change は多くの場合1%以内だった．これは，ranking fairness を直接最適化すれば，AUC を大きく犠牲にせず subgroup disparity を下げられる可能性を示す．

## 使いどころ

Pairwise Fairness は，threshold-independent な fairness metric として，[[Medical_Image_Fairness_Evaluation]] の指標セットに追加できる．特に次の場面で有用である．

| 場面 | 理由 |
| --- | --- |
| triage | score ordering が読影順や優先順位に関係する |
| chronic disease risk | high-risk patients を上位に rank する必要がある |
| threshold 未定の validation | operating point を固定せず fairness を見られる |
| intersectional subgroup | small subgroup でも ranking gap を測れる |

ただし，Pairwise Fairness は calibration を直接見ない．risk score の絶対値を患者説明や治療判断に使う場合は，subgroup calibration も別途評価する必要がある．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| Pairwise Fairness | subgroup positive が dataset negative より高く rank される確率 |
| PFD | Pairwise Fairness の subgroup 間最大差 |
| marginal ranking loss | positive score が negative score より margin 以上高くなるようにする loss |
| threshold-invariant | fixed threshold に依存しない性質 |
| ranking fairness | score ordering が subgroup 間で偏らないこと |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Equalized_Odds]]
- [[Worst_Group_Performance]]
- [[Demographic_Imbalance]]
