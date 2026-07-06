---
name: query
description: wiki 全体を検索して研究上の質問に回答し，Q&A を queries/ に記録する．
---

ユーザの研究上の質問に対して，wiki の articles / synthesis / sources / decisions を横断的に検索し，根拠付きで回答する．回答は `wiki/queries/` に記録する．

## 基本方針

- 回答は wiki に蓄積された知識に基づく．wiki に情報がない場合はその旨を明示する．
- 回答の根拠となった article / source / synthesis を明示する．
- 長く使える知識が生まれた場合は，article / synthesis / decision への蒸留を提案する．

## Workflow

### Step 1 — 質問を理解する

ユーザの質問を確認し，検索すべきキーワード・概念を特定する．

### Step 2 — wiki を検索する

質問に関連する情報を wiki 全体から検索する．

```sh
rg -l '<keyword>' wiki --glob '*.md'
```

必要に応じて，以下の順序で情報を探す:

1. `wiki/index.md` で関連する article / synthesis を特定
2. `wiki/articles/` で概念レベルの知識を確認
3. `wiki/synthesis/` で横断的な知識を確認
4. `wiki/sources/` で一次情報からの詳細を確認
5. `wiki/decisions/` で関連する判断理由を確認
6. `wiki/queries/` で過去の類似質問を確認

### Step 3 — 回答する

- 回答は日本語で，根拠を wikilink 付きで示す
- 推測や wiki 外の知識で補う場合は，その旨を明示する
- 「この情報は wiki にないが，raw に取り込むべき一次情報がある」場合は URL や論文名を提示する

### Step 4 — queries/ に記録する

回答を `wiki/queries/YYYY-MM-DD_{質問の要約}.md` として保存する．

```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

query の構成:

1. **質問**: ユーザの元の質問
2. **回答**: 根拠付きの回答
3. **参照した記事**: wikilink のリスト
4. **未解決・追加調査**: wiki に不足している情報や，今後調べるべきこと

### Step 5 — 蒸留を提案する

回答の中に，article / synthesis / decision として独立させるべき知識がある場合は，蒸留先を提案する．自動で蒸留はしない．

## ユーザへの引数

`/query <質問>` の形式で呼ぶ．質問は日本語でも英語でもよい．

## 注意事項

- query は思考過程の記録であり，短期的なメモとして扱う．
- 長く使える知識は articles / synthesis / decisions に蒸留することで wiki の価値が上がる．
- 過去の query と重複する質問の場合は，過去の回答を参照しつつ，新しい情報があれば更新する．
