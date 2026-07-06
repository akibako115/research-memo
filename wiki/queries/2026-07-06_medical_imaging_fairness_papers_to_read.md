# 最初に raw に取り込むべき論文リスト

作成日: 2026-07-06
更新日: 2026-07-06

## 背景

この wiki の研究方針は，Hypernetwork や画像 + テーブルデータのマルチモーダル学習を，医療画像分類の subgroup reliability / fairness と接続して整理することである．

先に `wiki/queries/` に投入した Deep Research レポートは，おおまかに次の3系統に分かれていた．

- `2026-07-06_medical_imaging_latent_subgroup_fairness_deep_research.md`
- `2026-07-06_medical_imaging_intersectional_fairness_deep_research.md`
- `2026-07-06_hypernetwork_image_tabular_medical_multimodal_deep_research.md`

したがって raw に最初に取り込む論文も，単一の読む順リストではなく，以下のトピックごとに分けて管理する．

1. 医療画像 Fairness の基礎
2. 潜在弱集団・hidden stratification
3. 複数属性・intersectional fairness
4. 画像 + テーブルデータ / Hypernetwork 系

## 1. 医療画像 Fairness の基礎

目的:

医療画像分類でどのような subgroup gap，underdiagnosis，protected attribute leakage，OOD fairness 問題があるかを押さえる．このトピックは全体の土台であり，最初に raw 化する優先度が高い．

### 最初に raw に入れる

#### Underdiagnosis bias of artificial intelligence algorithms applied to chest radiographs in under-served patient populations

- 出版: Nature Medicine, 2021
- URL: https://www.nature.com/articles/s41591-021-01595-0
- raw 保存候補: `raw/papers/2026-07-06_underdiagnosis_bias_chest_radiographs.md`

読む理由:

胸部 X 線診断モデルにおける underdiagnosis bias を，性別，年齢，人種，保険種別，交差属性で監査した代表的研究．医療画像 Fairness の問題設定を理解する起点になる．

#### AI recognition of patient race in medical imaging: a modelling study

- 出版: The Lancet Digital Health, 2022
- URL: https://www.thelancet.com/journals/landig/article/PIIS2589-7500(22)00063-2/fulltext
- raw 保存候補: `raw/papers/2026-07-06_ai_recognition_patient_race_medical_imaging.md`

読む理由:

医療画像から race などの protected attribute が推定できてしまうことを示す重要論文．患者属性を条件として明示的に使う研究では，属性が「入力しなくても漏れる」問題を理解する必要がある．

#### MEDFAIR: Benchmarking Fairness for Medical Imaging

- 出版: ICLR, 2023
- URL: https://arxiv.org/abs/2210.01725
- raw 保存候補: `raw/papers/2026-07-06_medfair_benchmarking_fairness_medical_imaging.md`

読む理由:

医療画像 Fairness の評価におけるデータセット，fairness metric，bias mitigation，model selection criterion を統一的に扱うベンチマーク．今後の実験設計の基準にしやすい．

#### The limits of fair medical imaging AI in real-world generalization

- 出版: Nature Medicine, 2024
- URL: https://www.nature.com/articles/s41591-024-03113-4
- raw 保存候補: `raw/papers/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization.md`

読む理由:

in-distribution で公平に見えるモデルが，外部施設・外部分布では公平性を維持できない問題を扱う．subgroup reliability を単一データセット内の gap だけで判断しないために重要．

#### How Fair are Medical Imaging Foundation Models?

- 出版: ML4H / PMLR, 2023
- URL: https://proceedings.mlr.press/v225/khan23a.html
- raw 保存候補: `raw/papers/2026-07-06_how_fair_are_medical_imaging_foundation_models.md`

読む理由:

ImageNet 初期化，医療画像 pretraining，fine-tuning protocol が subgroup fairness に与える影響を考える材料になる．今回の研究で ResNet baseline や pretraining bias を扱うための前提として重要．

### 次点

#### Gender imbalance in medical imaging datasets produces biased classifiers for computer-aided diagnosis

- 出版: PNAS, 2020
- URL: https://www.pnas.org/doi/10.1073/pnas.1919012117
- raw 保存候補: `raw/papers/2026-07-06_gender_imbalance_medical_imaging_biased_classifiers.md`

読む理由:

データセット内の gender imbalance が classifier bias を生むことを示す基本論文．データ分布と subgroup performance の関係を整理する補助線になる．

#### Addressing fairness issues in deep learning-based medical image analysis: a systematic review

- 出版: npj Digital Medicine, 2024
- URL: https://www.nature.com/articles/s41746-024-01276-5
- raw 保存候補: `raw/papers/2026-07-06_addressing_fairness_issues_deep_learning_medical_image_analysis.md`

読む理由:

evaluation / mitigation の分類を作るための地図として使える．個別論文を読んだ後で，全体像を補正する用途がよい．

## 2. 潜在弱集団・hidden stratification

目的:

既知の protected attribute だけでは見えない failure mode，latent subgroup，hidden cohort，systematic error slice を理解する．今回の研究では，属性条件付きモデルが既知 subgroup だけでなく潜在弱集団にどう影響するかも重要になる．

### 最初に raw に入れる

#### Hidden Stratification Causes Clinically Meaningful Failures in Machine Learning for Medical Imaging

- 出版: ML4H at NeurIPS, 2019
- URL: https://arxiv.org/abs/1909.12475
- raw 保存候補: `raw/papers/2026-07-06_hidden_stratification_medical_imaging.md`

読む理由:

医療画像で hidden stratification という問題設定を明確化した起点．平均性能や既知属性 subgroup だけでは，臨床的に重要な失敗群を見逃しうることを示す．

#### No Subclass Left Behind: Fine-Grained Robustness in Coarse-Grained Classification

- 通称: GEORGE
- 出版: NeurIPS, 2020
- URL: https://papers.neurips.cc/paper_files/paper/2020/file/e0688d13958a19e087e123148555e4b4-Paper.pdf
- raw 保存候補: `raw/papers/2026-07-06_no_subclass_left_behind_george.md`

読む理由:

latent subclass を埋め込み空間から推定し，proxy group に対して GDRO を行う代表的研究．医療画像専用ではないが，latent subgroup discovery と robust optimization をつなぐ基盤になる．

#### Domino: Discovering Systematic Errors with Cross-Modal Embeddings

- 出版: ICLR, 2022
- URL: https://openreview.net/forum?id=FPCMqjI0jXN
- raw 保存候補: `raw/papers/2026-07-06_domino_systematic_errors_cross_modal_embeddings.md`

読む理由:

cross-modal embedding を使って coherent な underperforming slice を見つける研究．医療画像における failure slice discovery，説明，human-in-the-loop 監査の設計に関係する．

### 次点

#### Subgroup Performance Analysis in Hidden Stratifications

- 出版: MICCAI, 2025
- raw 保存候補: `raw/papers/2026-07-06_subgroup_performance_analysis_hidden_stratifications.md`

読む理由:

医療画像で subgroup discovery を performance monitoring に接続した比較的新しい研究．CheXpertPlus などで，demographic metadata より大きな performance gap を持つ潜在 subgroup を報告している．

#### Fairness Beyond Demographics: Optimizing Performance Across Appearance-Based Hidden Cohorts in Medical Imaging

- 通称: LHCF
- 出版: arXiv, 2026
- raw 保存候補: `raw/papers/2026-07-06_fairness_beyond_demographics_hidden_cohorts.md`

読む理由:

人口統計ラベルを使わず，appearance-based hidden cohorts を発見して fairness loss を最適化する方向性．重要だが新しい preprint なので，最初の土台ではなく発展候補として扱う．

## 3. 複数属性・intersectional fairness

目的:

単一属性では公平に見えても，sex × race，age × sex，race × insurance などの交差 subgroup で性能差が増幅される問題を理解する．今回の研究で患者属性を使うなら，属性を単独ではなく組合せとして扱う必要がある．

### 最初に raw に入れる

#### On Fairness of Medical Image Classification with Multiple Sensitive Attributes via Learning Orthogonal Representations

- 通称: FCRO
- 出版: IPMI, 2023
- URL: https://arxiv.org/abs/2301.01481
- raw 保存候補: `raw/papers/2026-07-06_fcro_multiple_sensitive_attributes_medical_image_classification.md`

読む理由:

医療画像分類で複数 sensitive attributes を明示的に扱う代表的研究．属性表現と診断表現の関係，multi-sensitive fairness の設計を考える材料になる．

#### Improving model fairness in image-based computer-aided diagnosis

- 出版: Nature Communications, 2023
- URL: https://www.nature.com/articles/s41467-023-41974-4
- raw 保存候補: `raw/papers/2026-07-06_improving_model_fairness_image_based_cad.md`

読む理由:

intersectional subgroup を含む fairness 改善を，pairwise fairness の観点から扱う研究．AUC だけではなく，臨床判断に近い ranking / operating point の公平性を見るために重要．

#### FairREAD

- 出版: Medical Image Analysis, 2025
- raw 保存候補: `raw/papers/2026-07-06_fairread_demographic_refusion_medical_image_classification.md`

読む理由:

demographic-invariant 表現を作った後に demographic information を controlled re-fusion する設計が，今回の「属性を消すのではなく条件として使う」方針と近い．属性利用の是非を考える上で有用．

### 次点

#### Worst-Group Equalized Odds Regularization for Multi-Attribute Fair Medical Image Classification

- 出版: arXiv, 2026
- raw 保存候補: `raw/papers/2026-07-06_worst_group_equalized_odds_multi_attribute_medical_image_classification.md`

読む理由:

交差群を直接列挙せず，各 mini-batch で属性横断的に最悪群を選ぶ regularization．operating-point ベースの fairness を扱う発展候補．新しい preprint なので優先度は次点．

#### Demographic Bias of Expert-Level Vision-Language Foundation Models in Medical Imaging

- 出版: Science Advances, 2025
- raw 保存候補: `raw/papers/2026-07-06_demographic_bias_vision_language_foundation_models_medical_imaging.md`

読む理由:

医療画像 VLM の intersectional bias を扱う研究．自分の主軸が ResNet / conditional model である間は次点だが，foundation model との接続を考える際に有用．

## 4. 画像 + テーブルデータ / Hypernetwork 系

目的:

患者属性や臨床テーブルデータを，画像モデルにどのように条件付けるかを理解する．Fairness 論文だけでは「属性をモデルに入れる設計空間」が弱いため，FiLM，DAFT，HyperFusion の系譜を別トピックとして追う．

### 最初に raw に入れる

#### DAFT: A universal module to interweave tabular data and 3D images in CNNs

- 出版: NeuroImage, 2022
- URL: https://www.sciencedirect.com/science/article/pii/S1053811922006218
- raw 保存候補: `raw/papers/2026-07-06_daft_interweave_tabular_data_3d_images_cnns.md`

読む理由:

画像特徴と tabular data から scale / offset を生成し，feature map を条件付ける代表的手法．Hypernetwork より軽量な条件付き modulation の基準として重要．

#### Combining 3D Image and Tabular Data via the Dynamic Affine Feature Map Transform

- 出版: MICCAI, 2021
- URL: https://arxiv.org/abs/2103.06334
- raw 保存候補: `raw/papers/2026-07-06_dynamic_affine_feature_map_transform_3d_image_tabular.md`

読む理由:

DAFT の会議版．問題設定，baseline 比較，アブレーションが簡潔にまとまっており，実装・設計を把握する入口として有用．

#### HyperFusion: A Hypernetwork Approach to Multimodal Integration of Tabular and Medical Imaging Data for Predictive Modeling

- 出版: Medical Image Analysis, 2025
- URL: https://arxiv.org/abs/2403.13319
- raw 保存候補: `raw/papers/2026-07-06_hyperfusion_hypernetwork_multimodal_tabular_medical_imaging.md`

読む理由:

医療画像 + tabular data の統合に explicit hypernetwork を使う中核論文．今回の研究で HyperAdapt に依存しすぎず，より広い「患者文脈で画像モデルを条件付ける」文脈を作るために重要．

### 次点

#### Benefits of Linear Conditioning with Metadata for Image Segmentation

- 出版: MIDL, 2021
- URL: https://arxiv.org/abs/2102.09582
- raw 保存候補: `raw/papers/2026-07-06_linear_conditioning_metadata_image_segmentation.md`

読む理由:

FiLM 的な metadata conditioning が segmentation mask をどう変えるかを，条件反実仮想的な metadata swap で検証している．条件付きモデルの解析研究として有用．

#### HyperNetworks

- 出版: ICLR, 2017
- URL: https://arxiv.org/abs/1609.09106
- raw 保存候補: `raw/papers/2026-07-06_hypernetworks.md`

読む理由:

ネットワークが別のネットワークの重みを生成するという発想の原典．医療応用論文を読む前に，狭義の hypernetwork の定義を確認するために使う．

#### FiLM: Visual Reasoning with a General Conditioning Layer

- 出版: AAAI, 2018
- URL: https://arxiv.org/abs/1709.07871
- raw 保存候補: `raw/papers/2026-07-06_film_visual_reasoning_general_conditioning_layer.md`

読む理由:

feature-wise affine conditioning の基礎論文．DAFT や FiLMed U-Net を，Hypernetwork というより条件付き modulation の系譜として理解するために必要．

## 最初の投入順

一気に全部 raw 化するより，次の順に入れると source / article 化しやすい．

1. 医療画像 Fairness の基礎から 5 本
2. 潜在弱集団・hidden stratification から 3 本
3. 複数属性・intersectional fairness から 2-3 本
4. 画像 + テーブルデータ / Hypernetwork 系から 3 本

この順序にすると，まず「何を公平性として測るか」を固め，次に「既知属性だけで十分か」を疑い，その後で「属性をどう条件としてモデルに入れるか」を検討できる．

## raw 追加後に作るべき source / article 候補

raw に保存した後は，各論文ごとに `wiki/sources/` へ source を作成する．その後，複数 source を横断して以下の記事候補を育てる．

- `[[Medical_Imaging_Fairness]]`
- `[[Subgroup_Reliability]]`
- `[[Underdiagnosis_Bias]]`
- `[[Protected_Attribute_Leakage]]`
- `[[Hidden_Stratification]]`
- `[[Latent_Subgroup_Discovery]]`
- `[[Intersectional_Fairness]]`
- `[[Multiple_Sensitive_Attributes]]`
- `[[Fairness_Metrics_for_Medical_Imaging]]`
- `[[Medical_Imaging_Foundation_Model_Fairness]]`
- `[[Image_Tabular_Multimodal_Learning]]`
- `[[Conditional_Modulation]]`
- `[[Hypernetwork_for_Medical_Imaging]]`
- `[[FiLM]]`
- `[[DAFT]]`

## 注意

このリストは raw に原文を保存するための候補であり，この query 自体は一次情報ではない．実際の source / article 作成時には，必ず raw に保存された原文を入力として使う．

Deep Research レポートに含まれる主張は，source / article に昇格する前に，必ず raw に保存した一次情報で確認する．
