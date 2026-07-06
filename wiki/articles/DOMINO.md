---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_domino_systematic_errors_cross_modal_embeddings]]"
  - "[[sources/2026-07-06_subgroup_performance_analysis_hidden_stratifications]]"
---

# DOMINO

モデルが全体では高性能でも，特定の画像特徴や患者群で系統的に失敗することがある．DOMINO は，cross-modal embeddings と error-aware mixture model を使って，underperforming かつ human-understandable な data slice を発見し，その slice を自然言語で説明するための slice discovery method である．

医療画像では，胸腔ドレーン，撮像条件，病変の見た目，ラベルノイズなどが hidden slice を作る．DOMINO は，こうした slice を metadata なしに発見するための手法として，[[Hidden_Stratification]] と [[Subgroup_Performance_Monitoring]] の実務に接続する．

## 何を発見するか

DOMINO が探す slice は，次の2条件を満たす必要がある．

| 条件 | 意味 |
| --- | --- |
| underperforming | model の error rate が高い |
| coherent | domain expert が理解できる共通概念でまとまっている |

単に error examples を集めるだけでは，cluster が incoherent で使えない．逆に coherent な cluster でも performance gap がなければ，model debugging には直結しない．DOMINO はこの2条件を同時に満たす slice を探す．

## 3段階の手順

```text
1. Embed
   image / signal -> cross-modal embedding

2. Slice
   embedding + true label + model prediction
   -> error-aware mixture model
   -> underperforming slices

3. Describe
   slice prototype + text embeddings
   -> natural language description
```

### Embed

DOMINO は CLIP，ConVIRT，MIMIC-CLIP，EEG-CLIP のような cross-modal embeddings を使う．画像や時系列データと自然言語を同じ空間に埋め込むことで，embedding に semantic information が入る．これにより，単なる classifier activation より coherent な slice を見つけやすくなる．

### Slice

DOMINO は embedding だけで clustering するのではなく，embedding，true label，model prediction を jointly model する error-aware mixture model を使う．これにより，たとえば false positive に偏った slice や false negative に偏った slice のように，error type が揃った subgroup を見つけやすい．

`γ` は coherence と underperformance の trade-off を調整する hyperparameter である．`γ` が大きいほど error に寄り，小さいほど embedding coherence に寄る．

### Describe

DOMINO は cross-modal text embedding を使い，candidate phrase corpus から slice を最もよく説明する phrase を返す．slice prototype から class prototype を差し引くことで，class 全体の特徴ではなく slice 固有の特徴を説明しようとする．

## Slice type

DOMINO 論文では，underperforming slice を3種類に整理している．

| Slice type | 例 | なぜ失敗するか |
| --- | --- | --- |
| rare slice | rare disease，night photos | training loss への寄与が小さい |
| correlation slice | pneumothorax と chest tube | model が spurious correlate に依存する |
| noisy label slice | 特定 scanner の label noise | slice 内の label error が高い |

この分類は医療画像 fairness でも有用である．demographic subgroup だけでなく，artifact，label quality，visual phenotype も performance gap の原因になる．

## GEORGE との違い

| 手法 | 主な目的 | 入力 representation | 出力 |
| --- | --- | --- | --- |
| GEORGE | proxy subclass labels を作り，Group DRO で改善する | ERM model feature / pretrained embeddings | clusters |
| DOMINO | coherent underperforming slice を発見・説明する | cross-modal embeddings + labels + predictions | slices + natural language descriptions |

GEORGE は [[Worst_Group_Performance]] の改善に重点がある．DOMINO は slice discovery の発見精度と説明性に重点がある．ただし，DOMINO で発見した slice を downstream の robust training や targeted data collection に使うこともできる．

## 医療画像での使い方

DOMINO は，モデル監査で次のように使える．

**Step 1 — Validation / deployment data を集める**

代表性のある labeled validation set が望ましい．post-deployment monitoring では，labels が遅れて得られる場合にも，予測と embedding を蓄積しておく．

**Step 2 — Cross-modal embedding を選ぶ**

胸部X線なら ConVIRT / MIMIC-CLIP / BiomedCLIP のような domain-specific embedding が候補になる．ただし，Bissoto et al. の結果では natural-image CLIP でも meaningful performance gaps を露出できる場合がある．

**Step 3 — DOMINO で slice を発見する**

error-aware mixture model により，false positive / false negative など error type が揃った slice を探す．

**Step 4 — Natural language description と human review を併用する**

description は auditor の手がかりになるが，そのまま真実として扱わない．domain expert が代表例を確認し，slice の意味と臨床的重要性を判断する．

**Step 5 — 報告・改善に使う**

発見した slice は subgroup report，data collection，annotation schema 更新，robust training，deployment guardrail に使える．

## 注意点

DOMINO は model debugging tool であり，捕捉できない failure mode は残る．代表性のある test set での standard evaluation を置き換えるものではない．また，web 由来 image-text embeddings は社会的バイアスを含みうるため，underrepresented groups や concepts の error mode を見逃す可能性がある．

医療で使う場合，DOMINO が出した natural language description は仮説生成として扱い，臨床的な subclass definition や regulatory reporting には human validation が必要である．

## リファレンス

| 用語 | 意味 |
| --- | --- |
| slice | 共通 attribute / characteristic を持つ data subgroup |
| slice discovery method | underperforming かつ coherent な slice を自動発見する方法 |
| cross-modal embedding | image / signal と text を同じ semantic space に埋め込む representation |
| error-aware mixture model | embedding，label，prediction を同時に model する mixture model |
| precision-at-k | discovered slice の top k examples が ground truth slice に属する割合 |
| natural language slice description | 発見した slice の共通特徴を表す phrase |

## 関連概念

- [[Hidden_Stratification]]
- [[Subgroup_Performance_Monitoring]]
- [[Worst_Group_Performance]]
- [[Medical_Image_Fairness_Audit_Loop]]
- [[Spurious_Correlation]]
