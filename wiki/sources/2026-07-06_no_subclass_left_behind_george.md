---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_no_subclass_left_behind_george.pdf"
---

# No Subclass Left Behind: Fine-Grained Robustness in Coarse-Grained Classification Problems

Nimit Sohoni，Jared A. Dunnmon，Geoffrey Angus，Albert Gu，Christopher Ré による NeurIPS 2020 論文．coarse-grained class labels の内部に unlabeled subclasses がある設定で，hidden stratification を測定し，worst-case subclass performance を改善する GEORGE を提案する．

GEORGE は，まず superclass task で ERM model を学習し，その feature space 内で各 superclass を clustering して proxy subclass labels を推定する．次に，その cluster assignments を group labels として group distributionally robust optimization（GDRO）を行う．subclass labels を使わずに，worst-case subclass accuracy を最大14 percentage points 改善したと報告する．

## 問題設定

real-world classification tasks では，1つの class が複数の semantically distinct subclasses を含むことが多い．subclass labels は利用できないことが多く，coarse-grained class labels だけで学習された model は subclass 間で大きく異なる performance を示す．この現象は hidden stratification と呼ばれ，医療のような safety-critical applications では重要である．

robust optimization techniques は group identities が既知なら poorly-performing groups の性能を改善できる．しかし実務では，subclasses が unlabeled で，そもそも unidentified であることが多い．GEORGE は，subclass labels がない状況で hidden stratification を測定し，worst-case subclass performance を改善することを目的とする．

## Robust accuracy

各 datapoint `x_i` には observed superclass label `y_i ∈ {1, ..., B}` と latent subclass label `z_i ∈ {1, ..., C}` があるとする．subclass label は superclass label を決定するが，学習時には `z_i` は観測されない．

通常の ERM は overall population accuracy を最大化する．一方，この論文の目的は，全 subclass の中で最悪の expected accuracy を最大化する robust accuracy である．

```text
argmax_f min_c E[(1(f(x) = y)) | z = c]
```

もし true subclass labels が分かっていれば，worst-case per-subclass training risk を最小化でき，これは group distributionally robust optimization（GDRO）で扱える．GEORGE は `z_i` がない状況でこれを近似する．

## Hidden stratification の原因

著者らは generative model を使い，hidden stratification の主因を2つに分ける．

1. inherent hardness: ある subclass が他 superclass に視覚的・特徴空間的に近く，どの model でも分類が難しい．
2. dataset imbalance: rare subclass が ERM の平均損失最小化で under-served になる．

inherent hardness による worst-case error はどの model でも下限になるが，dataset imbalance による robust performance gap は subclass labels が既知なら GDRO で改善できる．GEORGE は後者を，feature space clustering によって subclass labels を推定することで扱う．

## GEORGE の手順

GEORGE は2段階の手法である．

### Step 1: Approximate subclass labels の推定

superclass task で ERM model を学習する．この model は featurizer `f_θ` と logits layer `L` からなり，superclass labels を予測する．次に，各 superclass の data について，`f_θ` が出力する feature representations を clustering し，estimated subclass labels `z̃_i` を得る．

実装では clustering 前に UMAP dimensionality reduction を使う．また，高 loss differences を持つ subclasses はより分離されやすいという insight に基づき，activation vector のうち decision boundary に直交する loss component も alternative representation として使う．

standard k-means や Gaussian mixture model は small clusters を見逃しやすく，rare low-performing subclass が問題になるため，著者らは over-clustering を使う．ただし過度な over-clustering は spurious clusters を作り，robust performance の測定を pessimistic / unstable にするため，Silhouette（SIL）criterion に基づく自動 criterion で `k` を選び，spurious overclusters を filter する．

### Step 2: Estimated subclasses を使った GDRO

estimated subclass labels `z̃_i` を group labels として使い，新しい classifier を GDRO で学習する．GDRO は groups の中で最悪の empirical distribution に対する average loss を最小化する．true subclass labels を使えば true robust objective と一致するが，GEORGE では cluster assignments を proxy group labels として使う．

## 理論解析

論文は，feature space で各 subclass が異なる Gaussian として記述される mixture model を仮定し，GEORGE が true subclass labels を持つ GDRO と同じ asymptotic sample complexity rate で optimal robust risk に収束することを示す．

Theorem 1 は，loss と model が Lipschitz で，parameters が bounded，かつ `P(x | z = c)` が subclass ごとに unique Gaussian である場合，estimated robust risk の minimizer が true robust risk の minimizer に `Õ(1/√n)` で近づくことを述べる．著者らは，この結果は good feature space の回復が重要であり，model architecture の選択が subclass recovery に大きく影響することを示すと解釈する．

## Datasets

評価は4つの image classification tasks で行われる．

- Waterbirds: land-bird vs water-bird を分類する robustness benchmark．95% の land-birds / water-birds はそれぞれ land / water background にあり，background shortcut が起きる．
- U-MNIST: MNIST を “<5” vs “≥5” に分類する modified task．digits 0-9 が subclasses．`8` の 95% を削除し，rare subclass とする．
- CelebA: “blond” vs “not blond” を分類する face dataset．blond faces のうち male は6%だけであり，ERM は rare subclass である blond males に弱い．
- ISIC: skin lesions を malignant / benign に分類する real-world dataset．benign images の 48% は colored patch を含む．non-patch examples の 49% は histopathology（biopsy / pathologist referral）を必要とした．ISIC では AUROC を報告する．

## End-to-end results

robust performance と overall performance の主な結果は以下である．ISIC 以外は accuracy，ISIC は AUROC である．

| Method | Metric | Waterbirds | U-MNIST | ISIC Non-patch | ISIC Histopath. | CelebA |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ERM | Robust | 63.3 ± 1.6 | 93.9 ± 0.6 | .920 ± .007 | .872 ± .010 | 41.1 ± 2.3 |
| ERM | Overall | 97.2 ± 0.1 | 98.2 ± 0.1 | .956 ± .003 | .956 ± .003 | 95.7 ± 0.1 |
| GEORGE | Robust | 76.2 ± 2.0 | 95.7 ± 0.6 | .918 ± .009 | .881 ± .005 | 52.4 ± 1.3 |
| GEORGE | Overall | 95.5 ± 0.6 | 97.9 ± 0.2 | .935 ± .007 | .935 ± .007 | 94.8 ± 0.2 |
| Subclass-GDRO | Robust | 90.7 ± 0.4 | 96.8 ± 0.4 | .922 ± .007 | .876 ± .005 | 85.9 ± 2.5 |
| Subclass-GDRO | Overall | 92.0 ± 0.4 | 98.0 ± 0.3 | .934 ± .010 | .934 ± .010 | 93.6 ± 0.2 |

GEORGE は ERM と比べ，robust accuracy を最大14 points 改善し，ERM と subclass-GDRO の robust error gap の最大62%を埋めた．Waterbirds，U-MNIST，CelebA では worst-case subclass accuracy が有意に改善した．ISIC では clinically meaningful な histopathology subclass AUROC が ERM より改善し，non-patch subclass では各手法が同程度だった．overall performance は ERM が最も高い傾向だが，GEORGE による overall performance 低下は多くの場合5 points 未満で，robust performance の改善より小さい．

## Cluster recovery

GEORGE の Step 1 が poorly-performing subclasses に対応する cluster を見つけるかを，precision / recall で評価した．主な結果は以下である．

| Task | Subclass | Subclass Prevalence | Trials | Precision | Recall |
| --- | --- | ---: | ---: | ---: | ---: |
| U-MNIST | “8” digit | 0.012 | 100 | 0.81 | 0.80 |
| Waterbirds | Water-birds on land | 0.05 | 100 | 0.15 | 0.95 |
| Waterbirds | Land-birds on water | 0.05 | 100 | 0.30 | 0.93 |
| ISIC | No-patch | 0.48 | 100 | 0.99 | 0.60 |
| CelebA | blond males | 0.06 | 100 | 0.13 | 0.90 |

各 poorly-performing subclass について，GEORGE は high recall かつ random より良い precision の cluster を見つけた．ISIC で recall が低いのは no-patch subclass が2つの cluster に分割されるためであり，この2 cluster を合わせると no-patch examples の precision / recall は 0.99 以上になる．

## Unlabeled subclass discovery

GEORGE は human-provided schema にない semantically meaningful subclass も発見した．U-MNIST では 60% の trials で “7” subclass が stylistically different な2つの subclusters に分かれた．ISIC では 60% の trials で no-patch benign images が2つの distinct clusters に分かれ，一方の cluster では 77% が histopathology を必要とし，他方では 7% 未満だった．つまり，no-patch subclass が clinicians にとって難しい histopathology と non-histopathology clusters に分かれた．

## Cluster-robust performance

GEORGE が返す clusters 上の worst-case performance を cluster-robust performance と呼び，true robust performance と overall performance と比較した．多くの場合，cluster-robust performance は overall performance より true robust performance に近かった．ISIC では，cluster-robust performance は patch / no-patch subclass labels よりも histopathology subclass の robust performance をよく推定した．

| Method | Metric | Waterbirds | U-MNIST | ISIC Non-patch | ISIC Histopath. | CelebA |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ERM | Robust | 63.3 ± 1.6 | 93.9 ± 0.6 | .920 ± .007 | .872 ± .010 | 41.1 ± 2.3 |
| ERM | Cluster-Robust | 76.8 ± 1.6 | 92.3 ± 2.5 | .894 ± .031 | .894 ± .031 | 59.1 ± 1.1 |
| ERM | Overall | 97.3 ± 0.1 | 98.2 ± 0.1 | .956 ± .003 | .956 ± .003 | 95.7 ± 0.1 |
| GEORGE | Robust | 76.2 ± 2.0 | 95.7 ± 0.6 | .918 ± .009 | .881 ± .005 | 52.4 ± 1.3 |
| GEORGE | Cluster-Robust | 93.5 ± 0.5 | 93.5 ± 1.9 | .904 ± .020 | .904 ± .020 | 71.8 ± 0.2 |
| GEORGE | Overall | 95.5 ± 0.6 | 97.9 ± 0.2 | .935 ± .007 | .935 ± .007 | 94.8 ± 0.2 |

cluster-robust performance と overall performance を比較することで，subclass labels なしに hidden stratification を検出し，その magnitude を推定できると述べる．

## Pretrained embeddings

ERM features の代わりに pretrained BiT embeddings を clustering に使う拡張も評価した．CelebA では robust accuracy が 86.0% に改善し，subclass-GDRO と一致した．blond male subclass の precision は 0.15，recall は 0.98 に改善した．ただし，Waterbirds では BiT clustering は default GEORGE より悪く，trained ERM model の task-specific information が meaningful clusters の識別に重要な場合がある．

## 結論

GEORGE は，subclass labels にアクセスせずに hidden stratification を測定・緩和する2段階手法である．ERM model の features を clustering することで worst-case subclass performance の有用な近似を作り，その cluster assignments を GDRO の group として使うことで worst-case subclass performance を改善する．著者らは，GEORGE は subclass labels がなくても hidden stratification を減らせる evidence を示したと結論づける．

## 関連概念

- [[Worst_Group_Performance]]
- [[Hidden_Stratification]]
- [[Subgroup_Performance_Monitoring]]
- [[Group_DRO]]
- [[Algorithmic_Subgroup_Discovery]]
- [[Medical_Image_Fairness_Audit_Loop]]
