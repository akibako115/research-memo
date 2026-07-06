---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_ai_recognition_patient_race_medical_imaging.pdf"
---

# AI recognition of patient race in medical imaging: a modelling study

この論文は，deep learning model が medical image pixel data だけから self-reported race を予測できるかを，大規模な public / private datasets と複数 imaging modalities で検証する．人間の radiology experts には obvious ではない race information が，AI model には高精度に利用可能であることを示す点が中心である．

著者らは，chest X-ray，chest CT，mammography，hand X-ray，cervical spine X-ray などで race prediction model を学習・外部検証し，race が複数 dataset，clinical environments，modalities を越えて高 AUC で予測できることを示した．また，BMI，disease distribution，breast density，age/sex/body habitus などの obvious confounders ではこの性能を説明できず，race signal は画像内の特定部位や特定 frequency band に単純に局在しないと報告している．

## 問題設定

医療画像 AI では，race を model input に入れていない場合でも，画像自体から race-related information を model が抽出する可能性がある．この能力があると，race-agnostic だと思われている model が race-specific errors を生む経路になりうる．

本論文は，self-reported race を biological essence ではなく，external perception と self-identification に関わる social, political, legal construct と定義する．racial discrimination における harm の vector は genetic ancestry ではなく racial identity であるため，self-reported race を racial identity の proxy として扱う．

## Dataset

public and private datasets を用い，複数 modalities と clinical scenarios を含める．

| Abbrev. | Dataset | Data type | Patients / images |
| --- | --- | --- | ---: |
| MXR | MIMIC-CXR | chest X-ray | 53,073 / 228,915 |
| CXP | CheXpert | chest X-ray | 65,400 / 223,414 |
| EMX | Emory chest X-ray | chest X-ray | 90,518 / 227,872 |
| NLST | National Lung Cancer Screening Trial | chest CT | 512 / 198,475 |
| RSPECT | RSNA Pulmonary Embolism CT | chest CT | 254 / 72,329 |
| EM-CT | Emory Chest CT | chest CT | 560 / 187,513 |
| DHA | Digital Hand Atlas | digital radiography X-ray | 691 / 691 |
| EM-Mammo | Emory Mammogram | breast mammograms | 27,160 / 86,669 |
| EM-CS | Emory Cervical Spine | lateral cervical spine X-ray | 997 / 10,358 |

race categories は dataset により分布が異なり，単一の race がすべての dataset で一貫して dominant ではない．主な分析では Asian，Black，White patients を扱い，sample size や記録方法の問題から Native American patients や Hispanic patients は十分に分析できないとして除外している．

## 実験群

著者らは3種類の実験を行う．

| 実験 | 目的 |
| --- | --- |
| race detection | medical images から race を予測できるか，外部 dataset や modality を越えて generalize するか |
| confounder analysis | BMI，disease labels，tissue density，age，sex，body habitus などが race prediction を説明するか |
| mechanism analysis | frequency filtering，resolution degradation，segmentation，occlusion，patch training で race signal の所在を探る |

performance variance や null hypothesis tests は，大規模 dataset と effect size の大きさのため informative ではないとして報告していない．

## Race detection の結果

chest X-ray では，internal validation と external validation の両方で高い AUC が得られた．

| Setting | AUC |
| --- | --- |
| MXR internal | ResNet34 0.97，DenseNet121 0.94 |
| CXP internal | ResNet34 0.98 |
| EMX internal | ResNet34 0.98，DenseNet121 0.97，EfficientNet-B0 0.99 |
| MXR to CXP / EMX | 0.97 / 0.97 |
| CXP to EMX / MXR | 0.97 / 0.96 |
| EMX to MXR / CXP | 0.98 / 0.98 |

Table 3 では，Asian，Black，White の3-class race classification でも高 AUC が報告されている．たとえば MXR ResNet34 では Asian 0.986，Black 0.982，White 0.981，CXP ResNet34 では Asian 0.981，Black 0.980，White 0.980 である．external validation でも多くが 0.91-0.98 の範囲にある．

non-chest modalities でも race detection は成立した．NLST chest CT では slice 0.92 / study 0.96，NLST to EM-CT では slice 0.80 / study 0.87，NLST to RSPECT では slice 0.83 / study 0.90，EM-Mammo では image 0.78 / study 0.81，EM-CS では 0.913，DHA では 0.87 が報告されている．

## Confounder analysis

著者らは，obvious anatomical / phenotypic confounders では race detection performance を説明できないことを示す．

| Confounder | 結果 |
| --- | --- |
| BMI alone | CXP で AUC 0.55 |
| tissue density | AUC 0.54 |
| age + tissue density | AUC 0.61 |
| diagnostic labels alone | MXR 0.54-0.61，CXP 0.52-0.57 |
| age，sex，gender，disease，body habitus の組み合わせ | logistic regression 0.65，random forest 0.64，XGBoost 0.64 |

`no finding` class だけでも race detection は高性能だった．MXR では `no finding` class の race detection AUC が Asian 0.914，Black 0.949，White 0.941 であり，全 disease classes を含む dataset の AUC と同程度だった．これは，race detection が disease labels だけで説明されないことを示す．

bone density information を除去しても，Black patients の race detection は MXR で AUC 0.960，CXP で 0.945 と高かった．average pixel thresholds for different tissues は AUC 0.5 で usable signal を持たなかった．

## Mechanism analysis

著者らは，race information が特定の anatomical region，frequency spectrum，image quality に単純に局在しないことを示す．low-pass / high-pass filtering，band-pass / notch filtering，resolution degradation，lung segmentation，saliency maps，occlusion，patch-based training を試したが，reasonable な resolution reduction，noise addition，frequency filtering，patch masking で race detection は十分には消えなかった．

MXR dataset では，160 x 160 以上の image resolution で AUC が 0.95 を超えた．また，3 x 3 grid の特定 patch を除いても race prediction は頑健で，画像の9分の1だけでも race identification performance が残った．

## 解釈

著者らは，AI が self-reported race を予測できること自体が問題なのではなく，この capability が多くの医療画像 model に readily learned であり，既存の racial disparities を再生・悪化させる direct vector になりうることが問題だと述べる．

人間の radiologists は通常 race demographic information を持たず，medical images から race を識別できない．そのため，model が race information を使って race-specific errors を出しても，人間の oversight だけでは認識・緩和しにくい．

## Colorblind approach への示唆

known disparity を緩和する方法として，sensitive attributes を encode する features を取り除き，model を colorblind にする発想がある．しかし本論文は，medical imaging では racial identity information が極めて isolate しにくいため，この approach は実現困難かもしれないと述べる．

著者らは，racial bias を検出する strategy と，racial outcomes を equalize する model design を default として検討すべきだと主張する．regulatory environment も，unexpected racial recognition by AI models を識別・緩和する強い process をまだ持っていないと指摘する．

## Limitations

本研究は self-reported race を ground truth として用いている．race は biological construct ではなく social construct であり，genetic variation は race 間より race 内の方が大きいという既存研究を踏まえている．しかし discrimination and bias の文脈では，self-reported race は racial identity の proxy として重要である．

また，racial identity labels の利用可能性と小さい cohort size のため，分析対象は Asian，Black，White に限定され，Native American patients や Hispanic patients は十分に扱えなかった．bone density 除去の実験にも residual bone tissue が残る可能性がある．

最後に，この研究は race による新たな performance disparity を直接確立したものではない．既存研究が示した disparities と，本研究が示した race recognition capability を合わせると，medical imaging model が race を認識し，異なる racial groups に異なる health outcomes を生む可能性がある，という位置づけである．

## 関連概念

- [[Race_Recognition_In_Medical_Images]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Demographic_Imbalance]]
- [[Bias_Amplification]]
- [[Underdiagnosis_Bias]]
