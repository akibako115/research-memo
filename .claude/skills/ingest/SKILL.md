---
name: ingest
description: raw/ に追加された一次情報を source → article へコンパイルし，index.md と log.md を更新する．
---

raw に新しく追加されたファイルを検出し，source 作成 → 既存 article 更新または新規 article 作成 → navigation 更新まで一貫して実行する．

## 基本方針

- raw は読み取り専用．編集しない．
- source は raw 1 件に対して 1 件作成する．執筆は `wiki/sources/AGENTS.md` に従う．
- article は 1 概念 1 ファイル．執筆は `wiki/articles/AGENTS.md` に従う．
- 既存 article に情報を追加すべき場合は更新し，新概念なら新規作成する．
- synthesis の自動作成はしない．更新が必要な場合はユーザに提案する．

## Workflow

### Step 1 — 新規 raw を検出する

`$raw-source-lint` を使って，source がまだ存在しない raw ファイルを特定する．

```sh
find raw -type f -not -name '.gitkeep' -not -name '.DS_Store' | sort
rg -n '^raw:' wiki/sources --glob '*.md'
```

ユーザが対象ファイルを指定している場合は，その raw だけを処理する．指定がない場合は，uncovered raw を一覧にしてユーザに確認する．

### Step 2 — source を作成する

対象の raw ファイルを読み，`wiki/sources/AGENTS.md` に従って source を作成する．

- ファイル名: `YYYY-MM-DD_{raw_のファイル名から拡張子を除いたもの}.md`（raw の日付プレフィックスをそのまま使う）
- frontmatter に `raw:` で元の raw ファイルパスを記載する
- 原文に忠実に要約・構造化する．LLM の解釈や意見は加えない
- 末尾に関連概念を `[[Concept_Name]]` で列挙する

### Step 3 — article を作成または更新する

source から抽出した概念について，既存 article との対応を確認する．

```sh
find wiki/articles -maxdepth 1 -type f -name '*.md' -not -name 'AGENTS.md' -not -name 'README.md' | sort
```

| 状況 | アクション |
|---|---|
| 既存 article がある | source を `sources:` frontmatter に追加し，新情報で本文を更新する |
| 新概念で article がない | `wiki/articles/AGENTS.md` に従って新規作成する |
| 概念が minor で article にするほどでない | 既存 article の関連概念に wikilink を追加するか，Article Backlog に登録する |

article の更新・作成後，関連する他の article の wikilink や関連概念リストも必要に応じて更新する．

### Step 4 — navigation を更新する

```sh
cat wiki/index.md
cat wiki/log.md
```

- `wiki/index.md`: 新規 article を適切なセクションに追加する．Reading Path への追加が妥当な場合は提案する．Article Backlog から作成済みの概念があれば除去する．
- `wiki/log.md`: 作成した source / article / 更新内容を記録する．

### Step 5 — synthesis への影響を確認する

新しい source / article が既存 synthesis の内容に関わる場合，更新を提案する（自動更新はしない）．

```sh
find wiki/synthesis -maxdepth 1 -type f -name '*.md' -not -name 'AGENTS.md' -not -name 'README.md' | sort
```

## ユーザへの引数

`/ingest` だけで呼ぶと uncovered raw を一覧表示する．
`/ingest raw/papers/YYYY-MM-DD_title.pdf` のように対象を指定すると，その raw だけを処理する．

## 注意事項

- raw が PDF の場合，Read tool で読み取る．大きい PDF は pages パラメータで分割して読む．
- 1 回の ingest で大量の raw を処理する場合は，ユーザに進捗を報告しながら進める．
- source 作成後，article 作成前にユーザに「この概念で article を作るか」を確認してもよい．
