---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_underdiagnosis_bias_chest_radiographs.pdf"
---

# Underdiagnosis bias of artificial intelligence algorithms applied to chest radiographs in under-served patient populations

この論文は，胸部 X 線診断モデルが underserved patient populations を選択的に underdiagnose するかを検証する．ここで underdiagnosis は，疾患を持つ患者を「no finding」と予測し，健康と誤って扱う失敗である．臨床 triage では，この失敗は受診優先度や治療開始を遅らせるため，単なる分類誤差より直接的な害になりうる．

著者らは，MIMIC-CXR，CheXpert，ChestX-ray14，および3 dataset を shared labels で統合した multi-source dataset を用い，sex，age，race/ethnicity，insurance type，および intersectional subgroups における underdiagnosis rate を比較した．結果として，female patients，younger patients，Black patients，Hispanic patients，Medicaid insurance の患者などで underdiagnosis が高く，intersectional subgroup ではさらに高くなる傾向が示された．

## 問題設定

医療画像 AI は expert-level performance を示すことがある一方，既存医療にある bias を反映・増幅する可能性がある．本論文は，特に underdiagnosis に注目する．underdiagnosis は「病気がある患者を健康と分類する」誤りであり，患者が必要な治療を受ける機会を失う可能性がある．

論文では，AI-based CXR prediction models が胸部 X 線から disease labels と `no finding` label を予測する設定を扱う．`no finding` は，対象 disease labels が検出されないことを表す．この `no finding` の false positive が，実質的な underdiagnosis とみなされる．

## Dataset

| Dataset | 画像数 | 患者数 | 主な属性 |
| --- | ---: | ---: | --- |
| MIMIC-CXR (CXR) | 371,858 | 65,079 | sex，age，race/ethnicity，insurance type |
| CheXpert (CXP) | 223,648 | 64,740 | sex，age |
| ChestX-ray14 (NIH) | 112,120 | 30,805 | sex，age |
| ALL | 707,626 | 129,819 | CXR，CXP，NIH の shared labels |

CXR と CXP は14 diagnosis labels を持ち，NIH は15 diagnosis labels を持つ．ALL dataset では，3 dataset の8 shared labels を使う．CXR と CXP では frontal と lateral images を含むが，NIH は frontal images のみである．

Table 1 では，平均 AUC が CXR 0.834，CXP 0.805，NIH 0.835，ALL 0.859 と報告されている．これは，各 dataset で5つの random seeds による model の label-wise AUC を平均した値である．

## Underdiagnosis rate の定義

本論文では，`no finding` label の binarized prediction における false positive rate を underdiagnosis rate と定義する．

```text
underdiagnosis rate
  = FPR of the no finding label
  = P(predicted no finding | actually not no finding)
```

subgroup `s_j` については `FPR_sj`，intersectional subgroup `s_i,j` については `FPR_si,j` を比較する．たとえば female patients，Black female patients，0-20 years and Medicaid insurance のような単位で underdiagnosis rate を計算する．

著者らは，単なる noisy model か，選択的な underdiagnosis bias かを区別するために，`no finding` の FNR も測る．もし誤差が単なる noise なら FPR と FNR は subgroup 間で同方向に増える可能性がある．一方，特定 subgroup が「健康」として過剰に予測されるなら，`no finding` FPR は高く，`no finding` FNR は低くなる．

## Model training

モデルは ImageNet weights で初期化した 121-layer DenseNet である．CXR，CXP，ALL では既存研究 CheXclusion と同じ training code を使い，NIH では `no finding` label を含めて学習する．入力画像は 256 x 256 pixels に resize し，ImageNet の mean/std で normalize する．

training / validation / test sizes は次の通りである．

| Dataset | train | validation | test |
| --- | ---: | ---: | ---: |
| ALL | 575,381 | 67,177 | 65,068 |
| CXR | 298,137 | 37,300 | 36,421 |
| CXP | 178,352 | 23,022 | 22,274 |
| NIH | 98,892 | 6,855 | 6,373 |

data augmentation は center crop，random horizontal flip，random rotation を用いる．optimizer は Adam，loss は binary cross-entropy である．評価 metric は同じ test set 上で計算し，5 random seeds の平均と95% confidence interval を報告する．threshold は全 group に共通の1つを用い，F1 score を最大化する値を選ぶ．protected attributes は train/test 時に model input としては使わない．

## 主な結果

CXR dataset では，female patients，0-20 years の患者，Black patients，Hispanic patients，Medicaid insurance の患者で underdiagnosis rate が高かった．つまり，これらの患者群は疾患があるにもかかわらず「no finding」と予測されるリスクが高い．

CXR，ALL，CXP では，female patients と younger patients が高い underdiagnosis rate を示すという傾向が一貫していた．NIH では male patients と >80 years の患者が最も underdiagnosed だったが，著者らは，>80 years group の test set に `no finding` label が37 samples しかないこと，NIH dataset が clinical hospital ではなく研究病院由来であることなどを理由に，dataset selection bias や small sample size の影響を示唆している．

Table 2 では，最も underdiagnosed な sex / age subgroup が次のように整理されている．

| Dataset | sex | age | female-age |
| --- | --- | --- | --- |
| CXR | Female | 0-20 years | 0-20 years |
| CXP | Female | 20-40 years | 20-40 years |
| NIH | Male | >80 years | 0-20 years |
| ALL | Female | 0-20 years | 0-20 years |

## Intersectional subgroup

intersectional subgroup では，underdiagnosis bias が重なる傾向がある．CXR dataset では，Hispanic female patients は white female patients より underdiagnosis rate が高かった．また，0-20 years and female，0-20 years and Black，0-20 years and Medicaid insurance の患者群が高い underdiagnosis rate を示した．

著者らは，すべての female patients が同じ率で誤診されるわけではなく，Hispanic female patients のように，複数の underserved attributes を持つ subgroup で underdiagnosis が強くなることを示している．ただし，最も小さい intersectional group が常に最悪とは限らないとも述べている．

## Underdiagnosis と overdiagnosis の関係

CXR dataset では，`no finding` FPR と `no finding` FNR が subgroup 間で inverse relationship を示した．つまり，under-served subgroups は「no finding」として過剰に予測される一方，対応する overdiagnosis が同時に増えているわけではない．

著者らは，この結果を単なる overall noise ではなく，selective algorithmic underdiagnosis と解釈している．もし誤りが random noise なら，健康扱いする誤りと病気扱いする誤りが同時に増えうる．しかし実際には，特定 subgroup に対して健康扱いする方向の誤りが増えていた．

## Disease prevalence と FDR

underdiagnosed population の disease prevalence は，一般の unhealthy population と異なっていた．たとえば，underdiagnosed population は lung lesion の positive label を持つ割合が高く，pleural effusion の positive label を持つ割合が低かった．これは，疾患検出の難しさが disease type によって異なることを示唆する．

また，著者らは `no finding` label の FDR も評価している．ここで FDR は，classifier が `no finding` と予測したときに実際には ill である確率に対応する．FDR でも protected attributes 間の gap が見られたが，その pattern は FPR/FNR と異なり，group ごとの prevalence の違いに影響される．

## Fairness definition の注意

本論文は underdiagnosis を主要な fairness concern として扱うが，臨床用途によって考慮すべき fairness definition は異なる．たとえば predictive parity は positive predictive value，または FDR の equality に対応する．ただし base rate が group 間で異なると，FNR，FPR，FDR を同時に等しくすることは一般に不可能である．

著者らは，subgroup ごとに threshold を変える post-processing で FNR/FPR を調整する方法にも限界があると述べる．intersectional subgroup では sample size が小さく threshold 推定が不安定になる．protected attributes が増えると必要な threshold 数が指数的に増える．また race/ethnicity は社会的構築物として境界が曖昧であり，group-specific threshold の運用には倫理的・実務的問題がある．

## Bias amplification

著者らは，report labels が clinical records から抽出されているため，ground truth 自体が unbiased ではない可能性を指摘する．既存医療で underserved subpopulations が underdiagnosed されているなら，その clinical records を使って学習した model は既存 bias を反映するだけでなく，さらに増幅する可能性がある．

また，CXR datasets では radiology reports から NLP-based automatic labelers で labels を作る流れが一般化している．NLP-based labelers は subgroup 間の labeling quality bias を持つ可能性があり，これも model bias の source になりうる．

## 規制・運用上の示唆

著者らは，AI-based diagnostic algorithms の regulatory approval や deployment 前評価に underdiagnosis checks を組み込むべきだと主張する．特に triage では，underdiagnosis が access to care を遅らせるため，subgroup-specific underdiagnosis rate を開発時と deployment 後に継続的に評価する必要がある．

結論として，本論文は，胸部 X 線モデルが underserved subpopulations と intersectional subgroups を systemically underdiagnose する証拠を示し，robust audit なしに医療画像 AI を実運用へ移すと既存の health inequities を悪化させうると述べる．

## 関連概念

- [[Underdiagnosis_Bias]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Subgroup_Performance_Monitoring]]
- [[Worst_Group_Performance]]
- [[Bias_Amplification]]
- [[Intersectional_Fairness]]
