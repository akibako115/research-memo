---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_linear_conditioning_metadata_image_segmentation]]"
---

# Metadata Conditioning

医療画像には，画像そのもの以外に，撮像装置，acquisition parameters，施設，疾患 subtype，患者属性，rater 情報などの metadata が付いていることが多い．Metadata conditioning は，この補助情報を単なる後段の特徴結合ではなく，画像モデルの中間処理を変える条件として使う設計である．

この概念が重要なのは，metadata が segmentation や classification の「何をどう見るべきか」を変える prior knowledge になりうるからである．たとえば tumor type が分かれば，典型的な size，location，contrast pattern を前提に segmentation できる．また，segmentation task label を metadata として入れれば，missing labels を持つ複数 dataset から1つの multi-task model を学習できる．

## 何を条件にするか

metadata は，患者情報だけでなく，画像や annotation の文脈も含む．

| Metadata | 例 | 使い道 |
| --- | --- | --- |
| patient metadata | age，sex，disease type，severity | 疾患形態や prevalence の prior |
| acquisition metadata | scanner vendor，center，echo-time，flip angle | domain shift / sequence 差の補正 |
| task metadata | organ label，target class | multi-task segmentation の task指定 |
| annotation metadata | rater id，rater experience | inter-rater variability の modeling |

metadata が画像にすでに encode されている場合，追加しても効果が小さいことがある．逆に，画像だけでは明示しにくい prior なら，conditioning によって性能や data efficiency が上がる．

## FiLM による実装

Lemay et al. は，2D U-Net に [[FiLM]] layers を入れ，one-hot encoded metadata から channel-wise `gamma` と `beta` を生成した．

```text
metadata
  -> FiLM generator
  -> gamma, beta
  -> gamma * feature_map + beta
```

この方法は image resolution に依存せず低コストであり，各 convolutional unit 後に FiLM layer を置ける．`gamma` は feature を suppress / pass し，`beta` は activation を shift するため，metadata が画像特徴抽出の途中に作用する．

## Segmentation で効く理由

segmentation は，対象構造の形状，場所，contrast，annotation policy に強く依存する．metadata conditioning は，これらの prior を model に渡すことで，画像から曖昧に推定する負担を減らす．

| 課題 | metadata conditioning の効果 |
| --- | --- |
| subtype ごとに形態が違う | subtype に応じて feature maps を変調する |
| missing labels がある | どの class label が提示されているかを model に教える |
| multi-task segmentation | task label で1つの U-Net を複数 task に切り替える |
| small dataset | 他 task の画像から shared weights を学べる |

spinal cord tumor segmentation では，tumor type を FiLM に入れることで all tumors の Dice が 54.0 から 59.1 に上がった．multi-organ segmentation では，FiLMed U-Net が missing-label setting でも single-class U-Net と同等の Dice に到達した．

## Fairness との関係

metadata conditioning は [[Image_Tabular_Fusion]] と同じく，患者属性や施設情報を model に入れる設計である．これは性能や robustness を上げる可能性がある一方，protected attribute への依存や shortcut を強める可能性もある．

したがって，metadata conditioning を医療画像 fairness に使う場合は，次を確認する必要がある．

| 確認点 | 理由 |
| --- | --- |
| metadata の意味 | biomarker，protected attribute，site artifact を混同しない |
| subgroup performance | conditioning が subgroup gap を広げないか |
| OOD generalization | facility / scanner が変わっても効果が残るか |
| ablation | metadata を抜いたときに性能と fairness がどう変わるか |
| parameter analysis | FiLM `gamma` / `beta` が subgroup shortcut を作っていないか |

この点で，[[FairREAD]] は metadata conditioning を fairness-aware に使う発展例である．画像内の demographic signal を一度 disentangle し，明示的な demographic attributes を controlled に re-fusion する．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| metadata conditioning | metadata によって画像モデルの処理を条件付けること |
| task metadata | どの class / organ を segment するかを示す metadata |
| FiLMed U-Net | FiLM layers を U-Net に入れた segmentation model |
| missing-label segmentation | 全 class が全 image に annotation されていない segmentation 設定 |
| task adaptation | metadata によって1つの model を複数 task に切り替えること |

## 関連概念

- [[FiLM]]
- [[Image_Tabular_Fusion]]
- [[FairREAD]]
- [[Conditional_Modulation]]
- [[Medical_Image_Fairness_Evaluation]]
