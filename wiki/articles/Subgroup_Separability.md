---
created: 2026-07-21
updated: 2026-07-21
sources:
  - "[[sources/2026-07-21_subgroup_separability_group_fair_medical_image_classification]]"
  - "[[sources/2026-07-21_demographically_invariant_models_representations_medical_imaging_fair]]"
---

# Subgroup Separability

同じ underdiagnosis bias を training data に混入させても，あるデータセットでは group fairness metric がはっきり bias を検出し，別のデータセットでは検出できずに全 group が一様に性能劣化する．この違いはどこから来るのか．Subgroup separability は，モデルが画像から個人を protected subgroup（性別，年齢，人種など）へ分離・識別できる度合いを指す概念であり，この違いを説明する．

この概念が重要なのは，fairness 文献がしばしば「データは subgroup member を識別するのに十分な情報を含む」と暗黙に仮定しているためである．しかし実際には，intrinsic physiological difference を持つ group（例: 胸部 X 線からの生物学的性別）は separability が高く，subtle な差異しか持たない group（例: fundus image からの性別）は separability が低い．この差が，同じ bias injection でも観測される fairness の現れ方を大きく変える．

## 何を測る概念か

Subgroup separability は，binary subgroup classifier（画像 `x` から subgroup label `a` を予測するモデル）の test-set AUC で近似測定する．AUC が高いほど，モデルが画像だけから個人の subgroup member 資格を高精度に判別できることを意味する．

```text
画像 x
  -> subgroup classifier
  -> a の予測（Group 0 or Group 1）
  -> AUC が高い = separability が高い = disease classifier も a を利用しやすい
```

Jones et al. は，皮膚科・眼底画像・胸部 X 線の3 modality，11の dataset-attribute の組み合わせで separability を実測し，AUC 0.642（PAPILA-Sex，fundus image）から AUC 0.986（MIMIC-Sex，chest X-ray）まで広く分布することを示した．age はどの modality でも一貫して高い separability を示す一方，sex の separability は modality によって大きく変動した．

| Separability | 例 | 意味 |
| --- | --- | --- |
| 高い（AUC ≳ 0.9） | chest X-ray からの sex，race，age | モデルが個人を subgroup ごとに区別しやすい |
| 中間 | skin dermatology の age，Fitzpatrick skin type | modality・attribute によって差が出る |
| 低い（AUC ≲ 0.8） | fundus image からの sex | subtle な差異しか画像に現れず区別しにくい |

## Separability が bias の現れ方を変える

二値疾患分類で，学習データに特定 subgroup `a*` の underdiagnosis bias（真に陽性の個体が陰性ラベルにされる label noise）が含まれるとする．このとき，全体の予測マッピングは全確率の法則により subgroup-wise mapping の線形結合として表せる: `P(y|x) = Σ_a P(y|x,a) P(a|x)`．

**separability が高い場合**，モデルは `P(a|x)` を高精度に推定できるため，subgroup ごとに異なるマッピングを学習できる．結果として underdiagnosed group `a*` だけが bias を再現し，他の group は unbiased mapping を回復する．この非対称性を group fairness metric（TPR gap など）が検出できる．

**separability が低い場合**（`P(a|x) ≈ 1/|A|` に近い），モデルは subgroup 別のマッピングを学習できず，`p̂(y|x, a) ≈ P_tr(y|x), ∀a` となる．bias は全 group に一様に波及し，group 間の差としては現れない．severity はラベル破損の割合と underdiagnosed subgroup のサイズに依存する．

```text
separability 高い:
  underdiagnosed group だけ TPR が下がる
  -> group fairness metric が検出できる

separability 低い:
  全 group の TPR が一様に下がる
  -> group fairness metric では検出できない（性能自体は劣化している）
```

Jones et al. は実験でこれを裏付けた．低 separability（<0.9 AUC）の組み合わせでは，25% のラベル破損を注入しても統計的に有意な性能劣化は検出されなかった．separability が上がるにつれ，underdiagnosed group の劣化が大きくなり，uncorrupted group はほぼ無傷のまま残った．

## Group fairness metric が沈黙するケース

この理論の実務上の含意は，**group fairness metric（AUC gap，TPR gap など）が「差がない」と報告しても，それはモデルが公平であることを意味しない**という点である．separability が低い状況では，bias があっても全 group が一様に悪化するため，group 間の差としては現れない．これは [[Medical_Image_Fairness_Evaluation]] における worst-case AUC や absolute performance の監視の重要性を補強する．group 間の差だけでなく，clean baseline に対する絶対的な性能低下も見る必要がある．

| 評価が見落とすもの | 理由 |
| --- | --- |
| separability が低い dataset での uniform degradation | group 間の差として現れないため，group fairness metric では検出できない |
| bias の有無そのもの | 差がないことは「bias がない」ではなく「separability が低い」ことを意味しうる |

## Sensitive information の representation encoding

Separability は，モデルが sensitive information を internal representation に符号化するかどうかとも結びつく．Jones et al. は post hoc の SPLIT（Supervised Prediction Layer Information Test，trained backbone を freeze し最終層のみ sensitive attribute 予測用に再学習する手法）を適用し，biased data で学習したモデルでは，利用可能な sensitive information の量（separability）と representation に符号化される量との間に統計的に有意な単調関連（Kendall's τ = 0.673, p = 0.003）を確認した．一方，unbiased data で学習したモデルではこの関連は見られなかった（τ = 0.164, p = 0.542）．

これは，モデルが sensitive information を「使う」かどうかは，データが biased かどうかと，そのデータで sensitive attribute がどれだけ separable かの両方に依存することを示す．この関係は [[Race_Recognition_In_Medical_Images]] が示す「pixel data に protected attribute information が residual に残る」という現象と接続する．separability が高い modality（chest X-ray）ほど，bias があるときに representation が sensitive information を強く符号化しやすい．

この視点は [[Demographic_Representation_Invariance]] とも補完関係にある．representation invariance の議論は「group membership を符号化しないよう representation を強制すると，どの fairness criterion が得られ，何を失うか」を扱う規範的な枠組みであるのに対し，subgroup separability は「bias があるデータで学習した ERM モデルは，そもそもどの程度 group membership を符号化しうるか」を記述的に測る．separability が低ければ，class-conditional representation invariance のような制約を明示的に課さなくても，モデルは事実上 group を区別できず，逆に separability が高い状況でこそ representation invariance の代償（statistical parity や separation の強制）が問題になりやすい．

## 設計思想（なぜこの視点が必要か）

MEDFAIR などのベンチマークでは，bias mitigation 手法がERMを一貫して上回らないという結果が報告されている．Jones et al. は，これを「手法が悪い」という話ではなく，**bias がどのように classifier に現れるかの underlying mechanism を理解しないまま手法を評価している**ことが一因ではないかと位置づける．Subgroup separability は，この mechanism の中心的な変数として，同じ bias mitigation 手法でも dataset-attribute の組み合わせによって効果が変わりうることを説明する枠組みを与える．

また，本研究は underdiagnosis bias を人為的に注入する設定を取っており，これは実データの bias 量を過小評価も過大評価もしうる．既存データセットが既に含む pre-existing bias は，人為的注入より小さい効果しか持たないと推測されるが，separability という変数自体は pre-existing bias の解析にも適用できる一般的な枠組みである．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| subgroup separability | モデルが個人を protected subgroup へ分離・識別できる度合い．binary subgroup classifier の AUC で近似測定する |
| SPLIT | Supervised Prediction Layer Information Test．representation に符号化された sensitive information 量を測る post hoc test |
| underdiagnosis bias | 真に陽性の個体が誤って陰性ラベルを付けられる label noise の一種．[[Underdiagnosis_Bias]] 参照 |
| uniform degradation | separability が低いときに bias が全 group へ一様に波及し，group 間の差として現れない現象 |
| P(a\|x) | 画像 x から subgroup a を予測する確率．separability が高いほどこの推定が正確になる |

## 関連概念

- [[Underdiagnosis_Bias]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Race_Recognition_In_Medical_Images]]
- [[Equalized_Odds]]
- [[Worst_Group_Performance]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Demographic_Representation_Invariance]]
