---
created: 2026-07-21
updated: 2026-07-21
raw: "raw/papers/2307.02791v1.pdf"
---

# The Role of Subgroup Separability in Group-Fair Medical Image Classification

Jones, Roschewitz, Glocker（Imperial College London）による論文（arXiv:2307.02791）．深層分類器の性能格差を，**subgroup separability**（モデルが個人を protected subgroup へ分離できる度合い）という観点から分析する．subgroup separability は医療画像 modality と protected attribute の組み合わせによって大きく異なり，この性質が algorithmic bias を予測することを理論的・実証的に示す．コードは https://github.com/biomedia-mira/subgroup-separability で公開されている．

## 問題設定

医療画像分類モデルは，sensitive information に依存して予測することがあり，protected subgroup 間で性能格差を示すことが知られている．多くの bias mitigation 手法が存在するが，MEDFAIR のベンチマークでは empirical risk minimisation (ERM) を一貫して上回る手法はなく，実運用に適した手法はまだない．公平なシステムを設計するには，まず ERM モデルがどのように bias を獲得するかの underlying mechanism を理解する必要がある，というのが本論文の立場である．

Subgroup separability とは，医療画像から個人が subgroup member であると識別されやすさを指す．たとえば生物学的性別は胸部 X 線から高精度（AUC > 0.98）で予測できるなど，intrinsic physiological difference を持つ group は separability が高くなりやすい一方，「social construct」に基づくような subtle な差異を持つ group は separability が低くなりやすい，という premise を著者らは立てる．

本論文の contribution は3つ．

1. subgroup separability が実世界の modality と protected attribute の組み合わせで大きく異なることを実証する．
2. separability の違いが学習済み分類器の model bias に影響し，subgroup separability が低い dataset では group fairness metric が不適切になりうることを理論的に示す．
3. 実世界の医療データセットでの実験により，データにバイアスがある場合，性能劣化と subgroup disparity が subgroup separability の関数であることを示す．

## 理論的枠組み

二値疾患分類問題を考える．画像 `x ∈ X` から label `y ∈ Y = {y+, y-}` への真のマッピングを `P: [Y|X] → [0,1]` とする．学習データセットの分布 `P_tr` が真の分布 `P` と異なるとき，そのデータセットは biased であるという．本論文が扱う bias は **underdiagnosis**（label noise の一種）で，真に陽性の個体 `x+` が誤って陰性ラベルを付けられる現象である．

group `A = a*` が underdiagnosed であるとは，次を満たすことをいう．

```text
P_tr(y|x+, a*) ≤ P(y|x+, a*)  かつ
∀a ≠ a*, P_tr(y|x+, a) = P(y|x+, a)
```

全体のマッピングは全確率の法則により subgroup-wise mapping の線形結合で書ける: `P_tr(y|x) = Σ_a P_tr(y|x,a) P_tr(a|x)`．この式から，個人に対する予測は，その個人が各 subgroup に属する確率で重み付けされた subgroup ごとのマッピングの線形結合であることが分かる．

**subgroup separability が高い場合**（sensitive information が容易に利用できる場合），モデルは各 subgroup ごとに異なるマッピングを学習できる．このとき，underdiagnosed group `a*` は underdiagnosis を再現する一方，他の group は unbiased mapping を回復する．結果として，underdiagnosed group の test-time TPR は他の group より明確に低くなり，group fairness metric がこの bias を検出できる．

**subgroup separability が低い場合**（`P(a|x) ≈ 1/|A|` で non-separable な場合），モデルは subgroup 別のマッピングを学習できず，`p̂(y|x+, a) ≈ P_tr(y|x+), ∀a ∈ A` となる．この場合，性能劣化は全 group に一様に生じ，group fairness metric（group 間の差）ではこの劣化を検出できない．劣化の深刻さは，underdiagnosed subgroup におけるラベル破損の割合と，dataset 内での underdiagnosed subgroup のサイズに依存する．

## 実験設定

MEDFAIR ベンチマークのサブセットから5つのデータセットを採用し，各データセットを binary subgroup label 付きの二値分類タスク（no-disease vs disease）として扱う．複数の sensitive attribute を持つデータセットは属性ごとに個別に扱い，合計11の dataset-attribute の組み合わせで実験する．modality は皮膚科（dermatology），眼底画像（fundus image），胸部 X 線（chest X-ray）の3種．

### Subgroup separability の実測（Table 1）

各 dataset-attribute の組み合わせについて，subgroup を予測する binary classifier を学習し，test-set AUC を separability の proxy として10 random seeds で測定した．

| Dataset-Attribute | Modality | Group 0 | Group 1 | AUC (μ) | AUC (σ) |
| --- | --- | --- | --- | ---: | ---: |
| PAPILA-Sex | Fundus Image | Male | Female | 0.642 | 0.057 |
| HAM10000-Sex | Skin Dermatology | Male | Female | 0.723 | 0.015 |
| HAM10000-Age | Skin Dermatology | <60 | ≥60 | 0.803 | 0.020 |
| PAPILA-Age | Fundus Image | <60 | ≥60 | 0.812 | 0.046 |
| Fitzpatrick17k-Skin | Skin Dermatology | I-III | IV-VI | 0.891 | 0.010 |
| CheXpert-Age | Chest X-ray | <60 | ≥60 | 0.920 | 0.003 |
| MIMIC-Age | Chest X-ray | <60 | ≥60 | 0.930 | 0.002 |
| CheXpert-Race | Chest X-ray | White | Non-White | 0.936 | 0.005 |
| MIMIC-Race | Chest X-ray | White | Non-White | 0.951 | 0.004 |
| CheXpert-Sex | Chest X-ray | Male | Female | 0.980 | 0.020 |
| MIMIC-Sex | Chest X-ray | Male | Female | 0.986 | 0.008 |

AUC の範囲は 0.642〜0.986 と非常に広く，subgroup separability が medical imaging application 間で大きく異なるという premise を裏付けている．全ての attribute が chest X-ray からは AUC > 0.9 で予測でき，X-ray という modality が患者の identity に関する情報を大きく含むことを示唆する．age はどの modality でも一貫して予測しやすい一方，biological sex の separability は modality によって大きく変動し，fundus image からの sex 予測は特に弱かった．

### Label bias 下での性能劣化（Fig. 1）

各 dataset で，Group 1（Table 1 参照）の陽性個体の25%をランダムに陰性へ誤ラベル付けし，underdiagnosis bias を人為的に注入した．biased data で学習した10モデルと，元の clean label で学習した10モデルを，共通の clean test data で評価し，biased model の性能劣化を測定した．統計的有意性は Mann-Whitney U test（Holm-Bonferroni 補正，p_critical = 0.05）で判定した．

結果は理論的分析と整合していた．subgroup separability が低い（<0.9 AUC）組み合わせでは統計的に有意な性能劣化は見られなかった．これらの実験ではラベル破損の割合が全体集団に対して小さく，underdiagnosed subgroup は uncorrupted group とマッピングを共有することで概ね回復した．PAPILA では性能が改善する意外な結果も見られたが，最小のデータセットであり，有意ではなかった．subgroup separability が上がるにつれ，underdiagnosed group（Group 1）の性能劣化が大きくなる一方，uncorrupted group（Group 0）はほぼ無傷だった．MIMIC-Sex 実験では Group 0 でも統計的に有意な劣化が見られ，著者らはモデルが group ごとに別々のマッピングを学習することで，Group 0 の実効的なデータセットサイズが縮小したためと考察している．

### Sensitive information の representation encoding（Fig. 2）

biased data で学習した全モデルに対し，post hoc の Supervised Prediction Layer Information Test (SPLIT) を適用した．trained backbone を freeze し，最終層のみを sensitive attribute 予測用に再学習する手法である．SPLIT AUC を Table 1 の subgroup separability AUC に対してプロットし，Kendall's τ で単調な関連を検定した（p_critical = 0.05）．

biased data で学習したモデルでは，利用可能な sensitive information の量と representation に符号化される量との間に統計的に有意な関連が見られた（τ = 0.673, p = 0.003）．一方，unbiased data で学習したモデルでは有意な関連は見られず（τ = 0.164, p = 0.542），sensitive information を exploit していないことを示唆する．

## Discussion（4つの takeaway）

1. **Subgroup separability は医療画像で大きく異なる**．fairness 文献では，データが subgroup member を識別するのに十分な情報を含むと暗に仮定されることが多いが，本研究の11 dataset-attribute × 3 modality の実験は，分類器が sensitive attribute を予測する能力が大きく異なることを示した．
2. **性能劣化は subgroup separability の関数である**．separability が高いとき，モデルは sensitive information を exploit し，bias は subgroup 間の明確な性能差として現れる．separability が低いとき，モデルは sensitive information を exploit できず，全 group で同様に性能が低下する．これは，separability が低い場面では group fairness metric が bias 検出に不十分である可能性を示す．
3. **bias の source が重要**．本研究では underdiagnosis bias を人為的に注入し，元の clean label を unbiased ground truth として扱ったが，実際にはこれらのデータセット自体が既に一定の underdiagnosis bias を含んでいる可能性がある．ただし，既存の pre-existing bias は人為的に注入した bias より効果が小さいと予想され，結果への影響は限定的と考えられる．
4. **Reproducibility**．データセットはすべて公開されており，前処理・実験・分析の完全な実装が GitHub で公開されている．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| subgroup separability | モデルが個人を protected subgroup へ分離・識別できる度合い．binary subgroup classifier の AUC で近似測定する |
| underdiagnosis | 真に陽性の個体が誤って陰性ラベルを付けられる label noise の一種 |
| SPLIT | Supervised Prediction Layer Information Test．trained backbone を freeze し最終層のみ sensitive attribute 予測用に再学習し，representation に符号化された sensitive information 量を測る post hoc test |
| ERM | Empirical Risk Minimisation．標準的な教師あり学習の目的関数 |
| leveling down | bias mitigation 手法が全 group の性能を悪化させることで見かけ上の group 間差を縮める効果 |

## 関連概念

- [[Underdiagnosis_Bias]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Race_Recognition_In_Medical_Images]]
- [[Equalized_Odds]]
- [[Worst_Group_Performance]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
