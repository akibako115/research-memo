---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_hidden_stratification_medical_imaging]]"
  - "[[sources/2026-07-06_subgroup_performance_analysis_hidden_stratifications]]"
  - "[[sources/2026-07-06_fairness_beyond_demographics_hidden_cohorts]]"
---

# Hidden Stratification

医療画像モデルの平均 AUROC や sensitivity が高くても，その疾患ラベルの内部にある重要な症例群で性能が低いことがある．Hidden stratification は，粗い superclass label の内部に臨床的・視覚的に異なる subclass が隠れ，aggregate metric がその失敗を覆い隠す問題である．

これが重要なのは，医療で見逃してはいけない症例ほど，しばしば rare，subtle，dangerous だからである．モデルがよくある軽症例や治療済み症例では高性能でも，少数で重篤な未治療例を見逃すなら，平均性能は臨床安全性を証明しない．

## Superclass の中に subclass が隠れる

医療画像のラベルは，機械学習の都合で粗くまとめられることが多い．しかし同じ疾患名でも，画像所見，重症度，治療状態，部位，原因，患者背景は異なる．

```text
superclass label: pneumothorax
├── with chest drain
└── without chest drain

superclass label: abnormal musculoskeletal x-ray
├── fracture
├── hardware
└── degenerative joint disease
```

superclass の大きな subset で性能が高いと，aggregate AUROC は高く見える．その一方で，少数 subclass の sensitivity や PPV が低くても，平均指標では見えにくい．

## 起こりやすい条件

Hidden stratification は，次の条件で起こりやすい．

| 条件 | 何が起きるか | 医療画像での例 |
| --- | --- | --- |
| low prevalence | 少数 subclass が training / evaluation で埋もれる | cervical fracture，subtle fracture |
| poor label quality | superclass label が subclass を正しく反映しない | degenerative joint disease が “abnormal” に入りにくい |
| subtle discriminative features | 視覚的差異が小さく，モデルが学びにくい | subtle hip fracture |
| spurious correlate | 疾患ではなく処置・撮像・施設などを手がかりにする | pneumothorax の chest drain |

これらは [[Medical_Image_Fairness_Audit_Loop]] とも接続する．demographic subgroup だけでなく，疾患 phenotype，重症度，治療状態，撮像条件，施設，ラベル品質によっても subgroup reliability は変わる．

## 測定方法

| 方法 | 何をするか | 強み | 弱み |
| --- | --- | --- | --- |
| schema completion | 事前に subclass schema を定義し，test data に subclass label を付ける | 報告基準を標準化しやすい | 想定外 subclass を見落とす |
| error auditing | model error を人間が確認し，一貫した失敗 pattern を探す | model-specific な失敗を見つけやすい | auditor の気づきに依存する |
| algorithmic measurement | clustering などで underperforming group を自動探索する | human burden を減らせる | feature space で分離できない subclass は見つからない |

重要なのは，これらを training set 全体に対してだけでなく，held-out test set の評価・報告に組み込むことである．regulatory や deployment の文脈では，aggregate score だけでなく subclass performance を示す必要がある．

## Spurious correlate と臨床リスク

Hidden stratification の典型例は，CXR14 の pneumothorax における chest drain である．chest drain は pneumothorax の治療器具であり，診断の causal feature ではない．しかし dataset 内で pneumothorax と強く共起すると，モデルは chest drain を pneumothorax の手がかりとして使いやすい．

この場合，treated pneumothorax では高性能でも，chest drain のない untreated pneumothorax で性能が落ちる．臨床的には，後者の方が life-threatening で見逃してはいけない．つまり，spurious correlate は単なるデータセットバイアスではなく，臨床リスクの重みを反転させる可能性がある．

## Fairness との違いと接続

一般的な fairness 評価は，sex，race，age などの protected attributes ごとの performance gap を見ることが多い．Hidden stratification は，それより広く「ラベル内部の見えていない subgroup」を対象にする．

| 観点 | Fairness subgroup | Hidden stratification |
| --- | --- | --- |
| subgroup の定義 | demographic / protected attribute が多い | phenotype，治療状態，重症度，label quality，artifact なども含む |
| 主な問題 | 属性群間の不公平 | aggregate metric が subclass failure を隠す |
| 発見方法 | 既知属性で stratify | schema completion，audit，clustering |
| 医療画像での重要性 | 患者属性ごとの安全性 | rare / subtle / dangerous cases の安全性 |

実際の安全性評価では，両方が必要になる．たとえば race ごとの性能が同じでも，ある race 内の rare phenotype で失敗していれば問題は残る．逆に hidden subclass が protected attribute と相関すれば，hidden stratification は demographic fairness gap として現れることもある．

## 条件付きモデルでの意味

[[FiLM]]，[[HyperFusion]]，[[Image_Tabular_Fusion]] のような条件付きモデルは，患者属性や臨床情報を使って subgroup reliability を改善する可能性がある．しかし，hidden stratification の観点では，平均性能改善だけでは不十分である．

条件付きモデルが本当に有用かを見るには，次を確認する必要がある．

| 検証 | 問い |
| --- | --- |
| known subclass performance | 既知の疾患 subtype / severity / treatment status で改善するか |
| hidden subgroup discovery | clustering や error audit で underperforming group が残っていないか |
| subgroup-specific calibration | subclass ごとの confidence がずれていないか |
| spurious correlate dependence | 処置器具，施設，撮像条件を疾患 signal と誤用していないか |
| worst-group metric | 平均ではなく最悪 subclass が改善するか |

## Performance monitoring への拡張

hidden stratification は一度の評価で終わる問題ではない．運用後のデータ分布や撮像プロトコルが変わると，新しい hidden subgroup が出る可能性がある．そのため，[[Subgroup_Performance_Monitoring]] では，既知 metadata による subgroup report と，embedding / prediction に基づく subgroup discovery を併用する．

Bissoto et al. の結果は，sex，age，ethnicity などの metadata subgroup では見えない低性能 cluster が，CLIP / BiomedCLIP feature と model prediction を使った subgroup discovery で見つかることを示している．これは，fairness auditing を demographic attributes だけに閉じないための実務的な手段になる．

Masroor et al. の [[Hidden_Cohort_Fairness]] は，hidden stratification を検出だけで終わらせず，appearance-based hidden cohorts を fairness optimization の group として使う．LHCF では image embeddings を GMM で cluster 化し，その cohort label に対して worst loss や loss gap を下げる．これにより，demographic labels を training に使わなくても，visible demographic groups や intersectional groups の fairness が改善しうる．

## リファレンス

| 用語                      | 意味                                                               |
| ----------------------- | ---------------------------------------------------------------- |
| superclass              | 機械学習で直接予測する粗い class label                                        |
| subclass                | superclass 内の臨床的・視覚的に異なる subset                                  |
| hidden stratification   | subclass がラベルや評価で明示されず，aggregate metric が subclass failure を隠す現象 |
| schema completion       | subclass schema を追加して test data を明示的に再ラベルする評価                    |
| error auditing          | model errors を人間が調べ，規則的な失敗 subgroup を探す評価                        |
| algorithmic measurement | clustering などで underperforming subgroup を探索する評価                  |
| spurious correlate      | causal ではないが label と共起し，モデルが手がかりにする特徴                            |

## 関連概念

- [[Subgroup_Reliability]]
- [[Subgroup_Performance_Monitoring]]
- [[Medical_Image_Fairness_Audit_Loop]]
- [[Fairness_Evaluation]]
- [[Spurious_Correlation]]
- [[Worst_Group_Performance]]
- [[Hidden_Cohort_Fairness]]
