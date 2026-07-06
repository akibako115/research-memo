---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_addressing_fairness_issues_deep_learning_medical_image_analysis.pdf"
---

# Addressing fairness issues in deep learning-based medical image analysis: a systematic review

この systematic review は，deep learning-based medical image analysis (MedIA) における fairness 研究を，fairness evaluation と unfairness mitigation に分けて整理する．PRISMA guidelines に基づいて Scopus，PubMed，arXiv，Google Scholar を検索し，687 papers から最終的に63 studies を抽出している．抽出対象は2015-2023年の英語論文で，deep learning を用いた medical image analysis の fairness methodology を扱うものに限定される．

主な貢献は，MedIA fairness の基本指標，研究領域，mitigation taxonomy，利用可能 dataset，そして clinical fairness と mathematical fairness のズレをまとめた点である．著者らは，fairness は単に数式上の parity ではなく，臨床的因果関係，subgroup-specific disease prevalence，annotation practice，deployment domain gap を含めて扱う必要があると主張する．

## Group fairness の基本

多くの MedIA fairness 研究は group fairness を使う．subject を `Si = {Xi, Yi, Ai}` とし，`Xi` は image，`Yi` は target label，`Ai` は protected sensitive attribute である．test set を sensitive attribute によって subgroup に分け，subgroup-wise metric の差を fairness disparity として計算する．

| Criterion | 要求する parity | 医療画像での注意 |
| --- | --- | --- |
| Demographic Parity | prediction rate parity | disease prevalence が subgroup で異なる場合，臨床的に不自然になりうる |
| Accuracy Parity | accuracy parity | subgroup prevalence と threshold に影響される |
| Equalized Odds | TPR と FPR の parity | fixed operating point の error disparity を見る |
| Equal Opportunity | TPR parity | underdiagnosis や sensitivity の偏りに近い |

著者らは，これらの fairness criteria は同時に満たせない場合があり，task に応じて適切な基準を選ぶ必要があると述べる．また，1つの grouping scheme では公平でも，別の grouping scheme では不公平になりうる．例として，sex では demographic parity を満たしても，race では満たさない状況が示されている．

## 研究動向

fair MedIA 研究は2019年頃から増え，年6-7本程度のペースで増加している．対象 modality は Brain MRI，Dermatology，Chest X-ray が多い．task は classification と segmentation が中心で，anomaly detection や regression への拡張もある．sensitive attributes は sex，age，race，skin tone が中心である．

レビュー対象の63 studies は，fairness evaluation 26件，pre-processing mitigation 15件，in-processing mitigation 24件，post-processing mitigation 4件に分類される．重複する研究があるため，カテゴリ数の合計は63を超える．

## Fairness evaluation

fairness evaluation は，subgroup performance comparison によって unfairness の存在を調べる研究と，unfairness source / mechanism を探る研究に分かれる．多くの benchmark studies は，複数 architecture，複数 attribute ratio，複数 modality で subgroup utility disparity を測る．

fairness source discovery では，visual disparity，shortcut learning，subgroup separability，label annotation procedure，image quality，uncertainty などが調べられる．たとえば，sex-inverted X-ray 生成によって sex attribute に関わる領域を探る研究，chest X-ray の drain が shortcut learning を誘発する研究，MRI reconstruction の estimated total intracranial volume / normalized whole brain volume が unfairness と関係する研究が挙げられる．

## Unfairness mitigation taxonomy

mitigation は pre-processing，in-processing，post-processing に分けられる．

| Category | Subtype | 考え方 |
| --- | --- | --- |
| pre-processing | re-distribution | resampling / mini-batch balancing で subgroup representation を調整する |
| pre-processing | harmonization | input image から sensitive information を除去・正規化する |
| pre-processing | aggregation | external dataset や EHR など外部情報で補う |
| pre-processing | synthesis | generative models で不足 subgroup / counterfactual samples を作る |
| in-processing | adversarial | gradient reversal などで latent space から sensitive information を減らす |
| in-processing | constraints | GroupDRO，differentiable fairness proxy，bias-balanced Softmax などを loss に加える |
| in-processing | disentanglement | feature を task-related / task-agnostic 部分に分ける |
| in-processing | contrastive | same target class / different sensitive attribute の feature 距離を縮める |
| in-processing | adapters / PEFT | adapter や parameter-efficient fine-tuning で fairness を調整する |
| post-processing | calibration | subgroup-specific threshold などで output を調整する |
| post-processing | pruning | fairness に関係する neuron / feature を削る |

in-processing の fairness constraints は，over-parameterization や overfitting を招き，sex と age それぞれでは公平でも sex x age の組み合わせで不公平になる fairness gerrymandering を起こしうると述べられている．

## Sources of unfairness

著者らは，unfairness source を data，model，deployment に分ける．

| Pipeline stage | Source | Potential solution |
| --- | --- | --- |
| data | skewed distribution | data augmentation / aggregation |
| data | anatomy difference | causal image synthesis |
| data | annotation noise / annotation preference | multi-annotator involvement |
| model | ERM-based model selection | DTO-based model selection |
| model | spurious correlation | confounder removal |
| model | amplification of existing unfairness | fairness-aware training / monitoring |
| deployment | inherited bias from pre-training data | model pruning / fairness constraints |
| deployment | domain gap | domain adaptation |

data stage では，diagnosis label と sensitive attributes の skewed distribution，subgroup 間の anatomical differences，clinician annotation preference が問題になる．model stage では，overall performance 最大化が subgroup gap を大きくする可能性や，spurious correlation の利用，data unfairness の amplification が挙げられる．deployment stage では，pre-trained model が pre-training data の bias を引き継ぐことと，開発環境と運用環境の domain gap が問題になる．

## Clinical fairness と mathematical fairness のズレ

著者らは，AI scientist と clinician の間で fairness の捉え方が異なることを強調する．AI fairness では，DP，AP，EqOdds など手で設計した metric の数値差を小さくすることが多い．一方で，臨床では数値上の equality が必ずしも treatment equity を意味しない．

たとえば demographic parity は，各 subgroup が同じ確率で disease positive と予測されることを求めるが，実際の疾患は age や sex と関係することがある．また，anatomical differences によって診断難易度が subgroup ごとに異なる場合，完全な numerical parity を強制すると臨床的 causal relationship を壊す可能性がある．したがって，どの attribute を sensitive attribute として扱うか，どの程度の numerical difference を unfairness とみなすかは，臨床文脈に基づいて決める必要がある．

## Foundation models

LLM，CLIP 系モデル，SAM 系モデルのような foundation models は，zero-shot / few-shot performance が高い一方，training sets がアクセス不能なことが多く，healthcare に採用する前に subgroup utility を確認する必要がある．

LLM では pre-training corpus 由来の unfairness や，pre-training task と downstream task の domain gap が問題になる．CLIP 系モデルでは，text-image alignment における sensitive attributes と target label の spurious relations が bias を生みうる．SAM 系モデルでは，training images の geographic distribution bias が medical fine-tuned variants に伝播しうる．

foundation models は parameter 数が大きく，再学習コストが高いため，従来の mitigation technique をそのまま適用しにくい．著者らは，feature space perturbation や input image editing など，foundation model 向けの mitigation が必要だと述べる．

## 結論

fair MedIA は，AI scientists，clinicians，ethicists，governments の協力を必要とする．AI scientists は数理的 fairness の限界を理解し，clinicians は disease diagnosis と patient metadata の causal relationship を明らかにし，government は clinical AI guidelines に fairness consideration を組み込む必要がある．

この review の結論は，fairness evaluation と unfairness mitigation は MedIA の急速に成長する研究領域であり，sex，age，race，skin tone などにまたがる health equity のために継続的に扱うべき，というものである．

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Equalized_Odds]]
- [[Foundation_Model_Fairness]]
- [[Demographic_Imbalance]]
- [[Subgroup_Performance_Monitoring]]
