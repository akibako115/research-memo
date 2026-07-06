---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_daft_interweave_tabular_data_3d_images_cnns]]"
---

# DAFT

[[FiLM]] は条件情報から feature map の scale / shift を生成するが，条件情報の側は画像特徴を知らない．画像特徴と表形式データに冗長性がある場合（たとえば CNN が年齢に対応する特徴を画像から学ぶが，年齢は tabular data にも含まれている），条件の作り方自体が画像特徴に依存すべきことがある．DAFT はこの問題に対して，global average pooling した画像特徴と tabular data の両方から scale / shift を生成する module である．

これがあると，tabular data が画像特徴を一方的に変調するだけでなく，画像特徴の状態に応じて tabular data の使い方も変わる．FiLM が one-way conditioning であるのに対し，DAFT は image と tabular の two-way exchange を意図した設計である．

## FiLM との違い

| 観点 | FiLM | DAFT |
|---|---|---|
| conditioning 入力 | tabular / metadata のみ | tabular + GAP した image feature |
| 情報フロー | tabular → image（one-way） | tabular ↔ image（two-way） |
| scale / shift の決め方 | 条件入力だけで決まる | 画像特徴にも依存して決まる |
| 追加パラメータ | 小さい（FiLM generator のみ） | やや大きい（bottleneck network） |
| 冗長性の扱い | 考慮しない | image と tabular の冗長性を auxiliary network で吸収 |

## 構造

DAFT は CNN の convolutional feature map `F_{i,c}` を，患者 `i` の tabular data `x_i` と image feature map 自身に基づいて affine transform する．

```text
3D image
  |
CNN feature map F ---- global average pooling ----+
                                                   |
tabular vector x ----------------------------------+--> auxiliary network --> α, β
                                                                        |
                                                                        v
                                                     F' = α * F + β
```

auxiliary network の処理手順:

1. feature map `F_i` の spatial dimensions を global average pooling で squeeze する
2. image feature vector と tabular vector `x_i` を concatenation する
3. FC layer + ReLU で bottleneck に圧縮する（圧縮率 `r = 7`）
4. 2 つ目の FC layer で channel 数 `C` に対応する `α_i` と `β_i` を出力する
5. `F'_{i,c} = α_{i,c} F_{i,c} + β_{i,c}` を適用する

## 挿入位置と設計判断

DAFT は CNN の任意の位置に挿入できるが，原論文では最後の residual block に入れる構成を推奨する．CNN の初期層は edge や blob のような primitive concept を扱うため，臨床 tabular data との level exchange は high-level concept を扱う late convolutional layer の方が妥当だとされる．

ablation の結果，DAFT は挿入位置に対して比較的頑健であり，ほとんどの位置で concatenation-based baseline を上回った．

### scale と shift の役割

| 設定 | diagnosis bACC | progression c-index | 解釈 |
|---|---|---|---|
| `α = 1`（scale なし） | 0.581 | 0.743 | 大きく低下．scale は重要 |
| `β = 0`（shift なし） | 0.609 | 0.746 | 低下するが scale ほどではない |
| sigmoid / tanh で α を制約 | 0.600 | 0.756-0.770 | diagnosis で低下，progression で改善もあり |
| Proposed（制約なし） | 0.622 | 0.748 | diagnosis で最良 |

test-time ablation では，`β` を training set mean で固定すると大きく性能低下し，tabular information が主に shifting を通じて統合されていることが示唆された．

## AD 診断での性能

DAFT は AD diagnosis（CN / MCI / AD 3 クラス分類）と time-to-dementia prediction（MCI → dementia の生存分析）で評価された．

| Model | Diagnosis bACC | Progression c-index |
|---|---|---|
| Linear Model（tabular only） | 0.552 | 0.719 |
| ResNet（image only） | 0.504 | 0.599 |
| Concat-1FC | 0.587 | 0.729 |
| FiLM | 0.601 | 0.712 |
| **DAFT** | **0.622** | **0.748** |

diagnosis task では tabular-only の Linear Model が image-only の ResNet を上回った．これは CSF biomarkers や PET-derived summary のような tabular data が MRI より早期に異常を示す場合があるためである．DAFT は両方を使い，全 baseline を上回った．

AIBL への generalization 実験でも DAFT は最高 bACC だったが，FiLM との差は ADNI で +0.009，AIBL で +0.004 であり有意差は弱い．backbone を ConvNet に変えても DAFT は全手法を上回り，backbone に依存しない統合能力を示した．

## Tabular feature の寄与

Baseline Shapley approach で tabular features の marginal contribution を推定した結果，FDG-PET，T-tau，Aβ42 が最も重要だった．これらはいずれも AD の既知 biomarker である．

## 医療画像 fairness での位置づけ

DAFT 論文自体は fairness 指標を主題にしていない．しかし，患者属性条件付きモデルを医療画像 fairness に使う場合，DAFT は以下の点で候補になる．

| 観点 | DAFT の特徴 |
|---|---|
| 解析可能性 | `α` / `β` が channel ごとに出るため，属性がどの特徴に効いているかを追跡しやすい |
| 冗長性の扱い | image と tabular の冗長な情報を auxiliary network で吸収できる |
| リスク | protected attribute を入れると subgroup-specific shortcut を学ぶ可能性がある |
| 検証項目 | subgroup performance，worst-group performance，`α` / `β` の subgroup 差，ablation |

[[Image_Tabular_Fusion]] の文脈では，DAFT は FiLM と [[HyperFusion]] の中間に位置する．FiLM より条件付けの自由度が高く，HyperFusion よりパラメータ生成の範囲が限定的である．

## リファレンス

| 用語 | 意味 |
|---|---|
| DAFT | Dynamic Affine Feature Map Transform．image feature と tabular data の両方から scale / shift を生成する module |
| auxiliary network | image feature（GAP 後）と tabular vector を受け取り，`α` / `β` を出力する小型ネットワーク |
| bottleneck | auxiliary network 内の圧縮層．channel 数を `r` 倍に削減して過学習を防ぐ |
| two-way exchange | image と tabular の双方向情報交換．FiLM の one-way flow との対比 |
| GAP | global average pooling．feature map の spatial dimensions を 1 つのスカラーに圧縮する |

## 関連概念

- [[FiLM]]
- [[HyperFusion]]
- [[Image_Tabular_Fusion]]
- [[Hypernetwork]]
- [[Conditional_Modulation]]
- [[Metadata_Conditioning]]
