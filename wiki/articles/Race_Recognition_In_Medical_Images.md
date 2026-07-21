---
created: 2026-07-06
updated: 2026-07-21
sources:
  - "[[sources/2026-07-06_ai_recognition_patient_race_medical_imaging]]"
  - "[[sources/2026-07-06_demographic_bias_vision_language_foundation_models_medical_imaging]]"
  - "[[sources/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization]]"
  - "[[sources/2026-07-21_subgroup_separability_group_fair_medical_image_classification]]"
  - "[[sources/2026-07-21_demographically_invariant_models_representations_medical_imaging_fair]]"
---

# Race Recognition In Medical Images

医療画像モデルに race を入力していなくても，画像そのものから race-related information を学習できるなら，「protected attribute を使っていないから公平」という前提は崩れる．Race recognition in medical images は，deep learning model が X-ray，CT，mammography などの pixel data だけから self-reported race を高精度に予測できる現象である．

この概念が重要なのは，人間には見えない sensitive information を model が利用できるためである．radiologist が race を画像から識別できず，model input に race column がなくても，image encoder が race signal を内部表現に持てば，race-specific error や [[Underdiagnosis_Bias]] の経路になりうる．

## 何が示されたか

Gichoya et al. は，public / private datasets と複数 modalities で，AI model が self-reported race を medical image alone から予測できることを示した．

| Modality | 例 | Race detection performance |
| --- | --- | --- |
| chest X-ray | MIMIC-CXR，CheXpert，Emory CXR | internal / external validation で概ね AUC 0.91-0.99 |
| chest CT | NLST，Emory Chest CT，RSNA PE CT | study-level AUC 0.87-0.96 |
| mammography | Emory Mammogram | study-level AUC 0.81 |
| cervical spine X-ray | Emory Cervical Spine | AUC 0.913 |
| hand X-ray | Digital Hand Atlas | AUC 0.87 |

重要なのは，この能力が単一 dataset の artifact ではなく，外部 dataset，施設，patient population，modality を越えて残る点である．

## Colorblind model の限界

医療 AI fairness では，protected attribute を model input から外せば bias を避けられる，という発想がある．しかし医療画像では，pixel data 自体に protected attribute information が含まれる可能性がある．

```text
race column を使わない
  != model が race information を使えない

image pixels
  -> encoder representation
  -> self-reported race signal
  -> race-specific prediction behavior
```

このため，colorblind approach は十分な guardrail にならない．むしろ，race を評価 metadata として保持し，subgroup performance を明示的に監査する必要がある．

## Confounder では説明しきれない

race recognition が，BMI，disease distribution，breast density，age，sex，body habitus などの obvious proxy だけで起こるなら，それらを除去・調整すればよい．しかし Gichoya et al. では，これらの confounder で race を予測する model は image-based model より大幅に低性能だった．

| Confounder model | AUC |
| --- | ---: |
| BMI alone | 0.55 |
| tissue density | 0.54 |
| age + tissue density | 0.61 |
| diagnostic labels alone | 0.52-0.61 |
| age，sex，disease，body habitus の組み合わせ | 0.64-0.65 |

一方，image-based model は chest X-ray で AUC 0.95 前後を出す．これは，race signal が単純な disease label や body habitus proxy だけでは説明できないことを示す．

## Signal が局在しにくい

race signal が画像の特定領域や周波数成分に局在していれば，masking や filtering で除去できるかもしれない．しかし Gichoya et al. は，low-pass / high-pass filtering，resolution degradation，lung segmentation，occlusion，patch-based training などを試しても，race prediction が頑健に残ることを示した．

| 操作 | 示唆 |
| --- | --- |
| frequency filtering | race signal は単一 frequency band に閉じていない |
| resolution degradation | 160 x 160 以上では AUC > 0.95 が残る |
| lung segmentation | lung region だけ，または非 lung region だけでも signal が残る |
| occlusion | 特定 patch を消しても prediction が壊れにくい |
| patch-based training | 画像の一部だけでも race information が残る |

このため，technical feature removal だけで race information を完全に消すのは難しい．

## Fairness 評価への影響

Race recognition capability は，[[Medical_Image_Fairness_Evaluation]] の設計を変える．protected attribute を model に入れたかどうかではなく，model behavior が protected subgroup ごとにどう違うかを評価する必要がある．

| 評価設計 | 理由 |
| --- | --- |
| self-reported race を evaluation metadata として保持する | model が race signal を内部利用しうるため |
| subgroup AUC / FPR / FNR / calibration を報告する | race-specific errors を検出するため |
| external validation を行う | race signal が施設 artifact か一般化するかを確認するため |
| intersectional subgroup を見る | race と sex/age の組み合わせで failure が増える可能性があるため |
| model explanation に頼りすぎない | signal が局在せず，人間にも見えにくいため |

この概念は [[Demographic_Imbalance]] とも関係するが，同じではない．demographic imbalance は dataset distribution の問題であり，race recognition は image representation が sensitive information を含みうる問題である．balanced dataset でも，model が race information を学習できる可能性は残る．

Yang et al. は，この問題が medical [[Vision_Language_Model_Fairness|vision-language foundation model]] の embedding にも現れることを示した．CheXzero の frozen penultimate-layer embedding から，Black subgroup を AUC 0.78，Black female subgroup を AUC 0.83 で予測できた．同じ胸部 X 線を見た radiologists の race prediction は random guess に近く，VLM が人間には読みにくい demographic signal を representation に持つ可能性を示している．

別の Yang et al. は，demographic encoding が fairness gap と相関し，さらに [[Fairness_Under_Distribution_Shift]] にも影響することを示した．ID data で representation から age，race，sex が予測しやすい model は FPR/FNR gap が大きくなりやすく，OOD deployment では ID fairness gap 最小の model より demographic encoding が少ない model selection の方が fair になりやすかった．

[[Subgroup_Separability]] は，この race predictability が modality と attribute によってどれだけ変動するかを定量化する枠組みを与える．Jones et al. は，chest X-ray からの race 予測が AUC 0.936-0.951 に達する一方，fundus image からの sex 予測は AUC 0.642 にとどまるなど，separability が dataset-attribute の組み合わせで大きく異なることを示した．separability が高い modality ほど，biased data で学習したモデルが sensitive information を representation に強く符号化しやすい．

[[Demographic_Representation_Invariance]] は，「race を符号化しないモデル」という colorblind approach の裏側にある発想を，marginal / class-conditional / counterfactual invariance という形式的な要求として分析する．そのうえで，group membership を符号化しないよう representation を強制すること自体が，statistical parity や separation の強制と等価であり，予測精度の犠牲や disparate treatment を招きうることを示す．したがって，race information を representation から除去すること自体を目標にするのではなく，race subgroup ごとの実際の outcome（error rate，calibration）を監査する方が実務的である，という本記事の結論とも整合する．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| race recognition | model が medical image から self-reported race を予測できること |
| colorblind approach | protected attribute を入力から除けば公平になるという発想 |
| self-reported race | 本研究で racial identity の proxy として用いられる属性 |
| external validation | train dataset と異なる dataset / institution で評価すること |
| confounder analysis | BMI，disease label，tissue density などで説明できるか確認する分析 |
| frequency filtering | low-pass / high-pass などで画像周波数成分を操作する実験 |

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Demographic_Imbalance]]
- [[Underdiagnosis_Bias]]
- [[Subgroup_Performance_Monitoring]]
- [[Bias_Amplification]]
- [[Vision_Language_Model_Fairness]]
- [[Fairness_Under_Distribution_Shift]]
- [[Subgroup_Separability]]
- [[Demographic_Representation_Invariance]]
