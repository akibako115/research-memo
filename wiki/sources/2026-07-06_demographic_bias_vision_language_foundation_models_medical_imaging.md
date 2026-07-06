---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_demographic_bias_vision_language_foundation_models_medical_imaging.pdf"
---

# Demographic Bias of Expert-Level Vision-Language Foundation Models in Medical Imaging

この論文は，medical vision-language foundation model が expert-level の診断性能を示しても，sex，age，race，intersectional subgroup に対して systematic underdiagnosis bias を持ちうることを，胸部 X 線の5つの国際 dataset で評価する．中心モデルは CheXzero であり，別の vision-language foundation model である KAD でも同様の傾向を確認している．

主な主張は，self-supervised / vision-language training によって pathology label の明示的 supervision を避けても，demographic bias は消えない，という点である．モデルは board-certified radiologists と同等またはそれ以上の AUROC を示す一方，radiologists より大きい underdiagnosis disparity を示し，さらに画像表現に demographic information を人間以上に強く encode していた．

## 評価対象

評価対象 dataset は5つの public chest X-ray datasets である．MIMIC と CheXpert は sex，age，race を持ち，NIH，PadChest，VinDr は sex と age を持つ．欠損 demographic data を持つ sample は除外されている．

| Dataset | 地域 | 規模 | Demographics |
| --- | --- | ---: | --- |
| MIMIC-CXR | Boston, US | 357,167 images / 61,927 patients | sex，age，race |
| CheXpert | Stanford, US | 223,458 images / 64,925 patients | sex，age，race |
| NIH ChestX-ray14 | Bethesda, US | 112,120 images / 30,805 patients | sex，age |
| PadChest | Spain | 160,736 images / 67,590 patients | sex，age |
| VinDr-CXR | Vietnam | 5,323 images / 5,323 patients | sex，age |

CheXpert test set 666 samples と VinDr 5,323 samples には外部 radiologist annotations があり，モデルと board-certified radiologists の diagnostic performance / fairness を比較するために使われる．PadChest では 39,053 images の physician-annotated subset を使い，unseen radiographic findings への generalization を評価する．

## モデル

主な評価対象は CheXzero である．CheXzero は ViT-B/32 backbone と OpenAI CLIP の pre-trained weights から初期化され，MIMIC の radiographs と対応する clinical texts を使って self-supervised に trained される．pathology labels や annotations は training に使われない．

追加検証として，knowledge graph を visual-language pretraining に導入する KAD も評価され，MIMIC 上で sex，age，race subgroup にまたがる underdiagnosis disparity が同様に観察されている．

## Fairness metric

病変 label では，疾患あり患者を陰性扱いする false negative が treatment delay につながるため，subgroup 間の FNR / TPR 差を underdiagnosis disparity として測る．`No Finding` では，疾患あり患者を `No Finding` と予測する失敗が問題なので FPR / TNR を見る．これは equal opportunity の一例として位置づけられる．

| 対象 | 主な失敗 | 評価する error |
| --- | --- | --- |
| pathology label | 疾患ありを陰性とする | FNR / TPR |
| `No Finding` | 疾患ありを `No Finding` とする | FPR / TNR |
| subgroup gap | 2つの subgroup 間の差 | underdiagnosis disparity |

threshold-dependent metrics は validation set 上で Youden's J statistic を最大化する threshold を用いて計算される．95% confidence interval は non-parametric bootstrap sampling 1,000回で推定される．

## Radiologists より大きい fairness disparity

CheXpert test set では，CheXzero は3つの pathology で radiologists と同等またはそれ以上の AUROC を示した．Enlarged Cardiomediastinum は AUC 0.917，Pleural Effusion は AUC 0.938，Lung Opacity は AUC 0.919 である．

しかし，同じ CheXpert test set で underdiagnosis disparity を比較すると，モデルは board-certified radiologists より大きい fairness gap を示した．たとえば Enlarged Cardiomediastinum では，sex，age，race，sex/race intersectional subgroup のすべてで，モデルの underdiagnosis rate が有意に高かった．報告された p 値は sex で 1.28e-131，age で 2.51e-103，race で 8.79e-93，intersectional sex/race で 1.58e-206 である．

この結果は，overall diagnostic accuracy が高いことと，subgroup-wise clinical safety が高いことは同じではないことを示す．

## Marginalized / intersectional subgroup の underdiagnosis

MIMIC では `No Finding` label を中心に underdiagnosis と overdiagnosis を評価する．`No Finding` の FPR は underdiagnosis，FNR は overdiagnosis として扱われる．

観察された pattern は，female patients，18-40 歳の younger patients，Black patients で algorithmic underdiagnosis rate が高い，というものである．さらに，Black female patients のような intersectional subgroup では underdiagnosis rate がより強くなる．著者らは，Lung Opacity や Pneumonia など他の pathologies でも同様の傾向があることを示している．

`No Finding` の FPR と FNR は subgroup 間で inverse relationship を示し，単なる random noise ではなく，特定 subgroup を健康側へ寄せる selective underdiagnosis の可能性を示す．

## Unseen radiographic findings での bias

PadChest では，174 findings と19 differential diagnoses のうち，sample size が100を超え，モデル AUC が0.7以上の48 radiographic findings を評価する．これらは CheXzero の training で labeled samples を見ていない unseen findings である．

sex では，`Multiple nodules` で female / male 間の maximum underdiagnosis disparity が 24.1% だった．48 findings のうち31 findings で fairness gap が5%を超えた．age では disparity がさらに大きく，`Tracheostomy tube` で 18-40 歳と >80 歳の間に 100% の gap があり，45/48 findings で20%を超える fairness gap があった．

これは，vision-language foundation model の demographic bias が，既知の benchmark pathology だけでなく，zero-shot / unseen finding setting でも現れることを示す．

## Demographic information の encoding

著者らは，モデルが demographic information を encode しているかを調べるため，MIMIC から sex，age，race が balanced になるように480 chest X-rays を選び，モデルの penultimate layer embedding に logistic regression の linear attribute prediction head を載せた．モデル本体は frozen にされる．同じ480 images について，3人の board-certified radiologists に chest X-ray のみから sex，age，race を推定させた．

CheXzero の embedding は，明示的な demographic supervision がなくても sensitive attributes を高 AUC で予測できた．female は AUC 0.92，18-40 歳は AUC 0.94，Black は AUC 0.78，Black female は AUC 0.83 である．radiologists は sex prediction では比較的高い AUC を示したが，age や race，intersectional group ではモデルより低く，race prediction は random guess に近かった．

この結果は，医療画像 VLM が人間には読みにくい demographic signal を representation に持ち，それが underdiagnosis bias の経路になりうることを示す．

## Prompt-based intervention

追加実験では，demographic details を text prompt に組み込むことで fairness intervention を試みている．例として，`Does this female patient have Pneumonia?` のように sensitive demographic information を input text に含める．

結果は一貫した解決ではない．Lung Opacity や `No Finding` では demographic bias が減る場合があったが，Pneumonia では改善しなかった．著者らは，demographic information を使って fairness を改善できる可能性はあるが，より原理的な方法が必要だとしている．

## Limitations

demographic labels は self-reported または physician-recorded であり，label noise を含みうる．dataset 間で image quality や projection が揃っていないため，その variability が結果に与える影響は明確ではない．また，中心的な評価対象は CheXzero という1つの VLM 実装であり，人間評価に参加した radiologists も3人に限られる．

## 関連概念

- [[Vision_Language_Model_Fairness]]
- [[Foundation_Model_Fairness]]
- [[Underdiagnosis_Bias]]
- [[Race_Recognition_In_Medical_Images]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Subgroup_Performance_Monitoring]]
