---
created: 2026-07-21
updated: 2026-07-21
raw: "raw/papers/2305.01397v3.pdf"
---

# Are Demographically Invariant Models and Representations in Medical Imaging Fair?

Petersen, Ferrante, Ganz, Feragen（DTU / Pioneer Centre for AI / CONICET / University of Copenhagen / Rigshospitalet）による論文（arXiv:2305.01397v3）．医療画像モデルが患者の人口統計学的属性（age，race，sex）を latent representation に符号化することが知られている中，「モデルが demographic group membership を符号化**しない**ことを要求するのは望ましいか」を問う．marginal representation invariance，class-conditional representation invariance，counterfactual model invariance の3種類の invariance を順に検討し，それぞれの fairness notion との対応関係と限界を理論的に整理する．

## 背景・問題設定

Gichoya et al. や Glocker et al. などの先行研究は，胸部 X 線などの医療画像から neural network が患者の race を高精度に推定できること，disease classification 用に訓練したモデルでも demographic group ごとに異なる latent encoding を学習する傾向があることを示してきた．これらの研究は，latent representation が group membership を符号化するなら，モデルが（意図的・非意図的に）demographic group に対して discrimination しうると警告する．この懸念は「demographic group membership を latent space に符号化しないモデルを開発すべきか」という問いにつながる．

問題設定は次の通り．患者は複数の（overlap しうる）demographic group `A`（例: young，female，young female）に属する．入力 `X`（医療画像，血液マーカー，その他の生理学的計測）から label `Y`（疾患カテゴリ，連続的な重症度スコア，segmentation mask 等）を予測する．deterministic な feature extractor `g: x → z` によって latent representation `Z` を得て，deterministic な `h: z → r` によって prediction `r ∈ R^dim(Y)` を得る．必要であれば `r` を threshold `τ` で discretize して `ŷ` を得る．`g` と `h` はいずれも group membership を明示的な入力として受け取らず，`τ` は group に依存しないと仮定する．モデルが `Z` から group membership `A` を chance 以上の精度で推定できるとき，モデルは `A` を「符号化する（encode）」という．

## Section 2 — Marginal representation invariance

モデルが group membership を符号化しないことを求めるのは，latent representation `z` が group `a` 間で invariant であることと等価である．

```text
p(z) = p(z | a)  ∀a   ⇔   Z ⊥ A     (式1)
```

しかし `p(z | a)` が group 間で同一であれば，prediction の分布 `p(r | a)` と `p(ŷ | a)` も group 間で同一になり，`R, Ŷ ⊥ A` が成り立つ．これは algorithmic fairness の **statistical parity（demographic parity, independence）** に対応する．

疾患 prevalence が group 間で異なる場合，式1を満たすことは予測精度の損失なしには不可能である．なぜなら，`p(ŷ | a) ≠ p(y | a)` が必然的に生じるからである．医療画像応用で `p(y | a)` が group 間で異なる理由の例:

- prevalence の違い: 乳がんの男女間 prevalence 差．prevalence が異なる group に対して同一の positive/negative prediction 分布を返す classifier は望ましくない．
- segmentation における organ shape/size の age・sex 依存差．

`p(y | a)` の group 間差は `Y` が高次元になるほど（例: multi-class，segmentation）識別しやすくなる．Figure 2 は，異なる prevalence を持つ binary disease label の数（次元）を増やすと，画像 `X` を一切使わずラベル `Y` だけから group membership `A` を予測する accuracy が急速に1に近づくことを示す（1000回の repetition，各疾患の incidence を [0.1, 0.9] からランダムに抽出）．これは，モデルが正確であるほど（`Ŷ` が `Y` を反映するほど）`A` の non-identifiability が事実上困難になることを示す．

domain adaptation 理論では，式1に対応する性質は **marginal alignment** と呼ばれ，これを満たす latent representation はしばしば単に "domain-invariant" と呼ばれる．`p(y | a)` の group 間の等しさは，予測性能最適な（marginally）invariant representation が存在するための必要条件であることが知られている．statistical parity は prevalence 差がある場合に大きな予測性能の損失を招くことが知られており，二値分類・二群設定では，statistical parity を強制すると両群の error rate の合計が prevalence 差で下から抑えられることが示されている（Zhao and Gordon）．

論文はここで **モデル**（`ŷ` が `A` の値に関わらず同一であるべき）と **表現**（`Z, Ŷ ⊥ A`，`Y` と `A` が相関していても成立するよう要求）の違いを区別する．demographically invariant representation を要求することは，`Y` が `A` と相関する場合，モデルの feature extraction（encoding）段階で **actively confounding**（意図的に交絡させる）ことを強制し，unequal treatment と不必要な誤分類を招く．

低次元ラベル（疾患ラベルなど）の場合，label shift（prevalence 差はその一例）に対処する一つの戦略は，training set を group 間で `p(y | a)` が等しくなるよう artificially balance することである．

## Section 3 — Class-conditional representation invariance

`p(y | a)` が domain 間で異なる状況は **label shift** と呼ばれる．一部の提案手法は，marginal distribution `p(z)` の代わりに **class-conditional distribution** `p(z | y)` を group 間でマッチさせようとする．

```text
p(z | y) = p(z | y, a)  ∀a, y   ⇔   Z ⊥ A | Y     (式2)
```

式2は `p(r | y, a)` と `p(ŷ | y, a)` の等価性を含意し，したがって `R, Ŷ ⊥ A | Y` を含意する．これは algorithmic fairness の **separation** 基準に対応し，その帰結として **equalized error rates** が成り立つ．class-conditional invariance は marginal invariance を含意しない（式2を満たすモデルが group membership を latent space に符号化しうる）．

class-conditional representation invariance が医療画像モデルにとって望ましい性質かは，group membership が符号化されるという懸念を措いても疑わしい．risk score `R` は，病的な場合を除き，separation と group-wise calibration の両方を同時に満たすことはできないことが知られている．また，separation の倫理的意義は不明瞭であるとも論じられている．separation を **risk score レベル**（`R ⊥ A | Y`）で要求することと，**classification レベル**（`Ŷ ⊥ A | Y`，equal error rates を含意）で要求することは異なり，後者は望ましい目標でありうる．ただし，equal error rate は class-conditionally invariant な risk distribution という過度に制約的な要求なしでも達成可能である．

## Section 4 — General drawbacks of representation invariance

representation invariance の共通の欠点は，group 間の **within-class distribution** の違いを無視することである．単一の class label が，疾患の異なる subtype や現れ方など，根本的に異なる複数の状況を包含することがあり，これは **hidden stratification** と呼ばれる．group（domain）間でラベルの現れ方（manifestation）の分布が異なる状況は **manifestation shift** とも呼ばれる．

Figure 3 はこれを図示する．病気の重症度（severity）の分布が group `a1`，`a2` の罹患患者間で異なる場合（左パネル），class-conditional representation invariance を強制すると，group によって異なる severity を持つ患者を同一の latent representation にマッピングすることを要求する（中央パネル）．これは同じ患者に同一の risk prediction を割り当てることにもつながる．

within-class variation の一種として，**task difficulty** が group 間で異なる問題がある．生理学的・技術的理由（例: 撮影を confound する組織量の違い）により，あるgroupではpredictionが他groupより難しいことがある．この場合，望ましいモデルは，より強く confound された group のメンバーに対しては（同じ疾患インスタンスであっても）より確信度の低い予測を返すべきであり，representation invariance はこのような本質的な group 間差を均一化することを要求してしまう．これは representation invariance が "fair treatment" を保証しないばかりか，**disparate treatment を要求しうる**ことを示す一例でもある．

representation invariance が意味のある fairness 保証を提供するかについて: marginal invariance は statistical parity を含意する（資源配分や患者優先順位付けの場面では望ましいこともあるが，一般的な予測設定では望ましくないことが多い）．Glocker et al. は，representation が group membership を "符号化する" ことは，モデルが意思決定にその情報を "使用する" ことを含意しないとも指摘する．class-conditional invariance は equalized error rate を含意し，これは leveling down 現象に苦しむことが知られているものの，予測場面では望ましい目標でありうる．しかし，equalized error rate は class-conditionally invariant な risk distribution を要求しなくても達成可能であり，class-conditional representation invariance の要求は group-wise calibration との非両立という欠点を伴う，過度に制約的な要求と見なせる．

さらに，representation invariance の fairness 保証は，評価に用いる **特定のデータセットに依存する**という根本的な限界がある．representation invariance は，特定のデータセットに適用された **モデル** の性質であり，同じモデルが別のデータセット（label shift，covariate shift，intra-class variation shift を含む）でも invariant representation を生成する保証はない．training/evaluation データセットが（一般的なベストプラクティス通り）注意深くキュレーションされ，実世界の観測データと大きく異なりうる場合，これは特に懸念される．この限界は representation invariance approach だけでなく，他のすべての統計的 group fairness criteria にも当てはまる．

## Section 5 — Model invariance（counterfactual invariance）

representation matching approach の欠点に対処するため，domain adaptation 文献では object matching，relaxed distribution matching，support alignment，hypothesis invariance など様々な代替手法が提案されているが，医療画像領域での説得力ある成功例はまだない．

representation invariance ではなく **model invariance**（nuisance variable `A` に関して invariant なモデル・機構自体）を学習しようという domain generalization コミュニティの方向転換が近年見られる．代表的なアプローチは **counterfactual invariance** の概念に基づく: `A` を変化させても "他の全てを固定した (keeping everything else fixed)" 場合にモデル予測が変化しないことを求める．`A` が sensitive attribute のとき，これは **counterfactual fairness**（individual fairness の一種，group fairness ではない）に対応する．counterfactual invariance が理論的に成り立つなら，データ分布が変化してもその invariance は保たれるはずである（回転・並進などの形式的に定義された代数演算に対する invariance ではこの理論的保証が得られているが，医療画像における demographic group に関する invariance の場合はより複雑で，形式的に定義することが難しい）．

Figure 4 は，"Birth Sex" が医療画像記録 `x` に因果的に影響しうる経路を示す簡易的な causal diagram（Birth Sex → Gender，Birth Sex/Gender → Anatomy & Physiology / Lifestyle Factors，これらが Disease と `x` に影響）である．これらの経路のどれに対して（counterfactually）invariant であるべきかは自明ではない．

**すべての経路**に対する invariance は，異なる生物学的（出生時の）性別の画像表現の（疾患条件付き）分布を完全に均一化することに相当する．胸部 X 線の文脈では，これは女性の胴体形状，組織分布，臓器サイズ，疾患の現れ方を男性群で観察される分布に適合させるように調整することを意味する．Veitch et al. はこのような counterfactual invariance approach が `R, Ŷ ⊥ A | Y`（すなわち separation）を含意することを見出しており，これは class-conditional representation invariance と同じ欠点を伴う（Nilforoshan et al. も同様の知見）．Puli et al. も類似の等価性を導いている．また，このような invariance を強制することは，BMI のような biological sex の単なる correlate がモデル予測に影響することも許可しなくなる．

**一部の経路のみ**に対する invariance（**path-specific counterfactual fairness**）も理論上は可能だが，医療画像解析への実装例は著者らの知る限り存在しない．これは causal diagram（Figure 4 のような）中の異なる causal relationship を経験的データから同定することの複雑さに起因すると考えられる．そのようなアプローチは通常，causal graph 中の全変数の観測を要求するが，医療では通常入手できない．counterfactual invariance approach の核心は，考慮すべき counterfactual の正確な定義にある: "何を固定し，何を調整すべきか"．これは "biological sex counterfactual"，"ethnicity counterfactual"，"age counterfactual" を生成する際に何が普遍的に成り立つべきか，どの group `a` の特性が本質的（peculiar）でモデルが invariant であるべきか，どれが単なる correlate として予測に影響してよいかという，social construct（demographic group）の文脈で非自明な問いを提起する．社会構築的な demographic group に関するこれらの問いの妥当性は，counterfactual model invariance approach の妥当性を完全に左右する．さらに，いかなる causal な fairness の考え方も unobserved confounding に対して脆弱である．

## Section 6 — Discussion & Conclusion

出発点は，複数の研究グループによる，deep learning モデルが患者の demographic feature を latent space に符号化する傾向があるという観察であった．これらの観察に促され，本論文はまず，モデルが demographic group membership を（latent representation から chance 以上の精度で推定できないという意味で）符号化**しない**ことを訓練するのが feasible かつ desirable かを問うた．

- **Marginal representation invariance**（=この要求と等価）は statistical parity を含意し，well-known な leveling-down 効果を超えて，モデル性能を著しく損なう場合がある．
- **Class-conditional invariance**（marginal invariance に近い代替案）は，label shift（group 間の `p(y|a)` の違い）下での深刻な性能劣化という marginal invariance の問題の1つを緩和する．しかし class-conditional invariance は algorithmic fairness の **separation** criterion（risk score レベル）を含意し，これは group-wise calibration との非両立などの理由から望ましくない可能性がある．error rate equality を直接強制することはこれらの欠点を伴わない．
- representation invariance のアプローチはいずれも，疾患 subtype や現れ方の違いなど group 間の **intra-class variation** の違いを無視するという欠点を共有する．また "fair treatment" を保証せず，むしろ disparate treatment を要求しうる（そのような disparate treatment は単にモデルの feature extraction 段階に移動するだけである）．
- 最後に，代替案として **counterfactually invariant なモデル** を検討したが，医療画像領域における demographic attribute に関する意味のある counterfactual の理論的定義と実務的推論は深刻な課題を伴い，しばしば representation invariance approach と同じ欠点（Nilforoshan et al. も参照）を引き起こす．

group membership を符号化することが有益になりうるか，という問いについて: モデルが（representation invariance を達成するために，あるいは推論時に group 別 calibration や thresholding を行うために）明示的な group membership 情報に依存する場合，そのモデルは，physiological な差異というより主に **sociocultural construct**（race，gender など）に基づいて人間を分類することに伴う周知の問題を引き継ぐ．代替として，予測タスクに関連する age，ethnicity，biological sex の側面だけを抽出する **implicit representation** を学習したモデルを考えることができる．このようなモデルは，粗い human-defined category ではなく，これらの属性の **continuous representation** を学習できる可能性があり，non-binary や mixed-race patient のような伝統的カテゴリの狭間にある患者群への，より頑健な一般化を可能にしうる（ただしこれは理想化されたビューであり，実践でモデルがそのような minimal かつ optimal な representation を実際に学習するかは重要な未解決の問いである）．Glocker et al. は，疾患予測のみで訓練された（demographic group prediction では訓練されていない）モデルが，demographic group prediction のために明示的に訓練されたモデルの representation より，demographic property に対する予測力が大幅に低い representation を学習する例を示しており，この可能性を示唆する証拠となっている．

representation invariance approach の主な応用領域は **unsupervised domain adaptation**（新しい domain でラベル `y` が利用できない設定）であり，この設定では invariant representation learning は有益になりうる．これは，本論文が扱う「全ての demographic group からラベルが利用可能」な設定とは異なる．また，本論文の議論は主に **strict invariance** の enforcement を対象としており，実務上多くの invariant representation learning approach は，domain や demographic group に対して不必要に強く予測的な representation の学習を防ぐために **正則化** を用いることが多い．こうした手法は，strict invariance enforcement の負の効果を最小化するようチューニングされていれば有益でありうる．同様に，fair pruning や fair early exiting のような，より制約の緩い mitigation 手法によっても類似の利益が得られる可能性がある．ただし，こうした手法を用いても，latent representation はある程度 demographic group membership を符号化し続ける．

総合すると，本論文の分析は，現時点で，類似の生理学的特徴を持ちながら異なる demographic feature を持つ個人に対する同様の扱いを保証する straightforward な方法は存在しないことを示唆する．異なる demographic invariance の notion を強制することは，group 間でモデル性能の異なる側面を害する可能性が高い一方，equal treatment に関して意味のある保証を一切提供しない．したがって，モデルが group membership を符号化するという単なる事実は，fairness violation とは見なせないと論文は主張する．group encoding は，人間が定義した patient category に内在するバイアスをモデルが継承することを防ぐ場合には，有益とすらみなせることもある．本分析は，包括的な subgroup 分析による fairness assessment の必要性にさらなる緊急性を与える．モデル性能改善には，balanced empirical risk minimization，targeted data collection，label bias の調査などが，現時点で最も有望な実務的手段として挙げられる．demographic shortcut learning を防ぐことが目的であれば，demographic invariance の代わりに，shortcut testing のような手法が使用されうる．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| marginal representation invariance | `Z ⊥ A`．latent representation が group membership の marginal distribution に依存しないこと．statistical parity を含意する |
| class-conditional representation invariance | `Z ⊥ A \| Y`．label 条件付きで latent representation が group 間で一致すること．separation（equalized error rates）を含意する |
| statistical parity（demographic parity, independence） | `R, Ŷ ⊥ A`．予測分布が group 間で等しいこと |
| separation | `R, Ŷ ⊥ A \| Y`．label 条件付きで予測分布が group 間で等しいこと |
| label shift | `p(y \| a)` が domain（group）間で異なる状況．prevalence 差はその一例 |
| manifestation shift | 疾患の現れ方（label の manifestation）の分布が domain・group 間で異なる状況 |
| hidden stratification | 粗い class label の内部に，臨床的・視覚的に異なる subclass が隠れている状態 |
| counterfactual invariance | `A` を変化させても "他を全て固定" した場合にモデル予測が変化しないこと |
| counterfactual fairness | counterfactual invariance のうち `A` が sensitive attribute である個体レベルの fairness notion |
| path-specific counterfactual fairness | causal diagram 上の一部の経路のみに対する counterfactual invariance |
| leveling down | fairness 強制により高性能な group の性能を下げることで見かけ上の group 間差を縮める現象 |
| encode（group membership を符号化する） | representation `Z` から group membership `A` が chance 以上の精度で推定できること |

## 関連概念

- [[Equalized_Odds]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Race_Recognition_In_Medical_Images]]
- [[Hidden_Stratification]]
- [[Subgroup_Separability]]
- [[Underdiagnosis_Bias]]
