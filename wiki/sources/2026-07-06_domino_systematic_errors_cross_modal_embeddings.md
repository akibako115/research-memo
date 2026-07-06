---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_domino_systematic_errors_cross_modal_embeddings.pdf"
---

# Domino: Discovering Systematic Errors with Cross-Modal Embeddings

Sabri Eyuboglu，Maya Varma，Khaled Saab，Jean-Benoit Delbrouck，Christopher Lee-Messer，Jared Dunnmon，James Zou，Christopher Ré による ICLR 2022 論文．高い overall accuracy を持つ model が，important subsets / slices で systematic errors を起こす問題に対し，cross-modal embeddings と error-aware mixture model を使う slice discovery method（SDM）である Domino を提案する．

Domino は，underperforming かつ coherent な slice を発見し，自然言語で説明することを目的とする．著者らは，natural images，medical images，medical time-series の3 input domains にわたる 1,235 slice discovery settings を構築し，Domino が ground truth coherent slices の 36% を同定したと報告する．これは既存手法から 12 percentage points の改善である．また，Domino は発見した slice の exact name を 35% の settings で生成できた．

## 問題設定

slice は，ある attribute / characteristic を共有する data examples の group と定義される．model がある slice で全体より低性能なら，systematic error が存在する．たとえば collapsed lung detection model が chest drain の有無に依存し，chest drain のない pneumothorax で false negative を起こす場合，この group は critical slice である．

high-dimensional inputs（images，audio，time-series，video）では，重要 slice は hidden であることが多い．raw input から簡単に抽出できず，metadata にも annotate されていない．このため，unstructured input data から semantically meaningful で underperforming な subgroup を mining する slice discovery が必要になる．

有用な SDM は2つの desiderata を満たす必要がある．

1. underperforming: model の error rate が高い examples を含む．
2. coherent: human-understandable concept によって united されている．

## 評価フレームワーク

既存の SDM evaluation は qualitative，synthetic，小規模な task / slice に限定されていた．著者らは，large-scale quantitative evaluation のため，slice discovery settings を programmatically generate する framework を作った．各 setting は以下からなる．

- labeled dataset `D = {(x_i, y_i)}`
- dataset 上で training された model `h_θ`
- model が degraded performance を示す coherent ground truth slice annotations `{s_i}`

SDM は validation set 上で fit され，test set に slicing functions を適用する．評価では，ground truth slice と discovered slice を比較する．主指標は precision-at-k で，discovered slice の top `k` elements のうち ground truth slice に属する割合を測る．この論文では `k = 10` を使う．

## Slice categories

著者らは underperforming slice の原因として3種類を扱う．

| Slice type | 内容 | 生成方法 |
| --- | --- | --- |
| rare slice | training set に少ない subclass で性能が落ちる | class label 内の subclass proportion を `0.01 < α < 0.1` にする |
| correlation slice | target と correlate が相関し，model が correlate に依存する | target variable と metadata label の correlation strength `α` を作る |
| noisy label slice | 特定 slice で label error rate が高い | slice 内だけ label noise を増やす |

appendix の overview では，trained slice discovery settings は Natural Images 984，MIMIC 221，EEG 30 で合計 1,235 である．synthetic settings は Natural Images 1,111，MIMIC 462，EEG 30 である．

## Domains

評価対象は3 domain である．

- Natural Images: CelebA と ImageNet．CelebA は 200k 以上の images と 40 labeled attributes，ImageNet は 1.2M images と 1000 classes を持つ．
- Medical Images: MIMIC-CXR．Beth Israel Deaconess Medical Center からの 377,110 chest x-rays で，14 conditions の annotations を持つ．
- Medical Time-Series: seizure onset prediction に使われる 12 second EEG signals dataset．

## Domino の手順

Domino は3段階で動く．

### 1. Embed

inputs `x_i` を cross-modal embedding space に encode する．cross-modal representation learning では，input examples と paired text descriptions を同じ latent space に埋め込む．これにより，semantic knowledge を含む input embeddings が得られる．

Domino は4種類の cross-modal embeddings を使う．

- CLIP: natural images 用．
- ConVIRT: medical images 用．
- MIMIC-CLIP: MIMIC-CXR 用に trained．
- EEG-CLIP: EEG reports と EEG readings のペアで trained．

### 2. Slice

cross-modal input embeddings，model predictions，true class labels を jointly model する error-aware mixture model を fit し，underperforming regions を見つける．mixture model は，slice membership `S` に条件づけて，embedding `Z`，label `Y`，prediction `Ŷ` がそれぞれ分布すると仮定する．

objective では `γ` が hyperparameter であり，coherence と under-performance の trade-off を調整する．label と prediction を一緒に model することで，false positives など error type に homogeneous な slices を見つけやすくする．

実装上は，mixture model は高 error concentration と正解 concentration の両方の slices を見つけるため，`k̄ > k̂` slices を model し，mistake concentration が高い top `k̂` slices を返す．appendix では `k̄ = 25` とし，top `k̂ = 5` を返すと説明される．

### 3. Describe

cross-modal text embedding を使って，発見した slice の natural language description を生成する．まず candidate phrase corpus `D_text` を用意し，各 phrase を text embedding に変換する．次に discovered slice の weighted average input embedding を prototype とし，most common class の prototype を差し引いて class effect を除く．最後に，distilled slice prototype と text embeddings の dot product が最大の phrase を description として返す．

## Cross-modal embeddings の効果

Natural Images では，synthetic models で CLIP embeddings の mean precision-at-10 は 0.570（95% CI: 0.554, 0.586）であり，BiT embeddings より 9 points，random activations より 23 points 高かった．trained models では CLIP と BiT の差はなかったが，どちらも trained classifier activations より mean precision-at-10 で約15 points 高かった．

Medical Images では，synthetic models で cross-modal ConVIRT embeddings が mean precision-at-10 0.765（95% CI: 0.747, 0.784）を達成し，best unimodal embeddings である BiT の 0.695（95% CI: 0.674, 0.716）を 7 points 上回った．trained models では，classifier activations は rare / noisy label slices で最も悪かったが，correlation slices では cross-modal embeddings と競合した．

Medical Time-Series では，EEG-report pairs で trained した CLIP-style cross-modal embedding が，synthetic models で mean precision-at-10 0.697（95% CI: 0.605, 0.784）を示し，unimodal embeddings の 0.532（95% CI: 0.459, 0.608）を 17 points 上回った．

## Error-aware mixture model の効果

cross-modal embeddings を固定し，slicing algorithm を比較した．比較対象は George，Multiaccuracy，Spotlight，ConfusionSDM である．

natural images の noisy / rare slices では，Domino の error-aware mixture model は mean precision-at-10 0.639（95% CI: 0.617, 0.660）を達成し，次点の George より 105% 高かった．一方，correlation slices では naive な ConfusionSDM baseline が error-aware mixture model を上回った．著者らは，correlation slice では confusion matrix cell による partition だけでも効果的な場合があると述べる．

## Natural language descriptions

Domino は identified slices に natural language description を生成できる最初の SDM とされる．natural images では，ground truth slice name または WordNet synonym が top-k descriptions に入る割合で評価した．

ground truth slice name を rank 1 に置いた割合は，rare slices 34.7%，correlation slices 41.0%，noisy label slices 39.0% だった．top 10 に入った割合は，rare 57.4%，correlation 55.4%，noisy label 48.7% だった．appendix では natural image，medical image，medical time-series の description examples が示される．

## 結論と注意点

Domino は cross-modal representations と error-aware mixture model を組み合わせた slice discovery method であり，既存 SDM より embedding / slicing step の性能が高く，semantic slice descriptions も生成できる．black-box access to models だけで使えるため，API access しかない状況でも model auditing に利用できる．

ただし，Domino がどれだけ有効でも捕捉できない failure modes は残る．著者らは，Domino のような model debugging tool が false sense of security を与える危険を指摘し，accurately-labeled representative test set での standard evaluation と併用する必要があると述べる．また，web 由来 image-text pairs で学習された embeddings は societal biases を反映する可能性があり，どの underrepresented groups / concepts の error mode を見逃すかを検討する必要がある．

## 関連概念

- [[DOMINO]]
- [[Algorithmic_Subgroup_Discovery]]
- [[Subgroup_Performance_Monitoring]]
- [[Hidden_Stratification]]
- [[Spurious_Correlation]]
- [[Worst_Group_Performance]]
