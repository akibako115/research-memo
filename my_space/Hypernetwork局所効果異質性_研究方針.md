# Hypernetwork による局所効果異質性の研究方針

## 現時点の結論

研究の中心を「潜在クラスタを発見すること」から、「患者 metadata による条件付けが患者空間のどこで性能を改善・悪化させるかを監査すること」へ移す。

中心課題は次のように定義する。

> 患者 metadata による分類器の条件付けは、capacity-matched な固定・融合モデルと比較して、どの患者領域の診断性能を改善または悪化させ、その局所効果は再現可能か。

ここで扱う低性能領域は、直ちに fairness subgroup とは呼ばない。protected attribute や社会的不利益との関係が示されない限り、基本的には subgroup reliability / model auditing の対象として扱う。

## 研究上の位置づけ

Hypernetwork を公平性改善手法として前提化しない。平均性能や既知 demographic gap の改善だけでなく、同じ demographic group 内の性能ばらつき、新たに生じる局所的失敗、calibration や operating point 上の変化を調べる。

主な問いは次のとおり。

- 既知 demographic group の gap は縮小するか。
- 同じ demographic group 内の局所的な性能ばらつきは増減するか。
- 固定分類器と Hypernetwork の性能差は患者空間の特定領域に集中するか。
- その領域は split、seed、近傍定義を変えても再現するか。
- 局所効果は画像特徴、metadata の主効果、または両者の interaction のどれで説明されるか。
- Hypernetwork の予測が metadata 条件に敏感な領域と、性能が変化する領域は対応するか。

## 主要仮説

### H1: Hypernetwork の効果は患者空間で一様ではない

> Hypernetwork の患者ごとの効果は一様ではなく、画像特徴と metadata の interaction に沿って局所化する。

患者 `i` に対する paired loss difference を次のように定義する。

```text
Delta_i = Loss_Hypernetwork(i) - Loss_Baseline(i)
```

共通の患者空間における条件付き期待値 `E[Delta_i | image_i, metadata_i]` を推定し、Hypernetwork が改善する領域と悪化する領域を調べる。

単に異質性が存在するだけでは不十分であり、次を要求する。

- capacity-matched baseline より局所効果の異質性が大きい、または異質性の構造が異なる。
- 複数 seed と独立 test set で効果の方向が再現する。
- 効果が十分な症例数を持つ領域に集中する。
- 平均性能の変化だけでは説明できない。

### H2: 局所効果の一部は画像と metadata の interaction で説明される

> Hypernetwork と固定・融合モデルの性能差は、画像特徴または metadata の主効果だけでは説明できず、両者の interaction によって追加的に説明される。

`Delta_i` を目的変数として、以下の説明モデルを比較する。

1. image features のみ
2. metadata のみ
3. image features と metadata の加法モデル
4. image と metadata の interaction を含むモデル

interaction を含むモデルが独立 test set で追加的な説明力を持ち、その効果が seed や split に対して安定していることを検証する。

これは統計的 interaction であり、因果的 interaction とは主張しない。

## 副次仮説

### H3: metadata 条件への予測感度と局所性能差は関連する

> metadata conditioning に対する予測感度が高い患者領域では、固定分類器との差や calibration error も大きい。

生成された分類器 weight の距離を直接解釈するのではなく、機能的変化を優先して測定する。

- 同一画像特徴に異なる metadata 条件を与えた場合の logit 変化
- metadata に対する logit Jacobian
- metadata masking
- matched strata 内での conditional permutation
- 共通 probe set 上での生成分類器間の出力距離

これらは機序の証明ではなく、主解析で得られた局所効果を説明する補助的証拠として扱う。

## Subgroup の扱い

大域的に明確なクラスタ構造が存在することは前提にしない。患者集団が離散クラスタを形成しない場合は、連続的な局所性能解析を主とする。

低性能領域が次の条件を満たす場合に限り、監査可能な候補 subgroup として記述する。

- validation set で発見し、独立 test set で性能低下が再現する。
- membership または領域定義が seed、bootstrap、近傍サイズに対して安定している。
- 効果の方向が複数の学習 seed で一致する。
- 十分な症例数、陽性数、陰性数を持つ。
- confidence interval または permutation test により偶然変動と区別できる。
- 画像所見、撮影条件、metadata、ラベル品質などとの関係を確認できる。

クラスタリングは主目的ではなく、局所性能構造を要約・説明するための補助手段とする。

## 必要な比較モデル

ResNet50 と Hypernetwork の2モデルだけでは、metadata 利用、モデル容量、融合方式、条件付け方式の効果を分離できない。最低限、次を比較候補とする。

- image-only ResNet50
- metadata-only model
- image feature + metadata の late fusion
- capacity-matched fixed nonlinear classifier
- FC-only Hypernetwork
- metadata permutation または metadata masking を行った Hypernetwork

全モデルで画像 encoder、初期化、学習回数、データ split、model selection criterion を可能な範囲で統制する。

## FC-only Hypernetwork のアブレーション

現在のタスクは `0 = Findings`、`1 = No Findings` の2クラス分類であり、Hypernetwork はクラス0・1それぞれの分類 weight と bias を生成する。現状では、群ごとに変化の方向は異なるものの、ResNet50 から Hypernetwork への変更で `Recall 0` が上がった群では `Recall 1` が下がり、逆方向でも同じトレードオフが見られる。一方、AUROC gap の変化は小さい。

この現象が、metadata に応じた画像識別方向の変更によるものか、患者ごとの実効的な operating point の変更によるものかを分離する。

2クラスの出力 logit を `z0`、`z1` とすると、No Findings 側の判定 score は次のように表せる。

```text
score = z1 - z0
      = {w1(metadata) - w0(metadata)}^T image_feature
        + {b1(metadata) - b0(metadata)}
```

比較するアブレーションは次のとおり。

| モデル | weight | bias | 検証する作用 |
| --- | --- | --- | --- |
| Fixed classifier | 固定 | 固定 | image-only baseline |
| HyperBias | 固定 | metadata から生成 | adaptive threshold / prior adjustment |
| HyperWeight | metadata から生成 | 固定 | metadata に応じた画像識別方向の変更 |
| Full Hypernetwork | metadata から生成 | metadata から生成 | 両方の作用 |
| Late fusion | 固定分類器 + metadata logit | 固定または加算 | HyperBias に近い単純な条件付き baseline |
| Shuffled-metadata Hypernetwork | metadata から生成 | metadata から生成 | metadata と患者の対応関係が必要か |

結果は次のように解釈する。

- HyperBias が recall trade-off と gap の変化を再現する場合、主作用は metadata-dependent operating point である。
- HyperWeight が subgroup / overall AUROC を改善する場合、metadata に応じた画像識別方向の変更が寄与している。
- Full Hypernetwork が HyperBias を上回らない場合、weight 生成の追加的価値は弱い。
- Late fusion と Full Hypernetwork が同等の場合、複雑な分類器生成の必然性は弱い。
- metadata shuffle で効果が消える場合、患者と metadata の対応関係が予測変化に必要である。
- metadata shuffle 後も変化が残る場合、追加パラメータ、最適化、正則化など metadata 以外の要因を疑う。

weight / bias アブレーションでは、可能な範囲で総パラメータ数を揃える。完全に揃えられない場合は、capacity-matched fixed MLP classifier を追加して容量差を統制する。

## 評価軸

AUROC、Accuracy、recall は同じ性質を測らない。AUROC は ranking、Accuracy や recall は特定 operating point 上の判断に依存する。そのため、次を分けて評価する。

- overall / subgroup AUROC
- TPR、FPR、FNR、specificity
- subgroup calibration
- Brier score または ECE
- worst-region performance
- best-worst gap
- paired loss difference
- model 間の予測不一致率

gap の縮小だけでは leveling down を見落とすため、gap と最悪領域の絶対性能を併記する。

## Operating-point sweep

2出力 softmax でも、クラス1の確率または2つの logit の差を1次元 score として threshold sweep できる。

```text
p1 = softmax([z0, z1])[1]
d  = z1 - z0

predict No Findings if p1 >= threshold
```

`p1 >= 0.5` と `d >= 0` は等価である。threshold を動かすと、各群の `Recall 0` と `Recall 1` のトレードオフを追跡できる。

ResNet50 と各アブレーションモデルについて、次の曲線を比較する。

- overall Recall 0 対 overall Recall 1
- overall Recall 0 対 Eopp0 gap
- overall Recall 1 対 Eopp1 gap
- worst-group Recall 0 対 worst-group Recall 1
- threshold 対 Eopp0 / Eopp1 gap
- balanced accuracy 対 Eopp0 / Eopp1 gap

単一の `0.5` threshold だけでモデル間の fairness を比較しない。同一の overall Recall 0、overall Recall 1、または balanced accuracy に対応する operating point でも比較し、現在の gap 差が score scale / threshold の違いだけで説明できるかを確認する。

threshold の選択と評価は分離する。

1. validation set で threshold を sweep する。
2. 臨床的制約または事前に定めた model-selection rule に基づいて threshold を選ぶ。
3. threshold を固定する。
4. test set で overall、group-wise、worst-group metrics を評価する。

test set 上で最も公平に見える threshold を選択しない。探索的な曲線の可視化と、事前規則で選択した operating point における確認的評価を分けて報告する。

モデル間で `overall Recall 0 vs Recall 1` の曲線がほぼ重なる場合、差は主に operating point の違いと解釈する。同じ utility に揃えても fairness curve が異なる場合、モデル固有の group-wise score distribution の違いが残っていると判断する。

## 新規性の候補

主たる新規性は、新しい clustering 手法や Hypernetwork の構造そのものではない。

> 患者 metadata で条件付けられた医療画像分類モデルについて、既知 demographic group の比較とモデル非依存な局所性能解析を統合し、条件付けによる効果の異質性と hidden failure の変化を評価する。

既存領域との差分は次のように整理する。

| 既存領域 | 主な問い | 本研究で追加する問い |
| --- | --- | --- |
| demographic fairness | race、sex、age 間に性能差があるか | 既知 group 内外で条件付けの効果がどう異なるか |
| hidden stratification | 粗い疾患ラベル内に弱い subclass があるか | 条件付けによって弱い領域がどう変化するか |
| subgroup discovery | 単一モデルの systematic error slice は何か | 複数モデル間の局所的な性能差はどこに集中するか |
| hidden cohort fairness | hidden cohort を使って worst-group 性能を改善できるか | 条件付きモデル自体が cohort reliability に与える影響は何か |
| multimodal / Hypernetwork | metadata 利用で平均性能が上がるか | 改善・悪化が誰に生じ、再現可能か |

## 降格した研究案

### 生成分類器の parameter geometry

weight distance は再パラメータ化や画像表現に依存し、機能距離とは限らない。主研究にはせず、局所性能差が確認された後の補助解析とする。

### 新しいマルチビュー subgroup discovery 手法

ground-truth subgroup の欠如、feature 選択と cluster 設定の自由度、error-aware discovery の循環性、既存手法との差分の弱さがある。現段階では新手法の提案を目標にせず、既存手法を監査ツールとして使う。

### Hypernetwork を公平性改善手法として提示すること

現状では recall gap の悪化も観察されており、改善手法としての方向づけは早い。まず条件付けが性能と失敗構造へ与える影響を明らかにする。

## 査読上の主要リスク

- CheXpert 単一データセットによる一般化可能性の不足
- pathology、metric、閾値、cluster 設定に関する多重比較
- 同じデータでの subgroup 発見と性能評価
- 少数領域の偶然の低性能
- 撮影条件やラベルノイズを患者 subgroup と誤認すること
- モデル容量や学習条件の不一致
- protected metadata の利用による group-specific specialization
- reliability と fairness の概念的混同
- 相関的な解析から因果的機序を主張すること

## 現時点での優先順位

1. 比較モデルと統制条件を確定する。
2. 対象 pathology と primary metric を事前に絞る。
3. 患者単位の paired prediction / loss table を作る。
4. 共通の患者表現上で局所的な `Delta_i` を推定する。
5. validation で発見し test で確認する評価設計を確立する。
6. 局所効果が確認された後に、metadata interaction と予測感度を解析する。
7. clustering は連続的な局所解析との整合性確認に使う。

## 今後の対話で決める事項

- primary pathology と secondary pathology
- primary outcome と臨床的 operating point
- 「患者領域」を定義する共通表現
- 局所効果を推定する統計手法
- capacity-matched baseline の具体的構造
- subgroup 採択に必要な最小症例数
- validation / test split と複数 seed の設計
- fairness と reliability を分ける報告方法
- 修士研究の時間内で実施する解析範囲
