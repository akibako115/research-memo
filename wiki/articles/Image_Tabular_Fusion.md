---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_daft_interweave_tabular_data_3d_images_cnns]]"
  - "[[sources/2026-07-06_hyperfusion_hypernetwork_multimodal_tabular_medical_imaging]]"
  - "[[sources/2026-07-06_fairread_demographic_refusion_medical_image_classification]]"
  - "[[sources/2026-07-06_linear_conditioning_metadata_image_segmentation]]"
---

# Image Tabular Fusion

医療画像分類では，画像だけでは疾患状態の一部しか見えないことがある．一方で，年齢，性別，検査値，遺伝子，施設，撮像条件などの表形式データは低次元だが臨床的に濃い情報を持つ．Image tabular fusion は，この2種類の情報を同じ予測モデルの中でどう相互作用させるかという設計問題である．

単純に画像特徴と表形式特徴を最後に結合すると，実装は簡単だが，表形式データが画像特徴抽出の途中に影響できない．DAFT 論文の問題意識はここにある．画像特徴と表形式特徴には相補性だけでなく冗長性もあるため，表形式データが画像特徴を文脈づけ，画像特徴も表形式データの使い方に影響するような統合が必要になる．

## 融合方式の全体像

| 方式 | 統合位置 | 相互作用 | 利点 | 弱点 |
| --- | --- | --- | --- | --- |
| two-stage | CNN 後，別モデル | ほぼなし | 実装が簡単 | CNN が tabular と冗長な特徴を学ぶ可能性 |
| late concatenation | classifier 前 | global descriptor レベル | 標準的で安定 | voxel / patch level の相互作用がない |
| MLP after concatenation | classifier 前 | 非線形 | late fusion より表現力が高い | parameter 増加と overfitting |
| tabular-conditioned scaling | convolution feature | tabular → image | channel を条件付きで強弱できる | one-way flow |
| [[FiLM]] | convolution feature | condition → image | scale と shift で軽量に変調 | condition 側に image context がない場合がある |
| DAFT | convolution feature | image + tabular → image | image と tabular の bidirectional な統合を意図 | block 位置や解析が設計課題 |
| [[HyperFusion]] | selected layer parameter | tabular → image network parameter | 患者ごとに画像モデルの重みを動的に変えられる | 条件付き専門化と fairness risk が大きい |
| [[FairREAD]] | latent representation | demographic attributes → fair image representation | shortcut を除いた後に属性を controlled に再注入できる | 属性利用可能性と subgroup threshold に依存する |
| [[Metadata_Conditioning]] | segmentation feature map | metadata / task label → image feature | subtype prior や task 指定を network 内に入れられる | metadata encoding と missingness の設計が必要 |

この表の中心的な違いは，表形式データを「最後に分類器へ足す」のか，「画像特徴抽出の途中で使う」のかである．後者は条件付きモデルに近く，[[Conditional_Modulation]] や [[Hypernetwork]] と接続する．

## なぜ late concatenation だけでは足りないのか

late concatenation では，CNN が画像から global descriptor を作った後に tabular vector を結合する．この設計では，画像特徴抽出器は tabular data を知らないまま学習される．

その結果，次のような問題が起きる．

| 問題 | 内容 |
| --- | --- |
| 冗長特徴 | CNN が年齢や性別など，tabular に既にある情報を画像から推定しようとする |
| 相互作用不足 | tabular feature が特定の image channel / region の解釈を変えられない |
| global 限定 | tabular と image の相互作用が最終表現だけに閉じる |
| 不安定な非線形化 | concatenation 後に MLP を増やすと overfitting しやすい |

DAFT 論文では，AD diagnosis において tabular-only linear model が image-only ResNet を上回った．これは，CSF biomarkers や PET-derived summary のような tabular data が MRI より早期に異常を示す場合があるためである．このような状況では，画像モデルが tabular biomarker と冗長な情報を学ぶだけでは不十分で，両者の役割分担を設計する必要がある．

## Channel-level feature merging

画像と表形式データを CNN 内で統合する代表的な方法は，feature map の channel を条件付きで変調することである．

```text
image -> CNN feature map F
tabular / metadata -> conditioning vector
conditioning vector -> scale / shift
F' = scale * F + shift
```

この設計では，tabular data が feature map のどの channel を強めるか，弱めるか，shift するかを決める．[[FiLM]] はこの考え方の基本形であり，DAFT はさらに image feature map 自体も conditioning network に入力する．

## DAFT が加える観点

DAFT は tabular data だけから `α` / `β` を作るのではなく，global average pooling した image feature と tabular data を結合して auxiliary network に入れる．つまり，scale / shift は患者の表形式情報だけでなく，その患者の画像特徴にも依存する．

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

この構造の狙いは，tabular data が image feature を一方的に変調するだけでなく，image context に応じて tabular data の使い方も変わるようにすることである．DAFT 論文ではこれを image と tabular information の two-way exchange と呼んでいる．

## Hypernetwork で重みを生成する

[[HyperFusion]] は，activation の scale / shift ではなく，primary image network の一部 layer parameter を tabular data から生成する．この設計では，患者の EHR や臨床属性が，画像特徴の通し方だけでなく，画像処理 layer の計算規則そのものを変える．

FiLM / DAFT が channel-level modulation であるのに対し，HyperFusion は parameter-level conditioning である．その分，条件付き専門化の自由度は大きいが，protected attribute や missingness indicator を入れる場合には，subgroup-specific shortcut を学習しないかをより慎重に検証する必要がある．

## Fairness-aware re-fusion

[[FairREAD]] は，fairness-aware な image-tabular fusion として読める．まず image representation から demographic signal を除き，その後 age，race，gender などの attributes を latent-space rescaling として再注入する．

この設計では，protected attributes を隠すのではなく，画像内に潜む uncontrolled shortcut と，明示的に使う clinical context を分けて扱う．したがって，FairREAD は DAFT / FiLM のような feature modulation と，fair representation learning を組み合わせた fusion 手法である．

[[Metadata_Conditioning]] は，segmentation における fusion の具体例である．tumor type，organ label，scanner vendor，acquisition parameters などを FiLM generator に入れ，U-Net の feature maps を条件付きで変調する．classification だけでなく segmentation でも，metadata は「最後に足す情報」ではなく，画像特徴抽出の途中で使う prior になる．

## 医療画像 fairness での注意点

患者属性を fusion に使う場合，性能改善と公平性改善は同じではない．年齢や性別などの属性を使うと subgroup performance が上がることもあるが，protected attribute への依存が強くなり，shortcut や group-specific overfitting を起こすこともある．

特に channel-level modulation では，属性ごとに image feature の通し方が変わる．そのため，次の検証が必要になる．

| 検証 | 見ること |
| --- | --- |
| subgroup performance | 属性群ごとの AUROC / sensitivity / specificity |
| worst-group performance | 平均改善ではなく最悪群が改善するか |
| calibration | 属性群ごとの予測確率がずれていないか |
| external generalization | 施設や dataset が変わっても改善が残るか |
| parameter / modulation analysis | `α` / `β` や adapter weight が subgroup ごとに過度に分離していないか |
| ablation | protected attribute を抜いたときに性能と fairness がどう変わるか |

DAFT 論文自体は AD prediction の性能評価が中心であり，fairness 指標を主題にはしていない．ただし，患者属性条件付きモデルを医療画像 fairness に使う場合，DAFT のような構成は「属性がどの channel に効いているか」を解析しやすい候補になる．

## 設計手順

**Step 1 — Tabular data の意味を分ける**

tabular data が疾患 biomarker なのか，患者属性なのか，撮像条件なのか，施設情報なのかを分ける．疾患 biomarker と protected attribute では，モデルに入れる意味とリスクが異なる．

**Step 2 — Fusion の位置を決める**

baseline として late concatenation を置き，必要に応じて CNN block 内の FiLM / DAFT 型 modulation を試す．初期層は primitive feature を扱うため，臨床 tabular data は late convolutional block に入れる方が解釈しやすい．

**Step 3 — One-way か two-way かを決める**

tabular data が画像内容を直接文脈づけるなら FiLM 型の one-way conditioning で足りる場合がある．画像特徴と tabular feature の冗長性や相互依存を扱いたいなら，DAFT のように image feature も conditioning network に入れる設計を検討する．

**Step 4 — 平均性能以外を見る**

balanced accuracy，macro-F1，c-index などの task metric に加えて，subgroup metric，calibration，外部データセット generalization を見る．fusion は平均性能を上げても subgroup gap を広げる可能性がある．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| image descriptor | CNN が画像から抽出した latent representation |
| tabular data | demographics，biomarkers，clinical variables，metadata などの低次元構造化情報 |
| late fusion | classifier 直前で image descriptor と tabular vector を結合する方式 |
| channel-level modulation | feature map channel ごとに scale / shift / gate を適用する方式 |
| FiLM | condition から feature-wise scale と shift を生成する layer |
| DAFT | image feature と tabular data の両方から scale / shift を生成する 3D CNN module |
| HyperFusion | tabular data から selected image-network layer の weights / biases を生成する hypernetwork fusion |
| two-way exchange | image と tabular の片方向条件づけではなく，両者を使って変調を決める考え方 |

## 関連概念

- [[FiLM]]
- [[HyperFusion]]
- [[FairREAD]]
- [[Metadata_Conditioning]]
- [[Hypernetwork]]
- [[Conditional_Modulation]]
- [[Subgroup_Reliability]]
- [[Fairness_Evaluation]]
