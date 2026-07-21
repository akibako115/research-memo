---
created: 2026-07-06
updated: 2026-07-21
sources:
  - "[[sources/2026-07-06_underdiagnosis_bias_chest_radiographs]]"
  - "[[sources/2026-07-06_demographic_bias_vision_language_foundation_models_medical_imaging]]"
  - "[[sources/2026-07-21_subgroup_separability_group_fair_medical_image_classification]]"
---

# Underdiagnosis Bias

医療画像 AI の平均 AUC が高くても，疾患を持つ特定の患者群を「異常なし」と判定しやすいなら，そのモデルは診断支援として危険である．Underdiagnosis bias は，患者に疾患があるにもかかわらず，モデルが健康または `no finding` と予測する誤りが subgroup 間で偏る現象である．

この概念が重要なのは，underdiagnosis が triage や診断支援で access to care を遅らせるからである．overdiagnosis では追加検査や医師判断に進む可能性が残るが，underdiagnosis では患者が低優先度に回され，治療機会を失いやすい．そのため，医療画像 fairness では，AUC gap だけでなく subgroup ごとの false negative / `no finding` false positive を見る必要がある．

## 何を測る概念か

胸部 X 線の multi-label classification では，モデルが複数疾患ラベルと `no finding` label を出すことがある．Seyyed-Kalantari et al. は，`no finding` の false positive を underdiagnosis として測った．

```text
患者は疾患あり
  ↓
モデルは no finding と予測
  ↓
underdiagnosis
```

このとき subgroup ごとの underdiagnosis rate は，`no finding` label の false positive rate として表せる．

| 観点 | 測るもの | 意味 |
| --- | --- | --- |
| underdiagnosis rate | `no finding` FPR | 疾患ありを「異常なし」とする率 |
| overdiagnosis rate | `no finding` FNR | 疾患なしを「異常あり」とする方向の率 |
| FDR of `no finding` | `no finding` 予測時に実際は疾患ありの確率 | no finding prediction の危険度 |
| intersectional rate | 複数属性の組み合わせでの FPR | bias が重なる subgroup の検出 |

## なぜ AUC だけでは不十分か

AUC は threshold に依存しない discrimination を測るが，臨床では最終的に binarized decision が使われることが多い．同じ AUC でも，threshold，calibration，prevalence，subgroup distribution によって，実際に「見逃される患者」の分布は変わる．

Underdiagnosis bias を見るには，次のように aggregate performance と subgroup-specific threshold outcome を分けて考える．

| 評価 | 見えるもの | 見えにくいもの |
| --- | --- | --- |
| overall AUC | 全体として疾患を順位付けできるか | どの患者群を見逃すか |
| subgroup AUC gap | subgroup 間の discrimination 差 | 臨床運用 threshold での見逃し |
| `no finding` FPR by subgroup | 疾患ありを健康扱いする偏り | threshold choice に依存する |
| intersectional FPR | 複数属性で重なる underdiagnosis | sample size が小さいと不安定 |

したがって，[[Medical_Image_Fairness_Evaluation]] では，overall AUC，worst-case AUC，FPR/FNR，calibration を同時に報告する必要がある．

## Selective error と random noise を区別する

Underdiagnosis bias は，単に「ある subgroup でモデルが全体的に悪い」という話ではない．重要なのは，誤りの向きが「健康扱い」に偏っているかである．

```text
random noise:
  no finding FPR ↑ and no finding FNR ↑

selective underdiagnosis:
  no finding FPR ↑ and no finding FNR ↓ or not ↑
```

Seyyed-Kalantari et al. は，under-served subgroup で `no finding` FPR が高く，`no finding` FNR とは inverse relationship を示すことを確認した．これは，単なる noisy subgroup ではなく，モデルが特定 subgroup を選択的に「no finding」へ寄せている可能性を示す．

Yang et al. も vision-language foundation model の評価で，MIMIC の `No Finding` prediction に同じ構造を使った．CheXzero では，female patients，18-40 歳の younger patients，Black patients で underdiagnosis rate が高く，Black female patients のような intersectional subgroup で bias が強くなった．これは，[[Vision_Language_Model_Fairness]] でも underdiagnosis を中心指標に置く必要があることを示す．

## Intersectional subgroup で強くなる

underdiagnosis は，単一属性だけでなく intersectional subgroup で強くなることがある．たとえば，胸部 X 線モデルでは，female patients や younger patients だけでなく，Hispanic female patients，0-20 years and Black，0-20 years and Medicaid insurance のような組み合わせで underdiagnosis rate が高くなった．

これは，fairness 評価を sex，age，race などの単独軸だけで行うと，最も危険な subgroup を見落とす可能性があることを意味する．ただし，intersectional subgroup は sample size が小さくなりやすいため，confidence interval と subgroup size を併記する必要がある．

## Bias amplification として見る

医療画像 dataset の labels は，clinical records や radiology reports から作られることが多い．もし既存医療で underserved subpopulations が underdiagnosed されていれば，その記録を使った model は，既存の underdiagnosis pattern を学習する可能性がある．

さらに，automatic labeler が radiology report から label を作る場合，NLP labeler 自体の subgroup bias も入り込む．このため，underdiagnosis bias は dataset collection，clinical documentation，automatic labeling，model training の各段階で増幅されうる．

```text
clinical underdiagnosis
  -> biased report / label
  -> model learns biased label pattern
  -> deployment amplifies delayed care
```

この見方は [[Hidden_Stratification]] ともつながる．metadata 上の protected subgroup だけでなく，疾患 subtype，label quality，treatment status，image artifact などの hidden subgroup で underdiagnosis が起こる可能性がある．

## Subgroup separability による現れ方の違い

underdiagnosis bias が学習データに存在しても，それが群間の性能差として観測されるとは限らない．Jones et al. は，モデルが画像から subgroup member を識別できる度合い（[[Subgroup_Separability]]）が高いときにのみ，underdiagnosed group の性能が選択的に劣化し，group fairness metric がそれを検出できることを理論的・実証的に示した．separability が低い場合，bias は全 group に一様に波及し，group 間の差としては現れない．したがって，「group fairness metric に差が出ない」ことは「bias がない」ことを意味せず，subgroup separability が低いために検出できていないだけの可能性がある．

## 運用での使い方

Underdiagnosis bias は，モデル開発時の validation だけでなく，deployment 後の monitoring で継続的に見るべき指標である．特に triage，screening，worklist prioritization のように，negative prediction が受診機会や読影順序を下げる用途では優先度が高い．

| 運用場面 | 見るべきこと |
| --- | --- |
| validation | subgroup ごとの `no finding` FPR/FNR，confidence interval |
| model selection | worst group の underdiagnosis rate を悪化させないか |
| external validation | dataset shift 下でも同じ subgroup が見逃されないか |
| deployment monitoring | 実運用 population で underdiagnosis gap が変化しないか |
| human audit | 見逃された症例に共通する disease type，artifact，label noise |

この監視は [[Subgroup_Performance_Monitoring]] の一部として扱うのが自然である．known demographic subgroup と discovered hidden subgroup の両方で underdiagnosis を測ることで，平均性能に隠れた failure mode を露出できる．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| underdiagnosis | 疾患ありの患者を健康または異常なしと扱う失敗 |
| underdiagnosis bias | underdiagnosis rate が subgroup 間で偏ること |
| `no finding` FPR | 実際は疾患ありなのに `no finding` と予測する率 |
| `no finding` FNR | 実際は no finding なのに疾患あり方向に予測する率 |
| selective underdiagnosis | 誤りがランダムではなく，健康扱いする方向に偏ること |
| intersectional underdiagnosis | 複数属性の組み合わせ subgroup で underdiagnosis が強くなること |
| bias amplification | clinical record や label にある bias を model が増幅すること |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Subgroup_Performance_Monitoring]]
- [[Worst_Group_Performance]]
- [[Hidden_Stratification]]
- [[Intersectional_Fairness]]
- [[Bias_Amplification]]
- [[Vision_Language_Model_Fairness]]
- [[Subgroup_Separability]]
