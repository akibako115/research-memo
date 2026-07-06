---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_film_visual_reasoning_general_conditioning_layer.pdf"
---

# FiLM: Visual Reasoning with a General Conditioning Layer

Ethan Perez，Florian Strub，Harm de Vries，Vincent Dumoulin，Aaron Courville による論文．Feature-wise Linear Modulation（FiLM）という汎用 conditioning layer を提案し，visual reasoning，特に CLEVR benchmark において高い性能を示す．FiLM は conditioning information に基づいて中間特徴を feature-wise affine transformation で変調する．

著者らは，FiLM が CLEVR の state-of-the-art error を約半減し，feature map を選択的・一貫した形で変調し，ablation や architecture modification に頑健で，few-shot / zero-shot generalization にも有効であると報告する．

## FiLM の定義

FiLM は neural network の intermediate feature `F_{i,c}` に対し，conditioning input `x_i` から生成した `γ_{i,c}` と `β_{i,c}` を使って feature-wise affine transformation を適用する．

```text
γ_{i,c} = f_c(x_i)
β_{i,c} = h_c(x_i)
FiLM(F_{i,c} | γ_{i,c}, β_{i,c}) = γ_{i,c} F_{i,c} + β_{i,c}
```

`f` と `h` は任意の関数でよく，実装上は 1 つの FiLM generator が `(γ, β)` を出力する．FiLM layer を適用される側のネットワークは FiLM-ed network と呼ばれる．CNN に適用する場合，FiLM は spatial location には依存せず，feature map ごとに activation distribution を変調する．

FiLM は feature map を scale up / down，negate，shut off し，ReLU と組み合わせることで thresholding も行える．必要な parameter は modulated feature map ごとに `γ` と `β` の2つだけであり，計算コストは画像解像度に依存しない．

## CLEVR モデル構成

FiLM モデルは，FiLM-generating linguistic pipeline と FiLM-ed visual pipeline から構成される．

- FiLM generator は question を GRU で処理する．GRU は 4096 hidden units，word embedding は 200 次元．最終 hidden state から各 residual block の `(γ, β)` を affine projection で生成する．
- visual pipeline は 224 × 224 image から 128 個の 14 × 14 feature maps を抽出する．image features は scratch CNN または ImageNet pretrained ResNet-101 の conv4 feature を使う．
- image features は 4 個の FiLM-ed residual blocks で処理される．各 ResBlock は 128 feature maps を持つ．
- classifier は 1 × 1 convolution，global max-pooling，1024 hidden units の2層 MLP からなり，answer softmax を出力する．
- spatial reasoning のため，relative x / y position を表す coordinate feature maps を image features，各 ResBlock input，classifier input に結合する．

学習は image-question-answer triplets のみを使い，追加の program supervision や data augmentation は使わない．optimizer は Adam，learning rate `3e-4`，weight decay `1e-5`，batch size 64，最大 80 epochs である．

## 関連手法との関係

FiLM は Conditional Normalization（CN）の一般化として位置づけられる．CN は normalization layer の feature-wise affine transformation parameter を conditioning information の関数に置き換える．FiLM はこの affine conditioning を normalization 直後に限定せず，normalization-free な設定にも拡張する．

conditioning information を convolution layer input に constant feature map として結合する方法や，fully-connected layer input に結合する方法は，feature-wise conditional bias に対応する．WaveNet や Conditional PixelCNN の conditional bias も FiLM の `γ = 1` の場合とみなせる．

LSTM，Convolutional Sequence to Sequence，Squeeze-and-Excitation Networks などの feature-wise conditional scaling は，`β` を持たず `γ` が 0 から 1 に制限された FiLM に近い．FiLM は scale と shift の両方を持ち，値域も制限しない．また，FiLM はある network が別 network の parameter を生成するため，hypernetwork の一種とも見なせる．

## CLEVR 結果

CLEVR は 700K の `(image, question, answer, program)` tuples からなる synthetic visual reasoning dataset である．質問は counting，existence，attribute query，number comparison，attribute comparison などを含み，multi-step で compositional である．

主な CLEVR accuracy は以下である．

| Model | Overall | Count | Exist | Compare Numbers | Query Attribute | Compare Attribute |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Human | 92.6 | 86.7 | 96.6 | 86.5 | 95.0 | 96.0 |
| CNN+LSTM | 52.3 | 43.7 | 65.2 | 67.1 | 49.3 | 53.0 |
| CNN+LSTM+SA | 76.6 | 64.4 | 82.7 | 77.4 | 82.6 | 75.4 |
| N2NMN | 83.7 | 68.5 | 85.7 | 84.9 | 90.0 | 88.7 |
| PG+EE, 700K programs | 96.9 | 92.7 | 97.1 | 98.7 | 98.1 | 98.9 |
| CNN+LSTM+RN | 95.5 | 90.1 | 97.8 | 93.6 | 97.9 | 97.1 |
| CNN+GRU+FiLM | 97.7 | 94.3 | 99.1 | 96.8 | 99.1 | 99.1 |
| CNN+GRU+FiLM, raw pixels | 97.6 | 94.3 | 99.3 | 93.4 | 99.3 | 99.3 |

program supervision を使わない手法の中で，FiLM は state-of-the-art error を 4.5% から 2.3% におよそ半減した．また，pretrained image features を使わず raw pixels から学習したモデルでも同等の性能を示した．

## FiLM が学習するもの

activation visualization では，FiLM model は answer-related object や question-related object の近傍の feature を使って予測している．著者らは，適切な feature modulation が間接的に spatial modulation を生むと述べる．

`γ` と `β` の histogram では，`γ` は -15 から 19，`β` は -9 から 16 の広い範囲を取る．`γ` は 0 付近に鋭い peak を持ち，FiLM が question に基づいて feature map 全体を shut off または大きく suppress することを示す．`γ` の 36% は負であり，FiLM 後に ReLU があるため，`γ < 0` は downstream に通る activation を大きく変えうる．`β` の 76% は負であり，ReLU を通る activation の選択にも使われる．

t-SNE 解析では，初期 FiLM layer の `(γ, β)` は low-level reasoning function ごとにまとまり，後期 FiLM layer の `(γ, β)` は high-level reasoning function ごとにまとまる．著者らは，FiLM が architectural prior なしに function-based modularity のような構造を学習していると解釈する．

## Ablation

FiLM の `γ` と `β` を分けて制限した ablation では，`β := 0` で 96.9%，`γ := 1` で 95.9% の validation accuracy だった．両方を使う best architecture は 97.4±0.4% である．著者らは，FiLM は biasing または scaling の片方だけでも conditioning できるが，両方を使う方が良く，特に `γ` が重要だと述べる．

test-time ablation では，trained model の `β` を training set mean に置き換えると accuracy drop は 1.0% だったが，`γ` を同様に置き換えると 65.4% drop した．Gaussian noise に対しても `γ` の方が敏感であり，実際には FiLM が主に `γ` を通じて conditioning していることを示す．

`γ` を `(0, 1)` に sigmoid で制限した場合は 95.9%，`(-1, 1)` に tanh で制限した場合は 96.3%，`(0, ∞)` に exp で制限した場合も 96.3% であり，制限なしの FiLM より低かった．著者らは，大きな magnitude で scale できること，feature map を negate / zero out できることが有効だと述べる．

FiLM を ResBlock 内の別位置に移動しても大きな性能低下はなく，normalization 直後である必要はない．`No batch normalization` でも 93.7% を保つ．この結果から，著者らは FiLM の効果は normalization と密接に結びついているわけではないと結論づける．

FiLM layer 数については，1 ResBlock でも 93.5%，2 ResBlocks で 97.1%，4 ResBlocks で 97.4±0.4%，6 ResBlocks で 97.7% である．少数の FiLM layer でも高い性能を示すが，深い FiLM-ed network では reasoning が pipeline 全体に分散されると述べられている．

## CLEVR-Humans

CLEVR-Humans は CLEVR images に対する human-posed questions であり，18K train，7K validation，7K test からなる．質問はより多様な語彙と複雑な概念を含む．

著者らは CLEVR-trained FiLM model の visual pipeline を固定し，FiLM-generating linguistic pipeline のみを CLEVR-Humans で fine-tune した．主な test accuracy は以下である．

| Model | Train CLEVR | Train CLEVR, fine-tune human |
| --- | ---: | ---: |
| LSTM | 27.5 | 36.5 |
| CNN+LSTM | 37.7 | 43.2 |
| CNN+LSTM+SA+MLP | 50.4 | 57.6 |
| PG+EE, 18K programs | 54.0 | 66.6 |
| CNN+GRU+FiLM | 56.6 | 75.9 |

FiLM は fine-tuning 前後のどちらでも state-of-the-art generalization を示した．fine-tuning 後は PG+EE を 9.3% 上回った．

## CLEVR-CoGenT

CLEVR-CoGenT は compositional generalization を測るための dataset である．Condition A では cube が gray/blue/brown/yellow，cylinder が red/green/purple/cyan に限定される．Condition B では cube と cylinder の color palettes が入れ替わる．sphere は両 condition で全色を取る．この設定は，モデルが trait combination を記憶しているのか，disentangled / general representation を学んでいるのかを見る．

主な結果は以下である．

| Method | Train A: A | Train A: B | Fine-tune B: A | Fine-tune B: B |
| --- | ---: | ---: | ---: | ---: |
| CNN+LSTM+SA | 80.3 | 68.7 | 75.7 | 75.8 |
| PG+EE, 18K programs | 96.6 | 73.7 | 76.1 | 92.7 |
| CNN+GRU+FiLM | 98.3 | 75.6 | 80.8 | 96.9 |
| CNN+GRU+FiLM 0-Shot | 98.3 | 78.8 | 81.1 | 96.9 |

FiLM は compositional generalization でも他手法を上回ったが，Condition A から B への zero-shot accuracy には低下があり，attribute combination bias も残る．著者らは FiLM parameter space で質問の `(γ, β)` を線形結合する zero-shot method を試し，Train A / Test B で 3.2% の overall accuracy gain を得た．ただし，この方法を適用できたのは B の質問の 1/3 である．

## エラー分析

appendix の error analysis では，多くの誤りは partial occlusion によるものだとされる．FiLM の計算コストは解像度に依存しないため，高解像度 CNN によって改善できる可能性がある．counting error の 96.1% は off-by-one error だった．また，正しく count しているにもかかわらず比較質問で論理的に矛盾した回答をする例があり，logical inconsistency を直接最小化することは FiLM と直交する将来課題として挙げられる．

## 結論

FiLM は，conditioning information に基づいて neural network の intermediate features を feature-wise affine transformation で選択的に変調する汎用手法である．visual reasoning において，FiLM は RNN が言語情報を使って CNN の挙動を変え，多様な multi-step reasoning task を解くことを可能にした．Ablation から，FiLM の成功は normalization に密接に依存しないこと，`γ` による scaling が特に重要であること，制限のない affine modulation が有効であることが示された．

## 関連概念

- [[FiLM]]
- [[Conditional_Modulation]]
- [[Feature_Wise_Affine_Modulation]]
- [[Conditional_Normalization]]
- [[Hypernetwork]]
- [[Image_Tabular_Fusion]]
