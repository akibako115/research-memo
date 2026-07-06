---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_gender_imbalance_medical_imaging_biased_classifiers.pdf"
---

# Gender Imbalance in Medical Imaging Datasets Produces Biased Classifiers for Computer-aided Diagnosis

この論文は，computer-aided diagnosis (CAD) 用の医療画像 dataset における gender imbalance が，under-represented gender に対する分類性能低下を生むかを検証する．対象は胸部 X 線の multi-label classification であり，NIH ChestX-ray14 と CheXpert を用いて，training data の male/female 比率を操作した実験を行う．

主張は，target class imbalance だけでなく，target label とは別の demographic variable である gender imbalance も，医療画像 classifier の bias source になるという点である．著者らは，minimum balance が満たされないと under-represented gender で AUC が一貫して低下し，balanced and diverse dataset が両 gender に対して最良の generalization を与えると報告している．

## 問題設定

医療画像 AI では，より高精度な CAD algorithm の開発に多くの努力が向けられている一方，dataset がどのように収集され，その偏りが model performance にどう影響するかは十分に扱われていない．本論文は，sex/gender analysis を医療画像 dataset 設計へ組み込む必要性を示すために，gender imbalance の影響を実験的に調べる．

著者らは，class imbalance ではなく，pathology label とは別の demographic variable である gender の imbalance に注目する．つまり「ある疾患の陽性例が少ない」問題ではなく，「training data 内で female または male images が少ない」ことが，疾患分類性能に影響するかを調べている．

## Dataset

| Dataset | 内容 | gender/sex 情報 |
| --- | --- | --- |
| NIH ChestX-ray14 | 112,120 chest X-ray images，30,805 patients，14 thoracic diseases | male 63,340 images (56.5%)，female 48,780 images (43.5%) |
| CheXpert | 224,316 chest radiographs，65,240 patients | 約60% male，約40% female |

NIH ChestX-ray14 の labels は radiology reports に対する automatic NLP analysis によって作成されている．CheXpert の uncertainty labels は，original paper の U-Zeros approach に従い negative と解釈されている．

著者らは，元 dataset の demographic variable 名に従って gender という語を使うが，X 線画像には anatomical attributes が反映されるため，SAGER guidelines に照らすと sex という語の方が正確かもしれない，とも述べている．

## Model

CAD system は CNN による multi-label classifier として実装される．主な結果は DenseNet-121 によるもので，14 disease labels に対応する14-dimensional output を持ち，最後に sigmoid を適用する．ImageNet pretraining を用い，Adam optimizer，batch size 32，initial learning rate 0.001 で end-to-end training する．

著者らは DenseNet-121 だけでなく，ResNet と Inception-v3 でも評価し，観察された傾向が異なる neural architectures でも一般化することを確認している．

## 実験設計

multi-label X-ray images に対して，male/female folds が pathology ごとに同じ number of images を持つように random splits を構成する．これにより，observed bias が pathology class distribution の違いから来る可能性を減らす．

実験では，training data の gender ratio を操作する．

| 設定 | 内容 |
| --- | --- |
| 0/100% | male-only または female-only training |
| 25/75% | minority gender が25%，majority gender が75% |
| 50/50% | gender-balanced training |

NIH ChestX-ray14 では各 split が 48,568 images，CheXpert では各 split が 27,147 images を含む．同じ実験を異なる random splits で20回実行し，test phase では male patients と female patients を別々に評価する．classification performance は AUC で測る．

## 主な結果

fully imbalanced datasets では，male-only training model を female test images で評価した場合，および female-only training model を male test images で評価した場合に，一貫した性能低下が観察された．この傾向は，3つの deep learning architectures と2つの X-ray datasets で確認された．

intermediate imbalance でも，minority gender の性能低下が見られた．著者らは，25%/75% imbalance ratio でも，全 disease 平均で minority class の performance が，50%/50% balanced dataset で学習した model より有意に低いと報告している．

一方で，balanced dataset で学習した model と，同じ gender のみで学習した extremely imbalanced model を同じ gender の test set に適用した場合には，有意差は見られなかった．著者らは，diverse and balanced dataset が両 gender に対して最良の performance を与え，diversity が additional information を提供して AI system の generalization capability を高めると結論づけている．

## 規制・dataset 設計への示唆

著者らは，national agencies が CAD systems を regulation / approval する際に，gender balance と diversity に関する explicit recommendations を含めるべきだと述べている．例として，FDA には clinical trials や medical devices の sex/gender issues に関する document はあるが，medical CAD systems の market approval guideline では，sampled population を記述すべき relevant demographic variables として gender/sex が明示されていないと指摘する．

また，医療画像 community でも，同様の問題がある．一部 dataset は subject-level gender/sex information を提供するが，多くの public datasets は patient-level gender/sex information を含んでいない．著者らは，MIMIC-CXR や REFUGE を例として挙げ，biomedical image analysis grand challenges の database design recommendation にも sex/gender demographic information の重要性が明示されていないと述べている．

## 解釈

CNN は task に有用な representation を学習するが，male images と female images の間には structural changes があり，data distribution shift が生じる．この distribution shift が，opposite gender test set での performance decrease を説明すると著者らは述べる．gender-balanced dataset の構築が難しい場合には，domain adaptation 的な algorithmic solution が必要になる可能性がある．

## Data / code availability

NIH ChestX-ray14 は公開 dataset として提供されており，CheXpert も Stanford ML Group の competition page から利用できる．元の CNN code は `brucechou1983/CheXNet-Keras`，本論文の modified code，auxiliary scripts，data splits，additional results は `N-Nieto/GenderBias_CheXNet` で公開されている．

## 関連概念

- [[Demographic_Imbalance]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Subgroup_Performance_Monitoring]]
- [[Bias_Amplification]]
- [[Data_Imbalance]]
