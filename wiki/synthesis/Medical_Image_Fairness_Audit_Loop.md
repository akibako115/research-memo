---
created: 2026-07-06
updated: 2026-07-06
articles:
  - "[[Medical_Image_Fairness_Evaluation]]"
  - "[[Underdiagnosis_Bias]]"
  - "[[Race_Recognition_In_Medical_Images]]"
  - "[[Foundation_Model_Fairness]]"
  - "[[Vision_Language_Model_Fairness]]"
  - "[[Fairness_Mitigation_In_Medical_Imaging]]"
  - "[[Fairness_Under_Distribution_Shift]]"
  - "[[Hidden_Stratification]]"
  - "[[Hidden_Cohort_Fairness]]"
  - "[[Subgroup_Performance_Monitoring]]"
---

# Medical Image Fairness Audit Loop

医療画像 fairness は，1つの metric を最小化する問題ではなく，model がどの subgroup / hidden cohort / deployment domain で臨床的に危険な失敗をするかを継続的に監査し，原因に応じて介入し，再び外部環境で検証する loop である．

この synthesis の中心命題は，**平均性能，ID fairness，attribute removal のどれも単独では安全性を保証しない**ということだ．医療画像モデルは，画像から sensitive attributes を encode でき，known demographic subgroup だけでなく hidden phenotype や artifact でも失敗し，さらに ID で fair な model が OOD で fair とは限らない．

## Loop 全体像

```text
1. Utility を測る
   overall AUC / subgroup AUC / calibration

2. Harm direction を決める
   underdiagnosis / overdiagnosis / ranking / calibration

3. Known subgroup を監査する
   sex / age / race / genotype / site / clinical metadata

4. Hidden subgroup を探索する
   embedding / prediction / clustering / human review

5. Representation を監査する
   sensitive attribute prediction / demographic encoding

6. Bias source を仮説化する
   imbalance / label noise / shortcut / pre-training bias / domain gap

7. Mitigation を選ぶ
   data / training / threshold / representation / model selection

8. ID と OOD で再評価する
   external validation / subgroup shift decomposition / monitoring
```

この loop は，[[Medical_Image_Fairness_Evaluation]]，[[Subgroup_Performance_Monitoring]]，[[Fairness_Mitigation_In_Medical_Imaging]] をつなぐ実務的な見取り図である．

## Step 1: 平均性能を出発点にしない

医療画像では，overall AUC が高くても，特定 subgroup に対する clinical harm が大きいことがある．特に triage / screening では，疾患あり患者を健康側に寄せる [[Underdiagnosis_Bias]] が重要になる．

| 失敗方向 | 指標 | 使う場面 |
| --- | --- | --- |
| 疾患ありを陰性とする | FNR / TPR gap | disease label prediction |
| 疾患ありを `No Finding` とする | `No Finding` FPR gap | chest X-ray triage |
| positive cases の順位が低い | [[Pairwise_Fairness]] / PFD | risk score prioritization |
| 確率がずれる | ECE gap / calibration | probability を意思決定に使う場合 |

したがって，fairness 評価では，AUC gap だけでなく，害の方向に合った threshold metric，ranking metric，calibration metric を選ぶ．

## Step 2: Known subgroup と hidden subgroup を両方見る

sex，age，race，genotype などの known subgroup は，regulatory reporting と臨床説明に必要である．しかし，known subgroup だけでは不十分である．[[Hidden_Stratification]] は，疾患 subtype，severity，treatment status，image artifact，label quality のような hidden factor で model failure が起きることを示す．

| Subgroup type | 例 | 主な用途 |
| --- | --- | --- |
| demographic | sex，age，race | fairness reporting |
| clinical | genotype，comorbidity，site | disease-specific safety |
| visual hidden cohort | lesion appearance，artifact | systematic error discovery |
| representation cluster | embedding-based cohort | metadata がない場合の監査 |

[[Hidden_Cohort_Fairness]] は，この発想を mitigation へ進める．hidden cohorts を発見して終わりではなく，それを fairness optimization の group として使うことで，demographic labels なしでも visible demographic fairness を改善できる可能性がある．

## Step 3: Sensitive attribute を「使っていない」は弱い主張

[[Race_Recognition_In_Medical_Images]] と [[Vision_Language_Model_Fairness]] は，medical image の pixel / embedding から race，age，sex，intersectional subgroup が予測できることを示す．protected attribute column を model input から除いても，image representation が sensitive signal を持つなら，colorblind design は fairness の保証にならない．

```text
race column なし
  != race information なし

image pixels / reports / pre-training distribution
  -> representation
  -> demographic encoding
  -> subgroup-specific errors
```

そのため，fairness audit では subgroup outcome だけでなく，frozen representation から sensitive attributes がどれだけ予測できるかも見る．

## Step 4: Mitigation は原因に合わせる

fairness gap を見つけた後，すぐに adversarial training や resampling を使うのではなく，bias source を仮説化する．

| Bias source | 代表的な介入 |
| --- | --- |
| demographic imbalance | resampling，balanced mini-batch，data collection |
| label noise / annotation bias | multi-annotator，label audit |
| spurious correlation | shortcut testing，confounder removal |
| representation encoding | adversarial removal，disentanglement，orthogonality |
| hidden cohort failure | subgroup discovery，GroupDRO，LHCF |
| threshold disparity | subgroup threshold，calibration |
| domain gap | external validation，domain adaptation，monitoring |

[[FairREAD]] や [[FCRO]] は representation / fusion 側の mitigation，[[Pairwise_Fairness]] は ranking 側の mitigation，[[Hidden_Cohort_Fairness]] は hidden cohort 側の mitigation として位置づけられる．

## Step 5: ID fairness を OOD fairness と混同しない

[[Fairness_Under_Distribution_Shift]] は，ID で fair な model が OOD でも fair とは限らないことを示す．ID と OOD の overall AUROC は相関しやすいが，fairness gap は相関しない場合がある．

```text
ID model:
  subgroup gap が小さい

OOD deployment:
  group A の performance が大きく悪化
  group B は少しだけ悪化
  -> 新しい fairness gap が発生
```

実務上は，ID fairness gap 最小の model を選ぶだけでは不十分である．representation に demographic information が少ない model selection，external validation，post-deployment subgroup monitoring を組み合わせる必要がある．

## Step 6: Fairness と calibration / utility の trade-off を見える化する

fairness mitigation は，leveling down や calibration gap 悪化を起こすことがある．[[Equalized_Odds]] は FPR/FNR parity を明確にするが，group calibration と両立しない場合がある．[[Fairness_Under_Distribution_Shift]] では，ID fairness を改善した locally optimal model が ECE gap，average precision，F1 score で悪化する例が示されている．

したがって，model selection では Pareto front を使い，次を同時に見る．

| 軸 | 見る理由 |
| --- | --- |
| overall utility | clinical usefulness を保つ |
| worst subgroup utility | harmful leveling down を避ける |
| fairness gap | subgroup disparity を測る |
| calibration | risk score の絶対値を安全に使う |
| OOD robustness | deployment shift に耐える |
| representation encoding | shortcut reliance の proxy |

## Research design への示唆

医療画像 fairness の研究では，以下を最低限の報告単位にする．

| 報告項目 | 理由 |
| --- | --- |
| dataset demographic distribution | imbalance と subgroup sparsity を解釈するため |
| disease prevalence by subgroup | disparity が label distribution 由来か見るため |
| subgroup size / confidence interval | small subgroup の不安定性を避けるため |
| harm-aligned metrics | underdiagnosis / overdiagnosis / ranking を区別するため |
| hidden subgroup analysis | metadata にない failure を見つけるため |
| representation attribute prediction | sensitive encoding を確認するため |
| ID / OOD split | deployment generalization を見るため |
| mitigation trade-off | fairness 改善が utility / calibration を壊さないか見るため |

## この wiki での使い方

新しい医療画像 fairness 論文を読むときは，次の問いで article へ蒸留する．

1. 何を sensitive attribute / subgroup として扱うか．
2. 何の harm を fairness metric に対応させているか．
3. known subgroup と hidden subgroup のどちらを扱うか．
4. model は sensitive information を encode しているか．
5. mitigation は data，model，post-processing，selection のどこに介入するか．
6. ID だけでなく OOD / external validation を見ているか．
7. fairness 改善が calibration / utility / worst group を壊していないか．

この loop に当てはめると，個別手法の違いよりも，「どの failure mode に対して，どの証拠で，どの介入を選んだか」が比較しやすくなる．

## 関連概念

- [[Medical_Image_Fairness_Evaluation]]
- [[Underdiagnosis_Bias]]
- [[Race_Recognition_In_Medical_Images]]
- [[Foundation_Model_Fairness]]
- [[Vision_Language_Model_Fairness]]
- [[Fairness_Mitigation_In_Medical_Imaging]]
- [[Fairness_Under_Distribution_Shift]]
- [[Hidden_Stratification]]
- [[Hidden_Cohort_Fairness]]
- [[Subgroup_Performance_Monitoring]]
