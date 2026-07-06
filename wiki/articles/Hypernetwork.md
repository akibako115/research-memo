---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_hypernetworks]]"
---

# Hypernetwork

モデルに条件情報を入れたいとき，単に入力特徴量を結合するだけでは，その条件が「どの層の，どのパラメータの，どの振る舞いを変えるのか」が曖昧になる．Hypernetwork はこの問題に対して，**別のネットワークの重みそのものを生成するネットワーク**を導入し，条件や層 ID や時系列文脈を parameter space に反映させるための考え方である．

これがあると，条件付きモデルを「入力に属性を足したモデル」ではなく，「条件に応じて計算規則を変えるモデル」として設計できる．医療画像分類で患者属性，撮像条件，施設，subgroup などを使う場合にも，どの程度まで group-specific な重み変化を許すかを制御する候補になる．

## 重みを直接持つモデルから重みを生成するモデルへ

| 構成 | 重みの持ち方 | 条件の入り方 | 向いている問い |
| --- | --- | --- | --- |
| 通常の neural network | main network が全重みを直接持つ | 入力特徴量として入れる | 条件を特徴量として使えば十分か |
| static hypernetwork | 層 embedding から各層の重みを生成する | layer ID / layer embedding | 層間でどの程度重み生成規則を共有できるか |
| dynamic hypernetwork | 入力や時刻文脈から重み調整を生成する | sample / timestep ごとの文脈 | 条件ごとに計算規則を変えるべきか |

Hypernetwork では，学習対象が main network の全重みそのものではなく，重みを生成する関数と，その関数に渡す embedding になる．このため，main network の重み空間に構造を入れられる．

```text
condition / embedding
        |
        v
  hypernetwork
        |
        v
generated weights or weight updates
        |
        v
  main network
        |
        v
prediction
```

## 層間共有として見る

CNN の各層が完全に独立した filter を持つと，表現力は高いがパラメータ数が増える．一方，RNN のように全時刻で同じ重みを共有すると，パラメータ効率は高いが，文脈ごとに計算規則を変えにくい．

Hypernetwork はこの両端の中間として理解できる．すべての重みを共有するのではなく，**重みを生成する規則を共有し，embedding によって個別性を持たせる**．このため，完全独立な重みより制約が強く，完全共有より柔軟な設計になる．

## 条件付きモデルとして見る

Hypernetwork の重要な使い方は，条件を main network の入力に足すのではなく，main network の重み生成に使うことである．

たとえば患者属性付き医療画像分類では，次の2つは同じではない．

| 方式 | 何が変わるか | 注意点 |
| --- | --- | --- |
| image feature と tabular feature を結合 | classifier の入力表現 | 条件がどの層に効いたか追いにくい |
| FiLM / conditional normalization | activation の scale / shift | 変調対象は activation |
| hypernetwork | weight / adapter / modulation parameter | 条件ごとの専門化が強くなりうる |

Hypernetwork は条件ごとに重みを変えるため，subgroup reliability を改善する可能性がある一方で，protected attribute による過度な group-specific specialization や shortcut を生む可能性もある．そのため，医療画像 fairness では平均性能だけでなく，group-wise calibration，worst-group performance，attribute leakage，分布外施設への generalization を同時に見る必要がある．

## 具体例で理解する

**Step 1 — 条件を embedding にする**

層 ID，時刻文脈，患者属性，撮像条件などを embedding `z` に変換する．静的 hypernetwork では layer embedding が使われ，動的 hypernetwork では入力や hidden state から embedding が生成される．

**Step 2 — embedding から重みを生成する**

hypernetwork `g` が `z` を受け取り，main network の重み `W` または重み更新量を生成する．

```text
W = g(z)
```

実用上は full weight matrix を毎回生成すると重いため，row scaling，low-rank update，adapter weight，normalization parameter など，より小さい対象を生成する設計が使いやすい．

**Step 3 — 生成された重みで予測する**

main network は生成された重みを使って通常の forward pass を行う．このとき main network の構造は固定でも，その計算規則は条件に応じて変化する．

**Step 4 — main network と hypernetwork を同時に学習する**

HyperNetworks 論文の中心は，hypernetwork と main network を end-to-end backpropagation で同時に学習できる点にある．進化計算や手設計の重み生成規則に依存しないため，大規模な CNN / RNN にも適用しやすい．

## 設計上の判断

重み全体を生成するほど表現力は高いが，メモリ，計算量，過学習，解釈困難性が増える．逆に，scale / shift や low-rank update だけを生成すると表現力は下がるが，安定して学習しやすく，どの条件がどの変調を起こしたか追いやすい．

医療画像と tabular metadata の融合では，hypernetwork をいきなり全 CNN weight に適用するより，次のような限定された使い方の方が検証しやすい．

| 生成対象 | 利点 | リスク |
| --- | --- | --- |
| classifier head | 実装が簡単で影響範囲が狭い | 画像特徴抽出器は条件非依存のまま |
| adapter / LoRA weight | 条件付き専門化と制御性のバランスが良い | adapter 容量の選び方に依存 |
| normalization / FiLM parameter | 軽量で安定しやすい | weight generation というより activation modulation に近い |
| selected layer parameter | [[HyperFusion]] のように画像処理 network の一部重みを条件付きにできる | subgroup-specific shortcut の検証が必要 |
| convolution kernel 全体 | 表現力が高い | 計算量と fairness リスクが大きい |

## Fairness 研究での使いどころ

患者属性を使う hypernetwork は，「属性を使えば公平になる」という単純な主張には使えない．むしろ，属性条件付きで重みが変わることにより，どの subgroup にどのような帰納バイアスを与えるかを検証する枠組みになる．

特に重要な検証軸は以下である．

| 検証軸 | 見るべきこと |
| --- | --- |
| subgroup performance | 各属性群，交差属性群，hidden subgroup の性能 |
| worst-group behavior | 平均性能ではなく最悪群が改善するか |
| calibration | subgroup ごとの confidence が歪まないか |
| attribute dependence | protected attribute が疾患 signal ではなく shortcut として使われていないか |
| generalization | 施設・データセット・撮像条件が変わっても改善が残るか |
| generated parameter analysis | 属性ごとの生成重みや adapter がどの程度分化しているか |

## リファレンス

| 用語 | 意味 |
| --- | --- |
| hypernetwork | main network の重みや重み調整を生成するネットワーク |
| main network | 実際に入力から予測を行うネットワーク |
| static hypernetwork | 固定 embedding から層ごとの重みを生成する構成 |
| dynamic hypernetwork | 入力，時刻，hidden state などに応じて重みを動的に生成・調整する構成 |
| relaxed weight-sharing | 完全共有と完全独立の中間として，重み生成規則を共有しつつ個別性を持たせる考え方 |
| HyperLSTM | LSTM の重みや weight scaling を hypernetwork で動的に調整する構成 |

## 関連概念

- [[Conditional_Modulation]]
- [[FiLM]]
- [[HyperFusion]]
- [[Image_Tabular_Fusion]]
- [[Subgroup_Reliability]]
- [[Fairness_Evaluation]]
