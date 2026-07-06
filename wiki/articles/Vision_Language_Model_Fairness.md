---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_demographic_bias_vision_language_foundation_models_medical_imaging]]"
---

# Vision Language Model Fairness

Medical vision-language model の fairness では，zero-shot diagnosis や self-supervised training によって annotation bias を避けられる，という期待をそのまま信じてはいけない．VLM は radiology image と report text から広い pathology を診断できる一方，画像表現に sensitive demographic information を encode し，特定 subgroup を underdiagnose する可能性がある．

この概念が重要なのは，VLM の臨床的な魅力が「explicit labels なしで多疾患を診断できる」点にあるからである．label supervision が少ないことは，公平性の保証ではない．むしろ，report text，site distribution，population imbalance，image-level demographic signal を通じて，bias が foundation representation に入り込む可能性を監査する必要がある．

## 何を評価するか

VLM fairness では，average AUROC と zero-shot coverage だけでなく，subgroup ごとの threshold error と representation-level demographic encoding を同時に見る．

| 評価対象 | 指標 | 目的 |
| --- | --- | --- |
| diagnostic utility | AUROC / ROC | radiologists と同等以上の診断性能があるか |
| subgroup error | FNR / FPR / TPR / TNR | underdiagnosis が特定 subgroup に偏るか |
| intersectional subgroup | sex x race，age x race など | 単独属性では見えない worst group を検出する |
| unseen findings | zero-shot finding ごとの gap | VLM の広い診断範囲で bias が残るか |
| representation | demographic attribute prediction AUC | embedding が sensitive information を持つか |
| human comparison | radiologists の operating point / attribute prediction | AI 特有の bias か，人間にもある bias かを切り分ける |

この評価は [[Medical_Image_Fairness_Evaluation]] の一部だが，VLM では text prompt と image-text representation があるため，image-only classifier より監査対象が広い．

## Zero-shot は fairness を保証しない

CheXzero のような medical VLM は，pathology labels を使わず，radiographs と clinical texts から self-supervised に training される．このため，explicit pathology annotation の human label bias を避けられるように見える．

しかし，Yang et al. は CheXzero が CheXpert 上で radiologists と同等または高い AUROC を示しながら，radiologists より大きい underdiagnosis disparity を持つことを示した．たとえば Enlarged Cardiomediastinum，Pleural Effusion，Lung Opacity で expert-level の AUROC を示しても，sex，age，race，intersectional subgroup の underdiagnosis gap は大きかった．

```text
zero-shot / self-supervised VLM
  -> label annotation を直接使わない
  -> しかし report text と image distribution から bias を学びうる
  -> average AUROC が高くても subgroup safety は別に評価する
```

## Underdiagnosis を中心に見る

VLM が screening / triage に使われる場合，疾患あり患者を健康側へ寄せる誤りが最も危険である．そのため，pathology label では FNR / TPR，`No Finding` では FPR / TNR を subgroup ごとに見る．

| Task | 臨床的に危険な失敗 | Fairness metric |
| --- | --- | --- |
| pathology detection | 疾患ありを陰性とする | FNR gap / TPR gap |
| `No Finding` prediction | 疾患ありを no finding とする | FPR gap / TNR gap |
| broad finding detection | unseen finding で特定 subgroup を見逃す | finding-wise underdiagnosis disparity |

MIMIC では，female patients，18-40 歳の younger patients，Black patients が高い underdiagnosis rate を示し，Black female patients のような intersectional subgroup で bias が強くなった．これは [[Underdiagnosis_Bias]] が VLM にもそのまま重要であることを示す．

## Embedding が demographic signal を持つ

VLM fairness では，入力に protected attribute を含めたかどうかだけでは不十分である．画像 encoder の embedding が sensitive information を持つなら，model は明示的な demographic column なしに subgroup-specific behavior を取りうる．

Yang et al. は CheXzero の penultimate layer embedding に logistic regression head を載せ，frozen representation から sex，age，race，intersectional subgroup を予測した．MIMIC の balanced subset では，female AUC 0.92，18-40 歳 AUC 0.94，Black AUC 0.78，Black female AUC 0.83 だった．同じ chest X-rays を見た radiologists は，race や intersectional attribute をモデルほど高く予測できなかった．

これは [[Race_Recognition_In_Medical_Images]] の一般化である．race だけでなく，age，sex，intersectional demographic attributes が foundation representation に残り，underdiagnosis の経路になりうる．

## Text prompt は介入点でもあり bias source でもある

VLM は text prompt を入力に含むため，prompt は公平性を変える intervention point になる．demographic details を prompt に入れると，一部の pathology では subgroup bias が減る可能性がある．

ただし，prompt-based demographic intervention は安定した解決策ではない．Yang et al. では，Lung Opacity や `No Finding` では bias が減ったが，Pneumonia では改善しなかった．このため，prompt に demographic information を足して公平になるかは task / pathology / subgroup ごとに検証が必要である．

## 監査プロトコル

medical VLM を評価するときは，次を最低限の監査単位にする．

| Step | 内容 |
| --- | --- |
| dataset audit | sex，age，race，site，label source，missing demographics を記録する |
| utility audit | pathology ごとの AUROC と radiologist operating point を比較する |
| underdiagnosis audit | subgroup / intersectional subgroup の FNR，FPR，TPR，TNR を測る |
| unseen finding audit | zero-shot findings でも subgroup gap を測る |
| embedding audit | frozen embedding から demographic attributes が予測できるかを見る |
| prompt audit | prompt template と demographic wording が subgroup outcome を変えないか確認する |
| external validation | MIMIC，CheXpert，NIH，PadChest，VinDr のように地域差を跨いで見る |

特に VLM は1つの model で多くの findings を扱うため，少数の benchmark disease だけで「公平」と判断するのは危険である．finding-wise に bias を出すと，見えにくい zero-shot finding で大きい gap が残ることがある．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| medical VLM | medical image と clinical text を対応づけて学習する vision-language model |
| zero-shot diagnosis | task-specific pathology labels なしで text prompt により診断すること |
| underdiagnosis disparity | subgroup 間の FNR / FPR / TPR / TNR 差 |
| demographic encoding | embedding から sex，age，race などが予測できること |
| prompt-based intervention | VLM の text prompt に demographic information を入れて model behavior を変える介入 |
| intersectional subgroup | sex x race など複数属性の組み合わせ subgroup |

## 関連概念

- [[Foundation_Model_Fairness]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Underdiagnosis_Bias]]
- [[Race_Recognition_In_Medical_Images]]
- [[Demographic_Imbalance]]
- [[Subgroup_Performance_Monitoring]]
