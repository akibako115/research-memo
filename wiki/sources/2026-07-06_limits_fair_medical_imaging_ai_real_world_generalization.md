---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_limits_fair_medical_imaging_ai_real_world_generalization.pdf"
---

# The limits of fair medical imaging AI in real-world generalization

この論文は，medical imaging AI が demographic shortcuts を使うか，shortcut removal が fairness を改善するか，そしてその改善が out-of-distribution (OOD) deployment で維持されるかを大規模に調べる．中心は chest X-ray で，MIMIC-CXR，CheXpert，NIH，SIIM，PadChest，VinDr の6 dataset を使い，dermatology と ophthalmology でも確認する．

主な結論は，demographic shortcut removal は in-distribution (ID) では fairness gap を下げて「locally optimal」な model を作れるが，その fairness は OOD へ一貫して転移しない，というものである．OOD fairness では，ID fairness gap を最小にする model よりも，ID representation に demographic information を少なく encode する model を選ぶ方が良い場合が多い．

## 問いと対象

論文は4つの問いを扱う．

1. disease classification model は demographic information を shortcut として使い，fairness gap を生むか．
2. shortcut removal / robustness methods は ID で fair な model を作れるか．
3. ID で fair な model は OOD deployment でも fair か．
4. OOD fairness を保つには，ID data だけでどの model selection criterion を使うべきか．

CXR task は `No Finding`，`Cardiomegaly`，`Effusion`，`Pneumothorax` の4つである．dermatology では ISIC の `No Finding`，ophthalmology では ODIR の `Retinopathy` を使う．CXR では race，sex，age，sex/race intersection を評価する．MIMIC-CXR 上では，4 tasks，4 demographic attributes，6 algorithms，12 hyperparameter settings，3 random seeds の組み合わせで3,456 models を training している．

## Fairness metric

screening model の clinical harm に合わせ，class-conditioned error rate を使う．`No Finding` では，疾患あり患者を健康と誤って扱う false positive が delayed treatment につながるため FPR gap を見る．他の disease labels では false negative が underdiagnosis なので FNR gap を見る．この equality は Equal Opportunity / Equalized Odds の文脈に置かれる．

## Demographic encoding と fairness gap

各 disease model の feature extractor を frozen にし，penultimate representation から sensitive attributes を予測する head を学習して，representation に含まれる demographic information を測る．ERM model の representation は，age，race，sex，sex/race intersection を高い AUROC で予測できた．この傾向は CXR だけでなく dermatology と ophthalmology でも確認される．

さらに，attribute prediction AUROC と fairness gap は強く相関した．例として，`No Finding` age では R=0.82，`No Finding` sex/race では R=0.81，`Cardiomegaly` age では R=0.81，`Effusion` race では R=0.71，`Pneumothorax` sex では R=0.59 だった．これは，demographic information を shortcut としてより強く encode する model ほど，FPR/FNR gap が大きくなりやすいことを示す．

## ID では shortcut mitigation が効く

ID setting では，ERM は大きい fairness gap を示す．たとえば `Cardiomegaly` prediction で age groups `80-100` と `18-40` の間に約20%の FNR gap があった．ReSample や GroupDRO のような group balancing / robustness method，DANN / CDANN のような adversarial method は，ID fairness gap を減らし，AUROC を大きく落とさない model を作れる．

著者らは，performance-fairness Pareto front 上にある model を locally optimal model と呼ぶ．ID では，いくつかの algorithm が high AUROC と low fairness gap を両立し，dermatology / ophthalmology でも同様の Pareto front が確認された．

## Locally optimal model の限界

ID で fairness と AUROC の Pareto front にある model は，他の clinically meaningful metrics で悪化することがある．`No Finding` では，fairness gap を下げると subgroup 間の Expected Calibration Error gap が悪化した．また，average precision や F1 score でも fairer model が悪くなる場合がある．

これは，fairness を単独で最適化すると，calibration や他の utility metric との trade-off が生じることを示す．特に Equalized Odds 系の criterion は group calibration と両立しないことが知られており，医療画像でも同様の問題が出る．

## ID fairness は OOD fairness に転移しない

OOD setting では，ID と OOD の overall AUROC は高く相関したが，ID fairness と OOD fairness の相関は一貫しなかった．`Effusion` / age では ID-OOD fairness correlation が強く正だったが，`Pneumothorax` / sex-race では R=-0.50 と負の相関だった．16 task-attribute combinations のうち，5設定で負の相関，3設定で弱い正の相関が観察された．

ID Pareto front 上の model も，OOD では Pareto optimality を維持しないことがある．`Cardiomegaly` / race の例では，ID で Pareto optimal な model が OOD Pareto front から外れた．この結果は，ID fairness を改善することが OOD fairness 改善を保証しないことを示す．

## OOD fairness gap の分解

著者らは，OOD fairness gap の変化を，ID fairness gap と subgroup ごとの performance change に分解する．例として，CheXpert で `No Finding` を学習し MIMIC-CXR に転移した ERM model は，ID では sex に関して FPR gap が -0.1% で有意ではなかったが，OOD では 3.2% の FPR gap を示し，female patients の underdiagnosis が高かった．

このとき OOD では female の FPR が 3.9% 増え，male の FPR は 0.8% 増えた．つまり，distribution shift は両群に悪影響を与えたが，female group により大きく影響したため fairness gap が生まれた．OOD fairness には，ID fairness の mitigation だけでなく，distribution shift が各 subgroup に与える disparate impact の mitigation が必要である．

## Globally optimal model selection

realistic deployment では，OOD samples を事前に観測できない．そこで著者らは，ID data だけから model を選ぶ8つの selection criteria を比較し，OOD fairness を oracle と比較した．oracle は OOD data を見て最も fair な model を選ぶ理想条件である．評価は外部 dataset，task，attribute の42 settings で行われる．

結果として，ID fairness gap を最小化する model selection は OOD fairness で最適ではなかった．ID embedding に含まれる demographic information を最小化する selection criteria，つまり minimum attribute prediction accuracy / AUROC を選ぶ方が，oracle に対する OOD fairness gap increase が小さかった．Minimum Attribute Prediction Accuracy は Minimum Fairness Gap より有意に良かった (P=9.60e-94)．

algorithm 別では，demographic encoding を embedding から除く DANN が OOD fairness で最も良く，ERM より有意に良かった (P=1.86e-117)．この結果は，globally optimal model には，ID fairness gap そのものより demographic encoding の少なさが重要になる可能性を示す．

## Caveats

著者らは，demographic feature をすべて shortcut として除くべきとは限らないと述べる．sex が breast cancer の causal factor であるように，demographic variables が疾患に直接または間接的に関係する場合がある．その場合は demographic reliance をゼロにするのではなく，true causal effect に見合う reliance に揃えるべきである．

また，fairness gap を小さくすることは必ずしも real-world health equity を保証しない．Equalized Odds は calibration by group と両立せず，leveling down を起こす可能性がある．著者らは，deployment scenario に合った fairness definition を選び，performance-equality trade-off を慎重に考えるべきだと述べる．

## Regulatory / monitoring implications

著者らは，FDA が clinical AI model の external validation を必須にしていない現状を踏まえ，distribution shift 下での model performance と fairness degradation を継続的に評価する必要があると主張する．single fair model がすべての setting で fair であるという前提は弱く，deployment 後も overall performance，per-group performance，clinical outcomes を monitor する必要がある．

## 関連概念

- [[Fairness_Under_Distribution_Shift]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Race_Recognition_In_Medical_Images]]
- [[Underdiagnosis_Bias]]
- [[Equalized_Odds]]
- [[Foundation_Model_Fairness]]
- [[Subgroup_Performance_Monitoring]]
