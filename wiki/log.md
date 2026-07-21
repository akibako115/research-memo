# Wiki Log

## 2026-07-21（続き）

- raw 1件投入: `raw/papers/2305.01397v3.pdf`（Petersen, Ferrante, Ganz, Feragen, "Are demographically invariant models and representations in medical imaging fair?" arXiv:2305.01397v3）
- source 1件作成: `2026-07-21_demographically_invariant_models_representations_medical_imaging_fair`
- article 1件新規作成: [[Demographic_Representation_Invariance]] — marginal / class-conditional / counterfactual representation invariance を，statistical parity・separation との対応関係と，それぞれの代償（予測精度低下，disparate treatment，within-class variation の均一化）として整理する新概念
- 既存 article 更新（wikilink・関連セクション追加）: [[Equalized_Odds]]，[[Race_Recognition_In_Medical_Images]]，[[Medical_Image_Fairness_Evaluation]]，[[Subgroup_Separability]]，[[Hidden_Stratification]]
- index.md 更新: Reading Path 1 に [[Demographic_Representation_Invariance]] 追加，Articles の「医療画像 Fairness: 評価」セクションに追加

## 2026-07-21

- raw 1件投入: `raw/papers/2307.02791v1.pdf`（Jones, Roschewitz, Glocker, "The Role of Subgroup Separability in Group-Fair Medical Image Classification," arXiv:2307.02791）．ファイル名が命名規則（`YYYY-MM-DD_{title}`）に従っていないため，source 側で今日の日付をプレフィックスに使用．
- source 1件作成: `2026-07-21_subgroup_separability_group_fair_medical_image_classification`
- article 1件新規作成: [[Subgroup_Separability]] — subgroup separability（画像から subgroup member を識別できる度合い）が underdiagnosis bias の group fairness metric への現れ方を左右するという新概念
- 既存 article 更新（wikilink・関連セクション追加）: [[Underdiagnosis_Bias]]，[[Medical_Image_Fairness_Evaluation]]，[[Race_Recognition_In_Medical_Images]]，[[Worst_Group_Performance]]，[[Equalized_Odds]]，[[Fairness_Mitigation_In_Medical_Imaging]]
- index.md 更新: Reading Path 1 に [[Subgroup_Separability]] 追加，Articles の「医療画像 Fairness: 評価」セクションに追加

## 2026-07-06

- wiki 初期構築: raw 22件（論文 PDF）を投入，source 22件・article 22件を一括作成
- synthesis 1件作成: [[Medical_Image_Fairness_Audit_Loop]]
- decisions 2件作成: HyperAdapt の位置づけ，初期モデルの方針
- queries 4件投入: Deep Research レポート 3件，論文読み順リスト 1件
- health check 実施: index.md 作成，frontmatter 整備，wikilink 修正
- `[[Medical_Image_Fairness]]` 8箇所 → `[[Medical_Image_Fairness_Audit_Loop]]` に統合
- Image_Tabular_Fusion を articles → synthesis に昇格
- DAFT article 作成: FiLM との違い，two-way exchange，AD 診断での性能，fairness での位置づけ
- synthesis/AGENTS.md 作成: synthesis 層の執筆ガイドライン（articles との区別，構成パターン）
- skills 追加: ingest（raw → source → article），query（wiki 検索 + Q&A 記録），article-create（backlog → article）
- query 追加: Fusion × Hidden Subgroup Fairness の交差領域の検討（fairness 評価軸，impossibility theorem，設計空間，本質的な難しさ，研究優先度）
