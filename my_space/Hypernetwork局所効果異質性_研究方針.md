# Metadata 利用を理解・制御する条件付き医療画像分類の研究方針

## 研究全体の最終目標

本研究の最終目標は、患者 metadata を利用する条件付き医療画像分類モデルについて、metadata が予測に作用する機序を理解し、その使い方を明示的に制御できる新しいモデルを提案することである。

中心的な研究問いを次のように置く。

> 医療画像分類において、患者 metadata が予測に与える作用を prior、画像解釈との interaction、decision policy に分離し、それぞれの利用を制御することで、平均性能、calibration、subgroup reliability の望ましいトレードオフを実現できるか。

条件付きモデルの解析と新モデルの提案は、独立した研究として扱わない。既存モデルの挙動を解析して失敗機序を特定し、その機序を直接制御できる構造を設計し、構造への介入によって解釈が正しいかを検証する一連の研究として扱う。

目指す貢献は次の3点である。

1. 条件付きモデルが患者 metadata をどのような機能として利用しているかについての一般的知見
2. metadata の作用を機能的に分離し、モデル間で比較するための解析方法
3. metadata の用途と利用強度を明示的に制御できる条件付き分類モデル

### Metadata 利用の機能的分解

現時点では、条件付き score を概念的に次のように分解する。

```text
score(x, m; alpha, beta)
  = image_evidence(x)
  + alpha * metadata_prior(m)
  + beta  * image_metadata_interaction(x, m)
```

- `image_evidence(x)`: metadata に依存せず画像から得られる診断的 evidence
- `metadata_prior(m)`: metadata から推定されるラベル prevalence / prior odds
- `image_metadata_interaction(x, m)`: 同じ画像特徴の意味が metadata によって変化する成分
- `alpha`, `beta`: metadata の各用途を制御する係数

想定する基本的な介入は次のとおり。

| 設定 | 解釈 |
| --- | --- |
| `alpha = 0, beta = 0` | image-only prediction |
| `alpha = 1, beta = 0` | metadata を prior としてのみ利用 |
| `alpha = 0, beta = 1` | metadata prevalence を直接使わず、画像との interaction のみ利用 |
| `alpha = 1, beta = 1` | full conditional prediction |

この分解は現時点では研究仮説であり、そのままでは各成分が統計的に一意に同定できるとは限らない。prior head の学習目標、interaction の centering / orthogonality、学習時の介入、反実仮想的 metadata 置換などを用いて、各成分に操作可能な意味を与える必要がある。

また、metadata による score shift を一律に有害な shortcut とはみなさない。群間でラベル prevalence が異なる場合、calibrated posterior の推定に metadata prior が有用な可能性がある。一方、その posterior に共通 threshold を適用すると群ごとの Recall 0 / Recall 1 が変化し得る。そのため、次の段階を区別して解析する。

```text
画像から得られる evidence
        ↓
metadata による prior / interaction
        ↓
予測確率
        ↓
threshold と臨床コストに基づく decision policy
```

目標は metadata の利用を禁止することではなく、どの情報を何の目的で利用しているかを可視化し、目的に応じて選択・制御可能にすることである。

## 現時点の結論

現在進めている局所効果解析は、研究全体の最終成果ではなく、既存の Hypernetwork が metadata をどのように利用しているかを特定する第1段階と位置づける。

第1段階の中心課題は次のように定義する。

> 患者 metadata による分類器の条件付けは、capacity-matched な固定・融合モデルと比較して、どの患者領域の診断性能を改善または悪化させ、その局所効果は再現可能か。

ここで扱う低性能領域は、直ちに fairness subgroup とは呼ばない。protected attribute や社会的不利益との関係が示されない限り、基本的には subgroup reliability / model auditing の対象として扱う。

この監査を通じて、観察された変化が主に metadata-dependent prior / operating point によるものか、画像と metadata の有益な interaction によるものかを識別する。その結果を、分離・制御可能なモデルの設計要件へ接続する。

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

## FC-only Hypernetwork における weight/bias 分離実験

現在のタスクは、胸部 X 線を「0 = 所見あり（Findings）」「1 = 所見なし（No Findings）」の2クラスに分類するものである。ここで使っている Hypernetwork は、患者の metadata（性別・年齢などの属性）を受け取り、最終分類層の重み（weight）とバイアス（bias）を、クラス0・クラス1それぞれについて生成する。

現状の観察: metadata を使わない ResNet50（baseline）からこの Hypernetwork に切り替えると、患者群によって方向は異なるものの、「`Recall 0`（所見なし患者を正しく所見なしと判定する率）が上がる群では `Recall 1`（所見あり患者を正しく所見ありと判定する率）が下がる」というトレードオフが一貫して見られる。一方で、`AUROC`（閾値に依存しない、患者を正しくランキングできているかを表す指標）の群間の差はほとんど変化していない。

この現象には、少なくとも2つの異なる原因が考えられ、どちらが実際に起きているかを切り分けたい。

1. **画像の見方が変わった**: metadata に応じて、モデルが画像のどの特徴を「疾患の証拠」とみなすかという判断基準そのものが変わった。
2. **判定の基準点だけが動いた**: 画像の見方自体は変わっておらず、metadata に応じて「陽性と判定するための基準点（閾値）」だけが動いた。

### 数式で見る weight と bias の役割の違い

2クラス分類の出力ロジットを、所見あり側を `z0`、所見なし側を `z1` とすると、「所見なし」と判定するためのスコアは次のように分解できる。

```text
score = z1 - z0
      = {w1(metadata) - w0(metadata)}^T image_feature
        + {b1(metadata) - b0(metadata)}
```

この式は性質の異なる2つの項からできている。

- `{w1(metadata) - w0(metadata)}^T image_feature`: image_feature ベクトルの「どの向き」を陽性の証拠とみなすかを決める項。metadata に応じてこの重みベクトルが変われば、同じ画像特徴でも metadata によって解釈のされ方が変わることになる。
- `{b1(metadata) - b0(metadata)}`: image_feature に一切依存しない定数項。metadata に応じてこの値だけが変われば、画像の解釈自体は変えずに「陽性と判定するための基準点」だけが動くことになる。

つまり、weight だけを metadata から生成すれば「画像の見方の変化」を、bias だけを metadata から生成すれば「判定基準点の変化」を、それぞれ単独で切り出して検証できる。

### 比較するモデル一覧

| モデル名 | weight（画像特徴への重み） | bias（判定の基準点） | このモデルで確かめたいこと |
| --- | --- | --- | --- |
| Fixed classifier | metadata を使わず固定 | metadata を使わず固定 | metadata を一切使わない場合の baseline（画像のみのモデル） |
| HyperBias | 固定（metadata を使わない） | metadata から生成 | metadata によって「判定の基準点」だけが調整されているか（有病率の違いなどを反映した閾値・事前確率の調整に近い作用） |
| HyperWeight | metadata から生成 | 固定（metadata を使わない） | metadata によって「画像のどこを疾患の証拠とみなすか」という判断基準自体が変わっているか |
| Full Hypernetwork | metadata から生成 | metadata から生成 | 上記2つの作用が両方とも起きている、現在実際に使っているモデル |
| Late fusion | 固定分類器の出力に metadata 由来の項を足し込む | 固定または加算 | HyperBias に近い、より単純な条件付け baseline |
| Shuffled-metadata Hypernetwork | metadata から生成（ただし患者と metadata の対応をわざとシャッフルする） | metadata から生成（同上） | 観察される効果が生じるために、「その患者本人の」metadata である必要があるか |

### 結果の解釈方針

- **HyperBias だけで、現状観察している `Recall 0`/`Recall 1` のトレードオフや群間の性能差が再現される場合**: 主な作用は「metadata に応じた判定基準点の調整」であり、画像の見方自体は変わっていないと考えられる。
- **HyperWeight で、患者群ごとまたは全体の `AUROC`（ランキング性能）に改善が見られる場合**: 「metadata に応じて画像のどこを疾患の証拠とみなすかが変わる」効果が実際に寄与していると考えられる。
- **Full Hypernetwork が HyperBias 単体を上回らない場合**: weight を metadata から生成することの追加的な価値は乏しいと考えられる。
- **Late fusion と Full Hypernetwork が同程度の性能の場合**: Hypernetwork のような複雑な重み生成を使う必然性は弱いと考えられる。
- **metadata をシャッフルすると効果が消える場合**: 観察された効果には、患者本人の metadata と画像の対応関係が必要であることを意味する。
- **metadata をシャッフルしても効果が残る場合**: 効果の原因は metadata そのものではなく、パラメータ数の増加・最適化の違い・正則化の違いなど、metadata 以外の要因である可能性を疑う。

weight/bias のアブレーション同士を比較する際は、可能な限りモデル全体のパラメータ数を揃える。完全に揃えられない場合は、metadata を使わず固定重みを持つ MLP 分類器（容量だけを Hypernetwork に合わせたもの）を追加の比較対象にし、パラメータ数の違いによる影響を切り分ける。

## 評価に使う指標

`AUROC`、`Accuracy`、`Recall` は、それぞれ違う性質を測っている。`AUROC` は「陽性・陰性を分ける閾値を決める前の、患者の並べ方（ランキング）」の良さを測る指標であり、`Accuracy` や `Recall` は「ある特定の閾値を選んだ後の、実際の判定」の良さを測る指標である。この2種類を区別せずに議論すると、「閾値の選び方の違い」による差なのか、「ランキング自体の質の違い」による差なのかが分からなくなる。そのため、評価では次を分けて記録する。

- 全体および患者群ごとの `AUROC`
- `TPR`（真陽性率）、`FPR`（偽陽性率）、`FNR`（偽陰性率）、`specificity`（特異度）
- 患者群ごとの calibration（予測確率がどれだけ実際の陽性率と一致しているか）
- `Brier score` または `ECE`（Expected Calibration Error）: どちらも予測確率の信頼性を数値化する指標
- 最も性能が低い患者群（worst-region）の絶対性能
- 最も性能が良い群と悪い群の性能差（best-worst gap）
- 同じ患者に対する2モデル間の損失の差（paired loss difference）
- 2モデル間で予測結果が食い違う患者の割合

患者群間の性能差（gap）が縮まっただけでは、「全体の性能が下がったことで見かけ上差が縮まっただけ」（leveling down、公平性改善に見えて実際は両群とも悪化している状態）という可能性を見落とす。そのため、gap の大きさと、最も性能が低い群の絶対的な性能を必ず併記する。

## 閾値を動かしながら比較する（operating-point sweep）

2クラス分類の出力（softmax確率）は1次元の score として扱い、その score に対する閾値を少しずつ動かしながら（sweep しながら）評価できる。

```text
p1 = softmax([z0, z1])[1]   # 「所見なし」と判定される確率
d  = z1 - z0                 # 2つのロジットの差

predict No Findings if p1 >= threshold
```

`p1 >= 0.5` という条件と `d >= 0` という条件は数学的に同じ意味になる。この閾値を動かしていくことで、各患者群で `Recall 0` と `Recall 1` がどうトレードオフするかを追跡できる。

ResNet50（baseline）と各アブレーションモデルについて、次の関係を曲線として比較する。

- 全体の `Recall 0` と全体の `Recall 1` の関係
- 全体の `Recall 0` と、`Eopp0 gap`（Equal Opportunity 0 の群間差。「所見なし」判定における患者群間の不公平さ）の関係
- 全体の `Recall 1` と、`Eopp1 gap`（「所見あり」判定における患者群間の不公平さ）の関係
- 最も性能が低い患者群での `Recall 0` と `Recall 1` の関係
- 閾値の位置と `Eopp0`/`Eopp1` gap の関係
- balanced accuracy（患者群ごとの recall の平均など、群サイズの偏りを補正した正解率）と `Eopp0`/`Eopp1` gap の関係

単一の `0.5` という閾値だけでモデル間の公平性を比較すると、「閾値の選び方の違い」による見かけ上の差を「モデル自体の性質の違い」と誤解する恐れがある。そのため、全体の `Recall 0`、全体の `Recall 1`、または balanced accuracy が同じ水準になる閾値同士でも比較し、現在観察している群間の差が、単に score の目盛りや閾値の違いだけで説明できてしまうものなのかを確認する。

閾値の選び方と、その閾値での評価は、次のように手順を分けて行う。

1. validation set 上で、閾値を細かく動かしながら性能の変化を確認する。
2. 臨床的な制約、または事前に決めておいたモデル選択のルールに基づいて、1つの閾値を選ぶ。
3. その閾値を固定する。
4. test set 上で、全体・患者群ごと・最も性能が低い群、それぞれの指標を評価する。

test set の結果を見てから最も公平に見える閾値を後付けで選ぶことはしない。「閾値を動かしながら探索的に傾向を確認する」段階と、「事前に決めたルールで選んだ1つの閾値での確認的な評価」段階は、報告の際にも分けて記載する。

モデル同士を比較したとき、全体の `Recall 0` 対 `Recall 1` の曲線がほぼ重なるなら、モデル間の性能差は主に「どの閾値を選んだか」の違いで説明できると解釈する。逆に、同じ全体性能（同じ utility）に揃えて比較しても公平性の指標に差が残るなら、それは閾値の違いでは説明できない、モデル固有の患者群ごとのスコア分布の違いが残っていると判断する。

## 新規性の候補

主たる新規性の候補は、患者 metadata を利用する条件付き分類を「metadata を使うか否か」という二値的な問題として扱わず、metadata の用途を次の3つに分けて理解・制御する問題として定式化する点にある。

- **prior**: 有病率などの事前情報として使う
- **画像との interaction**: 画像の解釈のしかたを変える
- **decision policy**: 最終的な判定の閾値の決め方

> 条件付き医療画像分類器における metadata の機能を分離して解析し、各機能の利用強度を操作可能なモデルを構築することで、予測性能・calibration（予測確率の信頼性）・subgroup reliability（患者群ごとの性能の安定性）の関係を明らかにする。

局所性能解析（患者ごとの性能差の分析）と operating-point sweep（閾値を動かしながらの評価）は、この中心命題を検証するための評価方法として位置づける。新規性は、単一の clustering 手法や Hypernetwork の構造変更だけに依存させない。

想定する既存領域との差分は次のように整理する。実際に新規性を主張する前に、次の既存研究領域との重複を調査する。

- **prior correction**: 患者群ごとの有病率の違いを補正する研究
- **multimodal shortcut learning**: 複数モダリティを使うモデルが、本来の疾患特徴ではなく近道の手がかり（shortcut）を学習してしまう問題の研究
- **conditional calibration**: 患者群などの条件ごとに、予測確率の信頼性を調整する研究
- **fairness-aware thresholding**: 公平性を考慮して判定閾値を決める研究
- **disentangled multimodal learning**: 複数モダリティの情報を、意味のある要素ごとに分離して学習する研究

| 既存の研究領域 | その領域の主な問い | 本研究で新たに追加する問い |
| --- | --- | --- |
| demographic fairness（患者属性ごとの公平性） | race、sex、age といった患者属性の間に性能差があるか | 既知の患者群の内側・外側で、条件付けの効果はどう異なるか |
| hidden stratification（隠れた層別化） | 粗い疾患ラベルの中に、性能が低い未知の subclass があるか | 条件付けによって、その弱い領域がどう変化するか |
| subgroup discovery（subgroup 発見） | 1つのモデルが系統的に間違えている患者の集まり（error slice）は何か | 複数モデルを比較したとき、局所的な性能差はどこに集中するか |
| hidden cohort fairness（隠れた集団の公平性） | 隠れた患者集団（hidden cohort）を使って、最も性能が低い群の性能を改善できるか | 条件付きモデル自体が、患者群ごとの性能の安定性（cohort reliability）にどう影響するか |
| multimodal / Hypernetwork（画像+属性の統合モデル） | metadata を使うことで平均性能が上がるか | metadata が prior・interaction・decision のどこに作用しているか |
| calibration / prior correction（予測確率の較正） | 患者群ごとの有病率の違いをどう補正するか | prior としての利用と、画像との interaction を、同一モデルの中でどう分離・制御するか |
| fairness-aware decision（公平性を考慮した意思決定） | 患者群間の性能差（group gap）をどう制約するか | 予測そのものと、判定の閾値を決める decision policy を分け、metadata の使われ方との関係をどう制御するか |

## 降格した研究案

以下は、検討はしたが現時点では研究の主軸にしないと判断した案である。

### 生成された分類器の重みそのものを比較する解析

Hypernetwork が生成した weight ベクトル同士の距離（parameter geometry）を直接比較して、「metadata ごとにどれだけ違う分類器が生成されているか」を測るという案。ただし weight の値は、同じ関数を別の重みの組み合わせで表現できてしまう性質（再パラメータ化）や、画像表現の取り方に依存してしまい、値の距離が「機能としての違い」を正しく反映するとは限らない。そのため、これは研究の主軸にはせず、局所的な性能差が別の方法で確認できた後の補助的な解析として位置づける。

### 新しい subgroup 発見手法の提案

複数のモデルの出力を横断して、低性能な患者群を自動発見する新しい手法を提案する案。ただし、次の課題がある。

- 正解となる subgroup が事前に分かっていない（ground-truth subgroup の欠如）
- どの特徴量や cluster 数を使うかに恣意性が残る
- エラーを手がかりに subgroup を探すこと自体が、エラーの定義に依存してしまう（循環論法になりやすい）
- 既存手法との違いを明確に主張しづらい

そのため、現段階では新しい発見手法を提案すること自体は目標にせず、既存の subgroup 発見手法は「監査のための道具」として使う。

### Hypernetwork を公平性改善手法として打ち出すこと

現状の実験では、Hypernetwork の導入によって `Recall` の群間差が悪化するケースも観察されている。そのため、「Hypernetwork は公平性を改善する手法である」という方向で研究を打ち出すのはまだ早い。まずは、metadata による条件付けが性能とエラーの起こり方にどのような影響を与えるのかを明らかにすることを優先する。

## 査読で指摘されうる主なリスク

- CheXpert という単一データセットだけでの実験であり、他のデータセットや施設でも同じ結果が得られるかは分からない（一般化可能性の不足）。
- 対象とする疾患（pathology）、評価指標、閾値、クラスタリングの設定など、多くの組み合わせを試すことによる多重比較の問題（たまたま良く見える組み合わせを選んでしまうリスク）。
- 同じデータを使って「低性能な subgroup を発見すること」と「その subgroup での性能を評価すること」の両方を行うと、発見した差が本物か偶然かを区別できなくなる。
- 症例数が少ない領域で、たまたま低性能に見えているだけの可能性（少数領域の偶然の低性能）。
- 撮影条件やラベルの間違い（label noise）を、患者属性による subgroup の違いだと誤って解釈してしまうリスク。
- 比較しているモデル同士でパラメータ数や学習条件が揃っていないことによる、公平でない比較。
- 性別や人種など保護すべき属性の metadata を使うことで、属性ごとに実質的に別々のモデルを学習してしまっている状態（group-specific specialization）になっていないか。
- 「reliability（同じ患者群内での性能の安定性）」と「fairness（患者群間の公平性）」という、本来別の概念を混同してしまうリスク。
- 相関関係が見えたことをもって、因果関係（なぜそれが起きているか）まで主張してしまうリスク。

## 現時点での優先順位

研究全体を次の4段階に分ける。

1. **機序の発見**: 既存 Hypernetwork の変化が、ランキング性能の変化（ranking）、metadata による事前確率・スコアのシフト（prior / score shift）、画像と metadata の相互作用（interaction）のどれから生じるかを特定する。
2. **機能的定式化**: metadata 利用を prior・interaction・decision policy に分け、各成分を操作可能にする定義と解析方法を確立する。
3. **モデル提案**: 各経路を明示的に分離し、その利用強度を制御できる条件付き分類モデルを設計する。
4. **立証と一般化**: 各経路への介入が `AUROC`・calibration・`Recall`・group gap・worst-group performance に与える影響を検証し、複数条件で一般化可能性を評価する。

直近は第1段階に集中し、次の順に進める。

1. 比較モデルと統制条件を確定する。
2. 対象とする疾患（primary pathology）と、主要な評価指標（primary metric）を事前に絞る。
3. weight/bias アブレーションと operating-point sweep を行う。
4. 患者単位で、モデル間の予測・損失を対応づけた表（paired prediction / loss table）を作る。
5. metadata を入れ替えたりマスクしたりする介入実験を行う。
6. 共通の患者表現上で、患者ごとの局所的な性能差 `Delta_i` を推定する。
7. 得られた機序から、新しいモデルに必要な分離の制約や制御変数を定義する。

## 今後の対話で決める事項

- 最終目標を、検証可能な細かい仮説・反証条件・KPI に分解する。
- 「prior」「interaction」「decision policy」それぞれの操作的定義（何をもってそれと判定するか）と識別条件を定める。
- 提案モデルの制御対象と、制御が成功したと言える指標を定める。
- 主要な対象疾患（primary pathology）と、補助的な対象疾患（secondary pathology）
- 主要な評価対象（primary outcome）と、想定する臨床的な操作点（operating point）
- 「患者領域」（局所的な効果を語る際の単位）を定義する共通の表現方法
- 局所効果を推定する統計手法
- 容量を揃えた baseline（capacity-matched baseline）の具体的な構造
- subgroup として採択するために必要な最小症例数
- validation / test の分割方法と、複数 seed を使う際の設計
- fairness（群間の公平性）と reliability（群内の安定性）を分けて報告する方法
- 修士研究の時間内で実施する解析の範囲
