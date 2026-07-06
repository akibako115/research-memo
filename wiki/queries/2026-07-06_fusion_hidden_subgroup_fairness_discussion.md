---
created: 2026-07-06
updated: 2026-07-06
---

# Image × Tabular Fusion と Hidden Subgroup Fairness の交差領域の検討

## 背景

医療画像 fairness の全体像を理解した上で，Image × Tabular Fusion（[[FiLM]]，[[DAFT]]，[[HyperFusion]]）と Hidden Subgroup Fairness（[[Hidden_Cohort_Fairness]]，[[DOMINO]]，[[Hidden_Stratification]]）の組み合わせを研究の方向として検討した．この2領域はほぼ独立に研究されており，交差する研究はまだほとんどない．

## 前提知識の整理

### 医療画像 Fairness の評価軸

評価の3軸（平均性能・subgroup 間差・worst group）は独立した軸であり，互いに包含しない．

- worst group が改善しても subgroup 間差が広がるケース: 最悪群が 0.70→0.72 に改善しても，最良群が 0.90→0.95 に伸びれば gap は拡大する
- subgroup 間差が縮小しても全体が悪化するケース（leveling down）: 高性能群を下げて差だけ小さくする

### Fairness criterion の不可能性

DP と EO は prevalence が subgroup 間で異なる限り同時に満たせない（impossibility theorem）．

```
P(Ŷ=1 | G) = TPR × prev(G) + FPR × (1 - prev(G))
```

EO を満たす（TPR, FPR が G に依存しない）場合，陽性予測率は prevalence の一次関数になるため，prev(A) ≠ prev(B) なら DP は自動的に破れる．同様に EO と Predictive Parity も同時に満たせない場合がある．

医療画像診断では EO / EOpp + subgroup AUC gap + worst-group AUC の組み合わせが最も一般的．DP は診断より資源配分の文脈で意味がある．

### Hidden Subgroup の種類

- demographic subgroup: sex，age，race（metadata で定義）
- clinical subgroup: 疾患 subtype，severity，treatment status
- visual hidden cohort: lesion appearance，artifact，image quality
- representation cluster: embedding-based cohort（metadata なし）

severity = 同じ疾患ラベル内の重症度差（大きな虚脱 vs 微小な虚脱），artifact = 画像に写り込む疾患以外の視覚的要素（chest drain，ペースメーカー，スキャナ特性）．

## Fusion × Hidden Subgroup Fairness の設計空間

### 2つの領域の現状

Fusion 系は「性能向上」が主目的で fairness を扱っていない．Hidden subgroup fairness は「公平性」が主目的で fusion を使っていない．

### 組み合わせのアプローチ

| アプローチ | 概要 | 利点 | リスク |
|---|---|---|---|
| A: Fusion embedding で cohort 発見 | fused embedding で clustering → hidden cohort | tabular の違いを反映した cohort が見つかる | protected attribute が cohort に混入 |
| B: Cohort 発見→cohort-aware fusion | cohort label を tabular に入れて fusion | cohort ごとに画像処理を調整できる | cohort の安定性に依存 |
| C: Fairness-aware fusion | disentanglement + controlled re-fusion | shortcut 除去と性能向上を同時に扱える | 何を除去し何を残すかの判断が難しい |
| D: Fusion パラメータで監査 | 学習済み α/β を hidden cohort ごとに分析 | 追加学習なしで適用できる | α/β の解釈は容易でない |

## 設計上の本質的な難しさ

### 1. Hidden cohort の定義が fusion の入力に依存する

画像 embedding で cohort を作ると tabular の違いが反映されない．fused embedding で cohort を作ると tabular の protected attribute が cohort に混入する．

具体例: 脳 MRI で，画像上似ている2患者が CSF biomarker の有無で臨床的に異なる場合，画像 embedding では分離できないが fused embedding では分離できる．しかし fused embedding で clustering すると，CSF 検査の有無（= アクセス格差と相関）が cohort 定義に入り込む．

### 2. Tabular data の missingness が hidden subgroup を作る

医療データの欠測は MNAR（Missing Not At Random）が普通．CSF，PET，遺伝子検査の欠測は，臨床的判断，患者の選好，施設のアクセス，保険の適用と相関する．

HyperFusion が missingness indicator を入力に使うと，「検査を受けたかどうか」で画像処理の重みが変わる．検査アクセスの格差がモデル性能の格差に変換されるが，demographic fairness 指標では捉えにくい場合がある．

さらに，missingness 自体が診断ラベルと相関する shortcut になりうる（CN 患者は侵襲検査を受けないことが多い → CSF_missing が CN の proxy に）．

### 3. Worst-cohort 改善と全体性能の trade-off

Group DRO で worst cohort の loss を下げると，他の cohort の性能が下がる可能性がある．Fusion model では条件付けの自由度が高い分（特に HyperFusion），worst cohort への過適合リスクが大きい．

FiLM（channel-wise γ/β のみ）は自由度が低く過適合しにくいが改善幅も限定的．HyperFusion（layer weights/biases を生成）は自由度が高く改善幅は大きいが，少数 cohort に過適合しやすい．

### 3つの難しさの連鎖

```
cohort 定義に protected attribute が混入
→ worst cohort がアクセス格差を反映した群になる
→ その群に fusion model を特化させると過適合
→ 新しい施設で検査方針が違うと崩壊
```

## Sensitive signal と disease signal の分離問題

「因果的に有用な属性は使い，社会的格差の proxy は使わない」が理想だが，実際には:

- age は AD と因果的に関係するが，insurance_type とも相関する
- age を入れると insurance の情報が間接的に流入する
- insurance_type 列を除いても age が proxy として機能する
- tabular の個々の変数（biomarker の有無など）も protected attribute と相関しうる

制御方法は3つあるがどれも完全ではない:

| 方法 | 制御精度 | 問題 |
|---|---|---|
| 入力から除く | 低い | proxy 経由で漏れる |
| Adversarial disentanglement | 中程度 | 相関が強いと因果的情報も消える |
| Causal fairness | 理論上は高い | 因果グラフの正しさに依存，医療画像 fusion では未実装 |

現実的には「制御できていないことを認めた上で，影響を測定する」アプローチが必要．age を入れた/入れないで insurance_type ごとの性能差がどう変わるかを ablation で見る，age の残差（insurance との相関を除いた成分）を使う，などが候補．

## α/β 分析の可能性と限界

DAFT の α/β を insurance_type ごとに比較すれば，age を通じた情報漏洩を観察できる可能性がある．ただし:

- 深い層の channel は distributed representation であり，1 channel = 1 概念の対応は期待できない
- 数百〜数千 channel の feature map を個別に解釈するのは非現実的

現実的な分析階層:

| Level | 手法 | 分かること | channel の意味 |
|---|---|---|---|
| 1 | α/β 全体の群間分布検定 | 漏れの有無 | 不要 |
| 2 | partial correlation で候補 channel を絞る | 漏れの規模と場所 | 不要 |
| 3 | 候補 channel の α を固定して予測変化を測る | 漏れの影響の大きさ | 不要 |
| 4 | 少数 channel の feature map を可視化 | 漏れが有害かの判断材料 | 必要（少数のみ） |

Level 1-3 は channel の意味を知らなくてもできる統計的・介入的分析．Level 4 は Level 2 で絞り込んだ少数 channel にだけ適用する．

## 研究の優先度

α/β 分析は「原因の診断」であり，それ以前に答えるべき基本的な問いがある:

```
Q1: fusion model は hidden subgroup の性能を改善するのか？ → 未検証
Q2: hidden subgroup の定義に tabular data を使うと画像のみより良いか？ → 未比較
Q3: fusion の条件付けに protected attribute の情報がどう漏れるか？ → α/β 分析はここ
```

### 推奨する研究の道筋

**Phase 1（最優先，最小限の実験で最大の知見）:**

既存 fusion model（image-only，late concat，FiLM，DAFT，HyperFusion）を hidden subgroup metrics で評価する．DAFT/HyperFusion 論文は overall 性能しか報告していない．各モデルの embedding を clustering → cohort ごとの AUC，worst-cohort AUC，cohort gap を測定するだけで新しい知見になる．

**Phase 2（Phase 1 の結果に応じて分岐）:**

- fusion が worst cohort を悪化させた場合 → α/β 分析で原因診断（Q3）
- fusion が改善した場合 → cohort discovery の改善（Q2）
- fusion model ごとに違う場合 → 条件付けの自由度との関係を分析

**Phase 3（解決策の提案）:**

Phase 1-2 の知見に基づいて fairness-aware fusion を設計する．

| タスク | 新規性 | 影響 | 実装難度 | 優先度 |
|---|---|---|---|---|
| 既存 fusion を hidden subgroup で評価 | 高 | 高 | 低 | 最優先 |
| embedding 選択と cohort discovery の比較 | 高 | 中〜高 | 低〜中 | 高 |
| α/β の統計的群間比較 | 中 | 中 | 低 | 中（Q1 次第） |
| α/β の介入実験 | 中 | 中 | 中 | 中（Q1 次第） |
| fairness-aware fusion の設計 | 高 | 高 | 高 | Q1-Q3 の後 |

## 関連概念

- [[FiLM]]
- [[DAFT]]
- [[HyperFusion]]
- [[Image_Tabular_Fusion]]
- [[Hidden_Stratification]]
- [[Hidden_Cohort_Fairness]]
- [[DOMINO]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Medical_Image_Fairness_Audit_Loop]]
- [[FairREAD]]
- [[Worst_Group_Performance]]
- [[Equalized_Odds]]
- [[Pairwise_Fairness]]
- [[Race_Recognition_In_Medical_Images]]
- [[Demographic_Imbalance]]
- [[Fairness_Under_Distribution_Shift]]
