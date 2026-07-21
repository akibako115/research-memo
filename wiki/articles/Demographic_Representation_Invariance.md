---
created: 2026-07-21
updated: 2026-07-21
sources:
  - "[[sources/2026-07-21_demographically_invariant_models_representations_medical_imaging_fair]]"
---

# Demographic Representation Invariance

医療画像モデルが患者の age，race，sex を latent representation から高精度に推定できることが繰り返し示されてきた（[[Race_Recognition_In_Medical_Images]]）．この観察は自然に「モデルが demographic group membership を符号化**しない**よう訓練すべきではないか」という発想を招く．しかし，この要求を数式に落とすと，それが暗黙に algorithmic fairness の特定の criterion（statistical parity や separation）を強制していることが分かり，予測精度の犠牲や，むしろ患者への disparate treatment を招くという逆説的な帰結にたどり着く．Demographic representation invariance は，「group membership を符号化しない」という直感的な目標を，どのレベルで invariance を課すかによって分類し，それぞれがどの fairness criterion に対応し，何を犠牲にするかを整理する枠組みである．

## 全体像

invariance は，どの変数（latent representation `Z`，risk score `R`，二値予測 `Ŷ`）に対して，どの条件（marginal，class-conditional，counterfactual）で課すかによって3種類に分かれる．

| Invariance の種類 | 数式 | 含意される fairness criterion | 主な欠点 |
| --- | --- | --- | --- |
| marginal representation invariance | `Z ⊥ A`（`p(z) = p(z\|a) ∀a`） | statistical parity（`R, Ŷ ⊥ A`） | prevalence 差がある場合，予測精度の大きな損失．actively confounding を強制 |
| class-conditional representation invariance | `Z ⊥ A \| Y`（`p(z\|y) = p(z\|y,a) ∀a,y`） | separation（`R, Ŷ ⊥ A \| Y`，equalized error rate） | risk score レベルの separation は group-wise calibration と両立しない |
| counterfactual model invariance | `A` を変化させても他を固定すれば予測が不変 | 全経路への invariance は separation と同型（Veitch et al.）．path-specific には理論上できるが実装例なし | 医療画像で意味のある counterfactual の定義自体が困難．intra-class variation を均一化してしまう |

いずれの invariance も，group 間の **within-class variation**（疾患 subtype，重症度，撮像条件の違いなど，[[Hidden_Stratification]] と同種の問題）を無視し，本質的に異なる患者を同一の latent representation に押し込めることを要求するという共通の欠点を持つ．

```text
「モデルが group membership を符号化しない」
        │
        ├─ marginal invariance  Z⊥A      → statistical parity
        ├─ class-conditional invariance  Z⊥A|Y  → separation (risk score level)
        └─ counterfactual invariance     → separation と同型（全経路の場合）
```

## モデルと表現の区別

この枠組みで最初に押さえるべきは，**モデル**の invariance と**表現**の invariance が異なる要求だという点である．

- モデルの invariance: 「`A` の値だけを変えて他を固定したとき，予測 `ŷ` は変わらない」．`Y` と `A` が相関していても，モデルが `A` を明示的に無視すればよく，`Y` が `A` と相関している分の予測力は失われる．
- 表現の invariance: 「`Z, Ŷ ⊥ A`」．`Y` が `A` と相関する場合，これを満たすには feature extraction（encoding）段階で**能動的に交絡させる**必要がある．同じ病態の患者を group によって異なる latent representation にマッピングし，unequal treatment と不必要な誤分類を引き起こす．

representation invariance を要求することは，見かけ上「group を見ない」ように見えて，実際には「group に応じて異なる扱いをモデルの内部で強制する」ことになりうる．

## 高次元ラベルほど invariance が難しくなる

`p(y | a)` の group 間差は，`Y` が高次元になるほど識別しやすくなる．疾患ラベルが1つなら prevalence 差は小さな signal だが，multi-class や segmentation のように `Y` が高次元になると，正確な予測 `Ŷ` から `A` を推定する精度は急速に1へ近づく．つまり，**モデルが正確であるほど**，`A` の non-identifiability を保つことは事実上不可能になる．これは，invariance を要求する対象が高次元ラベルに向かうほど（例えば segmentation mask の推定），marginal / class-conditional invariance の代償が大きくなることを示す．

## Counterfactual invariance も同じ壁にぶつかる

representation matching の欠点を避けるため，domain generalization コミュニティは "invariant representation" ではなく "invariant mechanism（model）" を学習する方向へ移ってきた．その代表が counterfactual invariance で，`A` を変化させても「他をすべて固定」すれば予測が変わらないことを求める．

しかし医療画像では「他をすべて固定する」の中身が非自明である．biological sex が anatomy，lifestyle，disease presentation を経由して画像 `x` に影響する causal graph を考えると，**全経路**に対する counterfactual invariance は，疾患条件付きで異なる sex の画像表現の分布を完全に一致させることを要求し，これは class-conditional representation invariance と同じ separation を含意してしまう（Veitch et al.，Nilforoshan et al.）．**一部の経路だけ**への invariance（path-specific counterfactual fairness）は理論上可能だが，どの経路が「本質的」でどの経路が「単なる correlate」かを社会構築的な demographic group について定義すること自体が困難であり，医療画像への実装例は存在しない．

## 符号化は fairness violation か

この枠組みが導く結論は，「モデルが group membership を符号化するという事実そのものは fairness violation とは言えない」というものである．根拠は次の3点に整理できる．

| 論点 | 内容 |
| --- | --- |
| encode と use は別 | representation が group membership と相関することは，モデルがその情報を意思決定に使用していることを含意しない |
| invariance には代償がある | marginal invariance は statistical parity（多くの予測場面で望ましくない）を，class-conditional / counterfactual invariance は separation（group-wise calibration と非両立）を強制する |
| encode が有益な場合もある | group membership を明示的に使わず，予測タスクに関連する age・sex・ethnicity の側面だけを抽出する implicit representation は，粗い human-defined category に内在するバイアスを継承しにくく，non-binary や mixed-race のような境界的な患者群への一般化にも有利になりうる |

したがって，この枠組みの実務的な帰結は，「representation から group membership を除去する」ことをゴールにするのではなく，[[Medical_Image_Fairness_Evaluation]] のように，**予測の group 間 disparity**（error rate，calibration，worst-case performance）を直接測定・監査することに重心を置くべきだ，という点にある．

## 関連する fairness criterion との対応

この枠組みは，representation の性質と，[[Equalized_Odds]] のような prediction 側の fairness criterion の間の含意関係を明らかにする．

| Representation 側 | Prediction 側（含意される criterion） |
| --- | --- |
| `Z ⊥ A` | `R, Ŷ ⊥ A`（statistical parity） |
| `Z ⊥ A \| Y` | `R, Ŷ ⊥ A \| Y`（separation，risk score レベル） |
| counterfactual invariance（全経路） | `R, Ŷ ⊥ A \| Y`（separation と同型） |

[[Equalized_Odds]] が扱う TPR/FPR parity は，この表の separation（classification level，`Ŷ ⊥ A | Y`）に対応する．ただし論文は，classification level の error rate equality は，risk score レベルの class-conditional representation invariance という過度に制約的な要求なしでも達成可能である点を強調する．つまり，「representation を invariant にする」ことと「予測の error rate を揃える」ことは別の目標であり，後者だけを狙う方が calibration とのトレードオフを避けやすい．

[[Subgroup_Separability]] は，この枠組みと補完的な視点を提供する．representation invariance の議論が「invariance を課すとどんな fairness criterion が得られ，何を失うか」を扱うのに対し，subgroup separability は「そもそもモデルが group membership をどれだけ識別できるか（separability）が，training data の bias が group fairness metric にどう現れるかを左右する」ことを示す．separability が低い状況では，class-conditional invariance のような representation-level の制約を課さなくても，モデルは事実上 group を区別できない．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| marginal representation invariance | `Z ⊥ A`．statistical parity を含意する |
| class-conditional representation invariance | `Z ⊥ A \| Y`．separation（risk score レベル）を含意する |
| statistical parity | `R, Ŷ ⊥ A`．予測分布が group 間で等しいこと |
| separation | `R, Ŷ ⊥ A \| Y`．label 条件付きで予測分布が group 間で等しいこと |
| label shift | `p(y \| a)` が group 間で異なる状況．prevalence 差はその一例 |
| manifestation shift | 疾患の現れ方の分布が group 間で異なる状況 |
| counterfactual invariance | `A` を変化させても他を固定すれば予測が不変であること |
| counterfactual fairness | counterfactual invariance のうち `A` が sensitive attribute である個体レベルの fairness notion |
| path-specific counterfactual fairness | causal diagram 上の一部の経路のみに対する counterfactual invariance |
| actively confounding | representation invariance を満たすために，本来無関係な要因でモデルが判断を歪めること |

## 関連概念

- [[Equalized_Odds]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Race_Recognition_In_Medical_Images]]
- [[Hidden_Stratification]]
- [[Subgroup_Separability]]
- [[Underdiagnosis_Bias]]
