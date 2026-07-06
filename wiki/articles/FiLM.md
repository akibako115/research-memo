---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_film_visual_reasoning_general_conditioning_layer]]"
  - "[[sources/2026-07-06_linear_conditioning_metadata_image_segmentation]]"
---

# FiLM

画像とテーブルデータ，画像と言語，患者属性と医療画像のように，片方の情報で別のネットワークの処理を変えたい場面では，単純な特徴結合だけだと条件情報の使われ方が見えにくい．FiLM はこの問題に対して，条件情報から feature map ごとの scale と shift を生成し，中間特徴を直接変調する方法である．

FiLM があると，条件情報を「入力に足す」のではなく，「特徴抽出器のどの channel を強め，弱め，反転し，通すかを決める信号」として扱える．そのため，[[Image_Tabular_Fusion]] や患者属性条件付きモデルでは，late fusion よりも早い段階で条件を画像特徴抽出に作用させる設計として使える．

## 基本形

FiLM は Feature-wise Linear Modulation の略である．条件入力 `x_i` から feature channel ごとの `γ` と `β` を生成し，中間特徴 `F_{i,c}` に affine transformation を適用する．

```text
γ_{i,c} = f_c(x_i)
β_{i,c} = h_c(x_i)
F'_{i,c} = γ_{i,c} F_{i,c} + β_{i,c}
```

CNN では `c` は feature map / channel に対応する．つまり，FiLM は空間位置ごとに別々の係数を持つのではなく，channel 単位で特徴マップ全体を変調する．このため，画像解像度が上がっても FiLM parameter の数は増えにくい．

## どこで条件が効くか

| 手法 | 条件が作用する場所 | 何を変えるか |
| --- | --- | --- |
| early concatenation | 入力 | 入力 channel / token |
| late fusion | classifier 前 | 最終表現 |
| conditional bias | activation | channel ごとの shift |
| feature-wise gating | activation | channel ごとの scale |
| FiLM | activation | channel ごとの scale と shift |
| [[Hypernetwork]] | parameter | weight / adapter / modulation parameter |

FiLM は [[Hypernetwork]] の一種として見ることもできる．ただし，生成するのは巨大な convolution kernel 全体ではなく，各 channel の `γ` と `β` だけである．このため，hypernetwork 的な条件付き計算を軽量に実装できる．

## FiLM の効き方

FiLM の `γ` は feature map を増幅，抑制，反転，zero-out できる．`β` は feature map を shift し，後続に ReLU がある場合には，どの activation が downstream に通るかを変えられる．

```text
condition
   |
   v
FiLM generator
   |
   +--> γ: feature map を scale / negate / suppress
   |
   +--> β: feature map を shift / threshold
   |
   v
FiLM-ed network
```

FiLM 論文の CLEVR 解析では，`γ` が 0 付近に集中する peak を持ち，feature map 全体を shut off する挙動が観察された．また `γ` の一部は負になり，ReLU と組み合わさることで downstream に渡る activation の集合を変える．この性質が，単なる 0-1 gating よりも強い条件付き変調を可能にする．

## 医療画像 + 患者属性での意味

患者属性を画像分類に使う場合，late fusion では「画像特徴を抽出した後」に属性を足す．FiLM を使うと，属性が画像特徴抽出の途中に入り，特定の channel を条件付きで強めたり弱めたりできる．

たとえば胸部 X 線分類で，年齢，性別，撮像ビュー，装置，施設などを FiLM generator に入れると，CNN backbone の各 block に属性条件付きの `γ` / `β` を与えられる．これは，属性ごとに完全に別モデルを持つより軽く，単純結合よりも条件の作用点が明確である．

ただし，protected attribute を FiLM に入れる場合，性能改善が疾患特徴の補正なのか，shortcut の強化なのかを区別する必要がある．FiLM は channel を選択的に抑制・増幅できるため，subgroup ごとの予測規則を強く分ける可能性がある．したがって，[[Subgroup_Reliability]] や [[Fairness_Evaluation]] と組み合わせて検証する必要がある．

## 設計思想

FiLM の設計上の強みは，条件付き計算の表現力と実装コストのバランスにある．

| 判断 | 理由 |
| --- | --- |
| channel-wise にする | spatial resolution に依存せず軽量にできる |
| scale と shift の両方を持つ | gating だけ，bias だけより表現力が高い |
| `γ` の値域を制限しない | feature map の大きな増幅，反転，zero-out が可能 |
| normalization 直後に限定しない | Conditional Normalization より広い場所に適用できる |
| 複数 block に繰り返し入れる | 条件付き reasoning / feature extraction を階層的に行える |

FiLM 論文では，normalization 直後でなくても性能が保たれることが示されている．そのため，FiLM の本質は normalization ではなく，条件情報に基づく feature-wise affine modulation にある．

## Segmentation への拡張

FiLM は classification / visual reasoning だけでなく，U-Net 型 segmentation にも使える．Lemay et al. は，2D U-Net の各 convolutional unit 後に FiLM layer を置き，one-hot encoded metadata から channel-wise `γ` / `β` を生成した．

spinal cord tumor segmentation では，tumor type を metadata として FiLM generator に入れることで，all tumors の Dice score が 54.0 から 59.1 に改善した．また multi-organ segmentation では，organ label を task metadata として入れることで，missing labels を持つ dataset から1つの FiLMed U-Net を学習できた．

この結果は，FiLM が単に「属性を足す」方法ではなく，どの target を segment するか，どの subtype prior を使うかを network 内で切り替える [[Metadata_Conditioning]] の基礎部品であることを示す．

## 具体例で理解する

**Step 1 — 条件を選ぶ**

画像と言語の visual reasoning では質問文を条件にする．医療画像では患者属性，撮像条件，施設 ID，EHR summary などを条件にできる．

**Step 2 — FiLM generator で `γ` と `β` を作る**

条件を MLP，GRU，Transformer などで embedding に変換し，各 FiLM layer の channel 数に合わせて `γ` と `β` を出力する．

**Step 3 — CNN block の中間特徴を変調する**

畳み込みや normalization の後の activation に対して，channel ごとに `γ F + β` を適用する．

**Step 4 — subgroup ごとの挙動を見る**

属性条件付き医療画像モデルでは，平均 AUROC だけでなく，subgroup AUROC，calibration，worst-group performance，FiLM parameter の subgroup 差を確認する．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| FiLM generator | 条件入力から `γ` と `β` を生成するネットワーク |
| FiLM-ed network | FiLM layer によって中間特徴を変調されるネットワーク |
| `γ` | feature-wise scale．抑制，増幅，反転，zero-out に関わる |
| `β` | feature-wise shift．ReLU などと組み合わさり threshold を変える |
| Conditional Normalization | normalization layer の affine parameter を条件付きにする手法群 |
| feature-wise affine modulation | channel ごとの scale と shift による条件付き変調 |

## 関連概念

- [[Hypernetwork]]
- [[Conditional_Modulation]]
- [[Image_Tabular_Fusion]]
- [[Metadata_Conditioning]]
- [[Subgroup_Reliability]]
- [[Fairness_Evaluation]]
