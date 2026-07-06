---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_hyperfusion_hypernetwork_multimodal_tabular_medical_imaging]]"
---

# HyperFusion

画像と表形式データを統合するとき，late fusion や FiLM / DAFT 型の feature modulation では，条件情報が影響できる範囲が比較的限られる．HyperFusion はこの問題に対して，表形式データから画像処理ネットワークの一部パラメータそのものを生成し，患者ごとに画像モデルを動的に調整する方法である．

これがあると，患者の EHR や臨床属性を「分類器に足す特徴」ではなく，画像をどう読むかを決める prior として扱える．[[Hypernetwork]] を [[Image_Tabular_Fusion]] に使う具体例であり，条件付きモデルの自由度を FiLM / DAFT より強めた設計として位置づけられる．

## 基本構造

HyperFusion は2つの network からなる．

| 要素 | 役割 |
| --- | --- |
| hypernetwork `H_φ` | tabular vector `T` を受け取り，primary network の一部 weights / biases を生成する |
| primary network `P_θ` | medical image `I` を受け取り，診断や回帰などの task prediction を行う |

primary network の parameter は2種類に分かれる．

```text
θ = {θ_H, θ_P}
```

`θ_H` は hypernetwork が tabular input ごとに生成する external parameters であり，`θ_P` は通常の学習で更新される internal parameters である．この分離により，network 全体を患者属性ごとに完全に分けるのではなく，一部の layer だけを tabular-conditioned にできる．

## FiLM / DAFT との違い

| 手法 | 生成するもの | 条件入力 | 作用点 | 自由度 |
| --- | --- | --- | --- | --- |
| [[FiLM]] | channel-wise `γ, β` | condition | activation | 軽い |
| DAFT | channel-wise `α, β` | image feature + tabular | activation | 中程度 |
| HyperFusion | layer weights / biases | tabular | parameter | 高い |

FiLM や DAFT は activation を affine transform する．HyperFusion は，primary network の layer parameter そのものを生成する．そのため，条件情報が計算規則に与える影響は大きいが，どの layer を hyperlayer にするか，どの程度の parameter を external にするかが重要な設計判断になる．

## Hyperlayer を選ぶ理由

すべての layer を hypernetwork で生成すれば，tabular data への依存は最大になる．しかし，それは tabular attribute の組み合わせごとに別 network を持つ状況に近づき，必要なデータ量や学習難度が増える．逆に，すべての layer を internal にすれば，通常の image-only model と同じで tabular data は効かない．

HyperFusion では，low-level image features は tabular attributes と関係しにくいという仮定から，初期層は internal に残し，後段の layer を hyperlayer にする．brain age prediction では final four linear layers，AD classification では last ResNet block 内の convolutional layer が hypernetwork から parameter を受け取る．

## 医療画像での意味

HyperFusion は，「患者属性や EHR を使って画像モデルの読み方を変える」設計である．たとえば AD classification では，年齢，性別，教育歴，CSF biomarkers，PET-derived summary が，hippocampus MRI を処理する primary network の一部 parameter を変える．

```text
EHR / tabular data
        |
        v
  hypernetwork
        |
        v
generated weights for selected image layers
        |
        v
MRI -> primary image network -> prediction
```

この構造は，医師が患者背景を知ったうえで画像を読む状況に近い．ただし，protected attribute を parameter generation に使う場合，モデルが subgroup-specific rule を強く学習する可能性があるため，fairness 評価が重要になる．

## 設計上の注意

HyperFusion では，tabular embedding が重要になる．tabular vector は MLP で低次元の latent vector に埋め込まれ，そこから weights と biases が生成される．one-hot の sex attribute のように離散的で直交した入力でも，embedding を通すことで連続的な parameter space に写像できる．

missing value の扱いにも注意が必要である．HyperFusion 論文では iterative imputation と missingness indicator を使うが，missingness 自体が class-specific な cue になりうることを明示している．医療データでは，CN subject には侵襲的検査が欠測しやすいなど，欠測が疾患ラベルや施設運用と結びつく場合がある．

## Fairness 研究でのリスク

HyperFusion は FiLM より強い条件付き専門化を許す．そのため，患者属性を入れると subgroup reliability を改善する可能性がある一方，attribute shortcut や subgroup overfitting のリスクも大きい．

検証では少なくとも以下を見る必要がある．

| 観点 | 確認すること |
| --- | --- |
| subgroup performance | 属性群・交差属性群ごとの性能 |
| worst-group performance | 最悪群が改善するか |
| external validation | 施設・dataset が変わっても効果が残るか |
| generated parameter analysis | 属性によって生成重みがどの程度変わるか |
| missingness leakage | 欠測 indicator が診断ラベルや subgroup proxy になっていないか |
| ablation | protected attribute を外したときの性能・公平性変化 |

## リファレンス

| 用語 | 意味 |
| --- | --- |
| hypernetwork | 別 network の parameter を生成する network |
| primary network | 実際に画像を処理して予測する network |
| external parameter | hypernetwork が tabular input に応じて生成する primary network parameter |
| internal parameter | 通常の backpropagation で直接学習される primary network parameter |
| hyperlayer | parameter が hypernetwork から供給される primary network layer |
| tabular embedding | EHR / tabular vector を parameter generation 用の latent vector に変換する処理 |

## 関連概念

- [[Hypernetwork]]
- [[Image_Tabular_Fusion]]
- [[FiLM]]
- [[Conditional_Modulation]]
- [[Fairness_Evaluation]]
