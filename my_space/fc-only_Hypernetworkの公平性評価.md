## 0. 全体性能
## 1. 単一属性での公平性

  - sex, race, ethnicity, frontal_lateral, ap_pa, age_group, bmi_group のどれで gap が大きいか
  - gap が recall_pos 側なのか recall_neg 側なのか
  - ResNet と FiLM で gap が縮む/広がるか

  __仮説__:
  H1: FiLM は全体性能だけでなく、特定属性の recall gap を改善する
  - 否定．むしろ患者属性 (age, bmi, race)を中心に悪化する．
  H2: 改善/悪化は AUROC より recall_pos/recall_neg に出やすい
  - 

  
## 2. 複数属性での公平性

__ヒートマップで確認すること__: 
  - 低性能セルがどの intersection に集中しているか
  - その低性能セルは train sample が少ないだけか
  - FiLM の改善/悪化が特定セルに偏っているか

__仮説__: 
  H3: 単一属性では平均化されるが、2属性 intersection では弱い subgroup が現れる
  H4: 撮影条件 × 患者属性で性能差が大きく、撮影条件が上位要因になっている
  H5: FiLM の効果は全 subgroup に均一ではなく、特定 intersection で改善/悪化する


__Conditioned barで確認すること__: 
  - attribute_a の各 group 内で attribute_b 差があるか
  - condition 内 gap と overall gap のどちらが大きいか
  - overall gap が大きい場合、それは condition 間差なのか、condition 内 subgroup 差なのか

__仮説__: 
  H6: 撮影条件が性能差の主要因で、その内部に患者属性差が重なる
  H7: 患者属性差は frontal と lateral で同じではない


__Train data composition vs Metricsで確認すること__: 
  - train samples が少ない subgroup ほど AUROC/recall が低いか
  - train positive rate が高い subgroup ほど recall_pos が高く recall_neg が低いか
  - train positives が少ない subgroup で recall_pos が低いか
  - train negatives が少ない subgroup で recall_neg が低いか
  - ResNet と FiLM でこの依存が違うか

__仮説__: 
  H8: subgroup 性能低下は train sample size の少なさで部分的に説明される
  H9: recall_pos/recall_neg の偏りは train positive rate に対応する
  H10: FiLM は train composition への依存を弱める、または逆に強める