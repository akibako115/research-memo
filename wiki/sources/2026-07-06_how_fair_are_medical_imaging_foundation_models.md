---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_how_fair_are_medical_imaging_foundation_models.pdf"
---

# How Fair are Medical Imaging Foundation Models?

この論文は，medical imaging foundation models の subgroup fairness を，pre-training method，pre-training data source，model architecture の違いから包括的に評価する．対象は MAE，Medical MAE，MoCov3，Medical MoCov3，BiT，REMEDIS の6モデルであり，CheXpert の chest X-ray multi-label classification に fine-tune して，sex と race に関する fairness gap を測る．

主な発見は，medical images で pre-training した foundation models は overall performance が高い一方，natural images で pre-training した model より subgroup fairness が一貫して悪い，という trade-off である．fine-tuning dataset を balanced にしても pre-training stage 由来の bias は完全には消えず，foundation model の pre-training design と evaluation に fairness を組み込む必要があると主張している．

## Foundation models

6つの foundation models を比較する．pre-training methods は supervised learning，masked self-supervised learning，contrastive self-supervised learning を含み，pre-training data は natural images と medical images に分かれる．

| Model | Architecture | Method | Type | Pre-training data |
| --- | --- | --- | --- | --- |
| MAE | ViT-B | self-supervised | masked | ImageNet-1K |
| MAE (M) | ViT-B | self-supervised | masked | ChestXray14，CheXpert，MIMIC-CXR |
| MoCov3 | ViT-B | self-supervised | contrastive | ImageNet-1K |
| MoCov3 (M) | ViT-B | self-supervised | contrastive | ChestXray14，CheXpert |
| BiT | ResNet152 | supervised | - | ImageNet-21K |
| REMEDIS | ResNet152 | self-supervised | contrastive | CheXpert，MIMIC-CXR |

Medical MoCov3 は，medical imaging 用の MoCov3 foundation model がなかったため，ChestXray14 と CheXpert で著者らが pre-training して作成している．また，medical imaging pre-training の量を増やす効果を見るため，MAE を medical imaging datasets のサイズを変えて pre-training している．

## Fine-tuning

foundation models は，chest radiographs から複数 pathology を識別する multi-label classification task に fine-tune される．Medical MAE の fine-tuning settings に従い，single V100 GPU で end-to-end fine-tuning する．optimizer は AdamW，`beta1=0.9`，`beta2=0.95`，weight decay 0.05，base learning rate 2.5e-4，warm-up 5 epochs，cosine annealing，layer-wise learning rate decay 0.55，RandAug magnitude 6，DropPath rate 0.2 である．

batch size は ResNet152 models (BiT，REMEDIS) で32，ViT-B models (MAE，Medical MAE，MoCov3，Medical MoCov3) で128である．medical imaging pre-trained models は natural imaging pre-trained models より速く収束するため，Medical MAE，Medical MoCov3，REMEDIS はそれぞれ100，100，20 epochs，MAE，MoCov3，BiT は200，200，30 epochs fine-tune する．

## Dataset splits and metrics

fine-tuning は CheXpert subset で行う．この subset は 127,118 chest X-ray scans，42,884 patients からなり，training 76,205，validation 12,673，test 38,240 に分割され，患者 overlap はない．test set は demographic representation が balanced になるように resample される．multi-label classification なので，各 disease について all diseases across all subgroups の prevalence が等しくなるように separate test set を作る．

performance metric は 14 pathologies の mean AUC である．fairness metric は fairness gap であり，worst-performing subgroup と best-performing subgroup の AUC 差として定義される．sex と race について個別に fairness gap を報告する．plot では higher is better に揃えるため fairness gap を fairness score に変換するが，表では lower fairness gap が望ましい．

## Natural vs medical pre-training

pre-training は，models initialized from scratch と比べると classification performance と fairness の両方を改善する．一方，natural imaging pre-training と medical imaging pre-training を比べると，medical imaging pre-training は Chest X-ray classification performance をより大きく改善するが，subgroup fairness は悪化する．

sex と race の両 protected attributes で，natural images で pre-training した foundation models が最も fair だった．medical images で pre-training した models は，natural images で pre-training した counterparts より fairness が一貫して悪く，race fairness では scratch baseline より悪い場合もあった．

著者らは，CheXpert の gender split が 59/41 (Male/Female) である一方，racial split が 78/15/7 (White/Asian/Black) とより skewed であることから，medical datasets で pre-training した models が sex fairness より race fairness で悪化しやすい可能性を指摘している．

## Contrastive vs masked SSL

classification performance では，masked SSL が contrastive SSL より一貫して高かった．しかし fairness では，pre-training data source によって傾向が変わる．natural images で pre-training した場合，masked SSL は sex と race の両方で contrastive SSL より fair だった．一方，medical images で pre-training した場合，contrastive SSL の方が fair であり，masked SSL は race fairness で scratch baseline より悪い場合があった．

著者らは，masked pre-training が medical pre-training data の subgroup imbalance に特に影響されやすいと解釈している．contrastive pre-training は each image を separate class のように扱い，同じ subgroup 内の画像とも contrast するため，skewed racial splits の悪影響を受けにくい可能性があると述べている．

## Pre-training data volume / epochs

medical imaging pre-training の量を増やすと，overall performance と subgroup fairness の両方が改善した．MAE を ChestXray14，CheXpert，ChestXray14 + CheXpert で pre-train した結果は次の通りである．

| Pre-training data | AUC | Sex FG | Race FG |
| --- | ---: | ---: | ---: |
| ChestXray14 | 79.97 | 1.58 | 3.09 |
| CheXpert | 80.98 | 1.49 | 2.85 |
| ChestXray14 + CheXpert | 81.38 | 1.29 | 2.82 |

pre-training epochs を増やした場合も，AUC と fairness gap が改善する．200 epochs では AUC 79.2，Sex FG 1.54，Race FG 3.56，400 epochs では AUC 79.9，Sex FG 1.44，Race FG 3.11，800 epochs では AUC 79.9，Sex FG 1.43，Race FG 3.03 である．

CheXpert dataset fraction を30%から100%へ増やす実験では，AUC 80.6 から 81.0，Sex FG 1.53 から 1.49，Race FG 2.86 から 2.85 へ改善した．

## Balanced fine-tuning

pre-training と fine-tuning の bias を切り分けるため，training set を race subgroups が同数になるように resampling した balanced fine-tuning dataset を作る．White subgroup が sex でも最も unbalanced なので，White の undersampling により sex もより balanced になる．

balanced fine-tuning は racial fairness を改善し，all foundation models が scratch baseline より良い racial fairness を示した．特に medical images で masked SSL pre-training した models は，medical pre-training data の subgroup imbalance に影響されやすいため，balanced fine-tuning の benefit が大きい．

しかし，balanced fine-tuning 後も，natural image pre-trained models は多くの場合 medical image pre-trained models より fair であり，fine-tuning dataset の balancing だけでは pre-training stage 由来の bias を完全には除去できない．

## Subgroup-level analysis

sex subgroup では，6つすべての foundation models で female patients subgroup が一貫して underperform した．著者らは，pre-training datasets における female patients の under-representation が一因かもしれないが，それだけが原因かは不明だとしている．

race subgroup では，CheXpert の racial distribution が 78/15/7 (White/Asian/Black) であることを踏まえ，medical image pre-trained models は frequent subgroups (White, Asian) で performance が向上し，natural image pre-trained models は minority subgroup (Black) で performance が向上する傾向があった．medical datasets の skewed racial splits は majority subgroups を過度に favor する可能性がある．

disease-stratified analysis では，多くの diseases が male patients でより良く診断される一方，Pleural Effusion は prevalence が male / female で似ているにもかかわらず female patients で一貫して良く診断される anomaly として報告されている．race では，多くの pathologies で，all six foundation models が同じ racial subgroup で overperform / underperform する傾向があった．Edema は sex と race の両方で最も fair に診断される condition とされる．

## Ensembles

foundation model ensembles では，medical image pre-trained models の ensemble が best overall performance を示し，natural image pre-trained models の ensemble は sex fairness に優れる．all foundation models ensemble は，AUC 81.4，Sex FG 1.12，Race FG 2.84 で，performance と fairness の balanced trade-off を示した．

Table 3 では，Medical Imaging ensemble が AUC 81.6，Sex FG 1.39，Race FG 3.12，Natural Imaging ensemble が AUC 80.4，Sex FG 0.78，Race FG 2.94，All Foundation Models が AUC 81.4，Sex FG 1.12，Race FG 2.84 と報告されている．

## Limitations

本研究は sex と race に関する subgroup fairness を扱うが，Asian ethnicities を一括するなど，dataset labels の粗さによりより細かい subgroup analysis はできていない．将来の研究では，より granular ethnic classifications を持つ public datasets が必要である．

また，本論文は Chest X-ray diagnosis に焦点を当てており，X-ray から Fundus，Chest X-ray から Knee X-ray のような modality / anatomical region transfer で foundation models が fairness にどう影響するかは future work として残る．

## 関連概念

- [[Foundation_Model_Fairness]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Demographic_Imbalance]]
- [[Race_Recognition_In_Medical_Images]]
- [[Subgroup_Performance_Monitoring]]
