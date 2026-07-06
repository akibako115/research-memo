---
name: article-create
description: 指定した概念の article を，既存 sources から作成し，index.md と log.md を更新する．
---

Article Backlog や wikilink で参照されているが未作成の概念について，既存の sources と articles から情報を集め，新規 article を作成する．

## 基本方針

- `wiki/articles/AGENTS.md` の執筆ガイドラインに従う．
- 1 概念 1 ファイル．問題起点で「なぜこの概念が必要か」から書く．
- 既存の sources を主な情報源とし，sources に情報が不足している場合はその旨を明示する．
- article 作成後，index.md と log.md を更新する．

## Workflow

### Step 1 — 概念と情報源を特定する

指定された概念名で，既存の参照箇所と関連 source を検索する．

```sh
rg -n '[[<Concept_Name>]]' wiki --glob '*.md'
rg -l '<keyword>' wiki/sources --glob '*.md'
```

- どの source / article がこの概念に言及しているかを把握する
- Article Backlog に記載がある場合は，そこの備考も確認する

### Step 2 — 関連 source を読む

概念に関連する source を読み，article に含めるべき情報を収集する．

### Step 3 — article を作成する

`wiki/articles/<Concept_Name>.md` を作成する．

frontmatter:

```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[sources/<source_file>]]"
---
```

構成は `wiki/articles/AGENTS.md` に従う:

1. 導入（問題起点で「なぜ必要か」から）
2. 全体像（テーブルや図で構造を一望）
3. 具体例（シナリオベース，Option）
4. 設計思想（なぜこの構造か）
5. リファレンス（ルックアップ用テーブル）
6. 関連概念（wikilink リスト）

### Step 4 — 既存 article の wikilink を確認する

新しい article への `[[Concept_Name]]` が既存 article に含まれている場合，リンク先が正しく解決されることを確認する．必要に応じて関連概念リストに追加する．

### Step 5 — navigation を更新する

- `wiki/index.md`: Articles セクションの適切なカテゴリに追加する．Article Backlog から除去する．Reading Path への追加が妥当な場合は提案する．
- `wiki/log.md`: 作成を記録する．

## ユーザへの引数

`/article-create <Concept_Name>` の形式で呼ぶ．

例:
- `/article-create DAFT`
- `/article-create Conditional_Modulation`
- `/article-create Spurious_Correlation`

概念名が未指定の場合は，Article Backlog から参照数が多い順に候補を提示する．

## 注意事項

- wiki に十分な source がない場合は，「この概念の article を充実させるには，以下の一次情報を raw に追加する必要がある」と提案する．
- 既存 article との重複を避ける．概念が既存 article の一部として扱われている場合は，独立 article にすべきか判断してからユーザに確認する．
