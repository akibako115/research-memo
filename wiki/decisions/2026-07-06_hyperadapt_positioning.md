# HyperAdapt を研究主軸ではなく比較対象として扱う

## Context

現状の研究テーマは，患者属性条件付きモデルが医療画像分類の subgroup fairness / reliability に与える影響を調べることである．

HyperAdapt 的な実装は，患者属性を compact embedding にし，hypernetwork-style module で selected layers を変調する強い条件付きモデルとして有用である．一方で，特定の新しい preprint や複雑な実装に研究全体を依存させると，研究の説明が弱くなり，効果の切り分けも難しくなる．

## Decision

HyperAdapt は研究の中心仮説ではなく，比較対象・再現対象・強い複雑モデルとして扱う．

研究の主軸は，次の問いに置く．

> 医療画像分類において，患者属性を明示的に使う条件付きモデルは subgroup fairness / reliability を改善するのか．改善する場合，それはどの融合方式・どの層・どの属性・どの複雑度に由来するのか．

## Survey Axes

今後のサーベイは，次の3層に分ける．

- Fairness in medical imaging: subgroup gap，protected attribute，評価指標，データセット，pretraining / fine-tuning と公平性の関係
- 画像 + テーブルデータ / 属性条件付きモデル: late fusion，FiLM，conditional normalization，hypernetwork，adapter，LoRA / PEFT
- 条件付きモデルの解析: 属性情報の使われ方，特徴空間・activation・attention・adapter weight の subgroup 差，shortcut / leakage / group-specific specialization の検出

## Experiment Direction

実験は，単純な条件付きモデルから複雑なモデルへ段階的に進める．

- 主 baseline: ImageNet 初期化 ResNet-50 の end-to-end fine-tuning
- simple conditional baseline: image feature + attribute MLP の late fusion
- lightweight modulation: FC-only FiLM / HyperLinear
- mid complexity: stage4-only FiLM / HyperAdapter
- higher complexity: stage3+4 modulation
- upper-bound / reproduction: all-stage HyperAdapter，frozen 2-stage adapter

## Rationale

- HyperAdapt を主役にすると，研究が1本の新しい preprint と複雑な実装に寄りすぎる．
- 2段階 frozen adapter は，固定済み診断モデルへの後付け adapter という問題設定では意味があるが，初期探索では checkpoint 管理と比較条件が複雑になる．
- 全層 HyperAdapter は表現力が高い一方で，公平性改善なのか属性ごとの別モデル化なのかが曖昧になりやすい．
- 複雑度を段階化すれば，どの程度の条件付き変調から subgroup fairness / reliability が改善するのかを説明しやすい．

## Review Conditions

次の場合は，HyperAdapt の位置づけを見直す．

- HyperAdapt 系手法が複数の査読済み論文で安定して有効性を示した場合
- lightweight modulation では改善が見られず，複雑な per-sample weight modulation でのみ一貫した改善が出た場合
- モデル解析により，HyperAdapter が単なる group-specific specialization ではなく，疾患関連特徴の補強に寄与していると示せた場合
