---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_hypernetworks.pdf"
---

# HyperNetworks

David Ha，Andrew Dai，Quoc V. Le による論文．あるネットワーク（hypernetwork）が別のネットワーク（main network）の重みを生成する手法を扱う．HyperNEAT や fast weights の流れを受けつつ，本論文の hypernetwork は main network と一緒に backpropagation で end-to-end に学習される点を強調する．

対象は主に deep convolutional network と long recurrent network である．静的 hypernetwork は CNN の層ごとの重みを生成し，動的 hypernetwork は RNN/LSTM の重みを時刻ごと・入力系列ごとに変化させる．著者らは，hypernetwork を「層間の厳密な weight sharing と完全に独立した重みの中間にある，relaxed weight-sharing」として位置づける．

## 問題設定

通常の neural network では，main network 自身が入力から出力への写像を学習する．本論文では，main network の重みを直接パラメータとして持つ代わりに，小さな hypernetwork が main network の重みを生成する．

著者らは，この関係を genotype と phenotype の関係に類比する．hypernetwork が genotype，main network が phenotype に対応する．ただし，HyperNEAT のように進化計算で探索するのではなく，hypernetwork と main network を gradient descent で同時に学習する．

## 関連研究との位置づけ

本論文は HyperNEAT，Compressed Weight Search，Differentiable Pattern Producing Networks，fast weights，parameter prediction 系の研究を関連研究として挙げる．

- HyperNEAT は virtual coordinate を入力にして大きなネットワークの重み構造を生成するが，進化計算を使うため大規模問題では遅い．
- Compressed Weight Search は DCT によって重み空間を圧縮するが，DCT prior が多くの問題に適しているとは限らない．
- fast weights は，あるネットワークが別のネットワークの context-dependent な重み変化を生成する考え方である．
- Denil et al.，Yang et al.，Bertinetto et al.，De Brabandere et al. などは CNN の一部パラメータを別ネットワークで予測するが，本論文は recurrent network への適用を主要な貢献として扱う．

## Static Hypernetwork

static hypernetwork は feedforward convolutional network の重みを生成する．各 convolution layer `j` に layer embedding `z_j` を割り当て，hypernetwork `g` が kernel `K_j` を生成する．

```text
K_j = g(z_j),  j = 1, ..., D
```

論文では convolution kernel を `N_in` 個の slice に分け，2層の線形 hypernetwork で生成する．学習されるのは，hypernetwork の共有パラメータと，各層の embedding `z_j` である．推論時には，学習済み embedding から各 layer の kernel を再生成する．

この構成では，通常の convolutional network が各層に独立した kernel を持つのに対して，hypernetwork は層間で生成規則を共有する．そのため，著者らは static hypernetwork を CNN の深い層に対する relaxed weight-sharing として解釈する．

kernel size や channel 数が層ごとに異なる場合には，基本サイズの kernel を生成し，必要に応じて複数の basic kernel を結合して大きな kernel を構成する．CIFAR-10 の Wide Residual Network 実験では，基本 channel サイズを 16 とし，embedding size `N_z = 64` を用いる．

## Dynamic Hypernetwork

dynamic hypernetwork は recurrent network の重みを時刻ごとに生成する．通常の RNN では `W_h`，`W_x`，`b` が系列全体で固定されるが，HyperRNN ではこれらを embedding の関数として変化させる．

一般形では，HyperRNN が入力 `x_t` と main RNN の前時刻 hidden state `h_{t-1}` から internal state を計算し，そこから `z_h`，`z_x`，`z_b` を生成する．これらの embedding が main RNN の重みと bias を生成する．

ただし，完全な重み行列を時刻ごとに生成するとメモリ使用量が大きいため，実用的な構成では各重み行列の row を scaling vector で動的にスケールする．これにより，重み行列全体を生成するほどの自由度はないが，Basic RNN に比べて許容可能な追加メモリで動的な重み調整ができる．

この scaling は，Recurrent Batch Normalization，Layer Normalization，Multiplicative RNN，Multiplicative Integration RNN と関係する．ただし，normalization が統計量に基づく固定的なスケーリングを学習するのに対し，HyperRNN は入力サンプルと時刻ごとに異なる scaling policy を学習する．

論文の実験では，主に LSTM 版である HyperLSTM を使う．HyperLSTM では LSTM の input gate，candidate，forget gate，output gate に対応する重み群に対して，hypernetwork が動的な scaling を与える．

## 実験結果

### MNIST

static hypernetwork を小さな2層 convolutional network に適用し，2層目の `7x7x16x16` kernel を生成した．embedding size は `N_z = 4`．通常の CNN は test accuracy 99.28%，hypernetwork 版は 99.24% でほぼ同等だった．この例では，12,544 個の kernel weight が 4 次元 embedding と 4,240 個の hypernetwork parameter から生成された．

### CIFAR-10

Wide Residual Network の `conv2`，`conv3`，`conv4` に含まれる 36 層分の kernel を単一の hypernetwork で生成した．WRN 40-1 と WRN 40-2 を対象とし，embedding size `N_z = 64` を用いた．

主な結果は以下である．

| Model | Test Error | Param Count |
| --- | ---: | ---: |
| Wide Residual Network 40-1 | 6.73% | 0.563M |
| Hyper Residual Network 40-1 | 8.02% | 0.097M |
| Wide Residual Network 40-2 | 5.66% | 2.236M |
| Hyper Residual Network 40-2 | 7.23% | 0.148M |

著者らは，relaxed weight sharing によって分類精度は約 1.25-1.5% 低下するが，パラメータ数は大幅に削減されると述べる．低下の理由として，深い CNN の各層は異なるレベルの特徴を抽出するため，本来は層ごとに異なる filter が必要であり，hypernetwork は 64 次元 embedding で層差を表現しつつも共通性を課すため，最適な独立 filter には届かない，と説明する．

### Penn Treebank

character-level Penn Treebank で HyperLSTM を評価した．HyperLSTM cell は 128 units，signal size は 4．LSTM，Layer Norm LSTM，HyperLSTM，Layer Norm HyperLSTM を比較した．

主な bits-per-character は以下である．

| Model | Test | Validation | Param Count |
| --- | ---: | ---: | ---: |
| LSTM, 1000 units | 1.312 | 1.347 | 4.25M |
| Layer Norm LSTM, 1000 units | 1.267 | 1.300 | 4.26M |
| HyperLSTM, 1000 units | 1.265 | 1.296 | 4.91M |
| Layer Norm HyperLSTM, 1000 units | 1.250 | 1.281 | 4.92M |
| Layer Norm HyperLSTM, Large Embedding | 1.233 | 1.263 | 5.06M |
| 2-Layer Norm HyperLSTM | 1.219 | 1.245 | 14.41M |

HyperLSTM は大きな LSTM や深い LSTM より良く，Layer Norm LSTM と同程度だった．Layer Norm と HyperLSTM を組み合わせるとさらに性能が向上したため，著者らは HyperLSTM が moments-based normalization を超える調整 policy を学習している可能性を示す．

### enwik8

Hutter Prize Wikipedia dataset（enwik8）で character language modeling を行った．データセットは 100M characters，205 unique characters からなる．

主な bits-per-character は以下である．

| Model | enwik8 | Param Count |
| --- | ---: | ---: |
| LSTM, 1800 units | 1.470 | 14.81M |
| Layer Norm LSTM, 1800 units | 1.402 | 14.82M |
| HyperLSTM, 1800 units | 1.391 | 18.71M |
| Layer Norm HyperLSTM, 1800 units | 1.353 | 18.78M |
| Layer Norm HyperLSTM, 2048 units | 1.340 | 26.54M |

HyperLSTM は Layer Norm LSTM と競合し，Layer Norm HyperLSTM は near state-of-the-art の結果を示した．また，HyperLSTM は LSTM や Layer Norm LSTM より training step あたりの収束が速いと述べられている．

### Handwriting Sequence Generation

IAM online handwriting database を用い，pen stroke の `(x, y)` 座標と pen-up/pen-down indicator を予測した．データセットは 221 writers による 12,179 handwritten lines であり，平均 sequence length は約 700，最長は約 1,900 steps．

主な validation log-loss は以下である．

| Model | Log-Loss | Param Count |
| --- | ---: | ---: |
| LSTM, 900 units | -1,055 | 3.36M |
| Layer Norm LSTM, 900 units | -1,096 | 3.37M |
| Layer Norm HyperLSTM, 900 units | -1,067 | 3.95M |
| HyperLSTM, 900 units | -1,162 | 3.94M |

このタスクでは Layer Norm は HyperLSTM と相性が悪く，Layer Norm なしの HyperLSTM が最良だった．著者らは，handwriting generation では statistical normalization が重み調整 policy として最適から遠い可能性を示す．

### Neural Machine Translation

GNMT の wordpiece model architecture（vocabulary size 32k）で LSTM cell を HyperLSTM cell に置き換え，WMT'14 English-to-French の newstest2014 で評価した．

| Model | Test BLEU | Log Perplexity |
| --- | ---: | ---: |
| GNMT WPM-32K, LSTM | 38.95 | 1.027 |
| GNMT WPM-32K, ensemble of 8 LSTMs | 40.35 | - |
| GNMT WPM-32K, HyperLSTM | 40.03 | 0.993 |

HyperLSTM は既存の GNMT single model を改善し，大規模な production-level neural machine translation model にも適用可能であることを示した．

## 解析

enwik8 の生成例では，HyperLSTM の weight scaling vector の変化を可視化している．重み変化が小さい領域では生成される phrase がより deterministic に見え，重み変化が大きい領域は単語間や bracket 周辺に多いと述べられている．

Layer Norm と HyperLSTM の違いを見るため，LSTM の hidden state `φ(c_t)` の histogram も比較している．Layer Norm は vanilla LSTM より saturation を減らすが，HyperLSTM では多くの時間で cell が saturated している．著者らは，HyperLSTM の動的重み調整 policy は statistical normalization とはかなり異なる挙動をしているが，同程度の性能を達成したと解釈する．

handwriting generation の可視化では，重み変化の高い領域は連続的にゆっくり変化するというより，単語間や文字間に集中した discrete な regime change として現れると述べている．

## 結論

本論文は，別の neural network の重みを生成する hypernetwork を end-to-end backpropagation で学習する方法を示した．static hypernetwork は convolutional network の重み生成に使われ，parameter count を大きく削減しながら競争力のある精度を示した．dynamic hypernetwork は recurrent network の重みを時刻・入力ごとに調整し，language modeling，handwriting generation，machine translation で LSTM baseline と同等以上の結果を示した．

## 関連概念

- [[Hypernetwork]]
- [[Static_Hypernetwork]]
- [[Dynamic_Hypernetwork]]
- [[HyperLSTM]]
- [[Relaxed_Weight_Sharing]]
- [[Weight_Generation]]
- [[Conditional_Modulation]]
