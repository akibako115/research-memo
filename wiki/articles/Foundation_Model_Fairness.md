---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_how_fair_are_medical_imaging_foundation_models]]"
  - "[[sources/2026-07-06_demographic_bias_vision_language_foundation_models_medical_imaging]]"
  - "[[sources/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization]]"
---

# Foundation Model Fairness

医療画像 foundation model は，downstream task の平均性能を上げる一方で，pre-training data に含まれる subgroup imbalance を広範囲の downstream models に持ち込む可能性がある．Foundation model fairness は，pre-training method，pre-training data，fine-tuning strategy が subgroup performance にどのような bias を残すかを評価する考え方である．

この概念が重要なのは，foundation model の bias は1つの task だけでなく，その representation を使う多くの task に転移しうるからである．fine-tuning dataset を balanced にしても pre-training stage で埋め込まれた bias が完全には消えない場合，pre-training 時点から fairness を設計・監査する必要がある．

## 評価対象

foundation model fairness では，downstream performance だけでなく，pre-training の条件を分けて評価する．

| 軸 | 例 | 見ること |
| --- | --- | --- |
| pre-training data | natural images vs medical images | domain-specific pre-training が fairness を改善するか悪化するか |
| pre-training method | masked SSL，contrastive SSL，supervised | subgroup imbalance への感度 |
| architecture | ViT，ResNet | representation bias の違い |
| fine-tuning strategy | end-to-end，linear probing，balanced fine-tuning | pre-training bias が downstream で残るか |

Khan et al. は，MAE，Medical MAE，MoCov3，Medical MoCov3，BiT，REMEDIS を CheXpert の multi-label classification に fine-tune し，sex と race の fairness gap を比較した．Yang et al. は，CheXzero のような medical [[Vision_Language_Model_Fairness|vision-language foundation model]] を，MIMIC，CheXpert，NIH，PadChest，VinDr で評価した．この設定では，モデルは pathology labels ではなく radiographs と clinical texts から self-supervised に学習し，zero-shot に広い radiographic findings を診断する．

## Medical pre-training の trade-off

医療画像で pre-training すると，Chest X-ray classification の AUC は上がりやすい．しかし Khan et al. では，medical image pre-trained models は natural image pre-trained models より subgroup fairness が一貫して悪かった．race fairness では scratch baseline より悪くなる場合もあった．

```text
medical image pre-training:
  overall AUC ↑
  subgroup fairness ↓

natural image pre-training:
  overall AUC はやや低い
  subgroup fairness は高い
```

この結果は，domain-specific representation が必ず公平になるわけではないことを示す．medical pre-training dataset が skewed な demographic distribution を持つ場合，foundation model は majority subgroup に有利な representation を学ぶ可能性がある．

## SSL method による違い

masked SSL と contrastive SSL では，fairness への影響が pre-training data によって変わる．natural images で pre-training した場合は masked SSL がより fair だったが，medical images で pre-training した場合は contrastive SSL がより fair だった．

| 条件 | 傾向 |
| --- | --- |
| natural image pre-training | masked SSL が sex/race fairness で有利 |
| medical image pre-training | contrastive SSL が fairness で有利 |
| medical masked SSL | race imbalance に弱く，scratch baseline より悪い場合がある |

著者らは，contrastive SSL が各 image を separate class のように扱い，同じ subgroup 内の画像とも contrast するため，skewed racial split の影響を受けにくい可能性を挙げている．

## Pre-training data を増やす効果

medical pre-training の量を増やすと，overall AUC と subgroup fairness の両方が改善する傾向がある．ChestXray14，CheXpert，両者の組み合わせで MAE を pre-train した実験では，combined pre-training が最も高い AUC と低い fairness gap を示した．

これは，[[Demographic_Imbalance]] に対して，単に balanced sampling するだけでなく，多施設・多 dataset の data diversity を増やすことが fairness 改善につながる可能性を示す．ただし，dataset を増やしても各 subgroup の label quality や disease prevalence が偏っていれば，bias は残りうる．

## Balanced fine-tuning の限界

balanced fine-tuning は fairness を改善するが，pre-training bias を完全には消せない．Khan et al. は race subgroups が同数になるように fine-tuning training set を resample し，racial fairness の改善を確認した．しかし balanced fine-tuning 後も，natural image pre-trained models は多くの場合 medical image pre-trained models より fair だった．

```text
pre-training bias
  -> foundation representation に入る
  -> balanced fine-tuning で一部改善
  -> しかし完全には消えない
```

したがって，foundation model fairness では fine-tuning dataset の fairness だけを見ても不十分である．pre-training data composition，pre-training objective，training epochs，dataset diversity まで記録・評価する必要がある．

## Subgroup-level audit

foundation model は aggregate fairness gap だけでなく，どの subgroup を favor するかまで見る必要がある．Khan et al. では，すべての foundation models が female patients で一貫して underperform した．race では，medical image pre-trained models が frequent subgroups，White と Asian，を favor し，natural image pre-trained models は minority subgroup，Black，で performance が上がる傾向があった．

この audit は [[Subgroup_Performance_Monitoring]] と同じ構造を持つが，foundation model では pre-training stage と downstream stage を分けて考える点が重要である．

## Vision-language foundation models

vision-language foundation model では，explicit pathology labels を使わないことが fairness を保証するわけではない．Yang et al. は，CheXzero が CheXpert 上で Enlarged Cardiomediastinum，Pleural Effusion，Lung Opacity に expert-level の AUROC を示す一方で，sex，age，race，intersectional subgroup の underdiagnosis disparity が radiologists より大きいことを示した．

VLM では，画像 embedding が demographic attributes を強く encode する点も重要である．CheXzero の frozen penultimate-layer embedding から，female AUC 0.92，18-40 歳 AUC 0.94，Black AUC 0.78，Black female AUC 0.83 で attribute prediction ができた．これは，[[Race_Recognition_In_Medical_Images]] と同様に，protected attribute を入力から除くだけでは foundation model fairness を保証できないことを示す．

VLM 特有の追加監査対象は text prompt である．demographic details を prompt に入れると一部 condition の fairness gap は減るが，Pneumonia のように改善しない場合もある．したがって，foundation model fairness では pre-training data / objective だけでなく，prompt template と zero-shot finding ごとの subgroup error も記録する必要がある．

## Distribution shift

foundation model や pre-trained representation の fairness は，ID validation だけでは評価しきれない．Yang et al. は，medical imaging models で demographic shortcut removal が ID fairness を改善しても，OOD fairness には一貫して転移しないことを示した．特に，ID data で fairness gap が小さい model より，representation に含まれる demographic information が少ない model の方が OOD fairness で良い場合がある．

したがって，foundation model fairness では，downstream fine-tuning 後の AUC / fairness gap だけでなく，representation-level attribute prediction，external validation，post-deployment monitoring を含める必要がある．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| foundation model fairness | foundation model の pre-training / fine-tuning が subgroup performance に与える影響 |
| fairness gap | best subgroup と worst subgroup の AUC 差 |
| medical pre-training | medical images を使った domain-specific pre-training |
| natural pre-training | ImageNet など natural images を使った pre-training |
| balanced fine-tuning | downstream training set を protected subgroup で balancing すること |
| pre-training bias | pre-training data / objective 由来で representation に残る bias |
| demographic encoding | foundation representation から sex，age，race などが予測できること |
| prompt-based intervention | VLM の text prompt に demographic information を入れて model behavior を変える介入 |
| OOD fairness | external domain でも subgroup fairness が保たれること |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Demographic_Imbalance]]
- [[Race_Recognition_In_Medical_Images]]
- [[Subgroup_Performance_Monitoring]]
- [[Worst_Group_Performance]]
- [[Vision_Language_Model_Fairness]]
- [[Fairness_Under_Distribution_Shift]]
