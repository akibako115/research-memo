---
name: raw-source-lint
description: この llm-wiki プロジェクトにおいて, raw/ に追加された資料の source 化漏れを検出する．
---

`wiki/sources` の本文を読まず，この skill に同梱した lint script を使って raw と source frontmatter の対応を確認する．

## Workflow

1. リポジトリ root で以下を実行する．

```sh
python3 .claude/skills/raw-source-lint/scripts/lint_raw_sources.py
```

2. 出力を以下のように読む．

| セクション | 意味 |
|---|---|
| `uncovered raw files` | grouped unit 外の raw ファイルで，source frontmatter から参照されていないもの |
| `uncovered grouped files` | grouped raw unit 内のファイルで，どの source の `scope` にも入っていないもの |
| `missing raw references` | source frontmatter が存在しない raw path を参照しているもの |
| `duplicate raw references` | 複数 source が同じ raw ファイルを参照しているもの |
| `warnings` | 動作はするが推奨形ではないメタデータ．多くは古い grouped unit 書式 |

3. ユーザが内容レビューや source コンパイルを依頼していない限り，raw や source 本文は開かず，backlog だけを報告する．

## Project Conventions

- raw/source 検出は metadata-only で行う．
- grouped raw unit は `wiki/index/raw_units.json` で定義する．
- grouped unit の source frontmatter は以下の形式にする．

```yaml
raw: "raw/notes/chapters/"
raw_unit: "data-engineering-data-science-textbook"
scope:
  - "02-data-modeling-pipeline.md"
```

- `uncovered grouped files` には，source 化前の future chapter backlog が出る想定である．
- ユーザが full ingest completion を求めていない限り，`uncovered grouped files` は health check failure とみなさない．

## When Fixing Findings

- 通常 raw ファイルが uncovered の場合は，`raw: "<path>"` を持つ `wiki/sources/*.md` を 1 つだけ作成または更新する．
- grouped chapter が uncovered の場合は，`raw:` に group folder，`scope:` に chapter file を持つ source を作成または更新する．
- source が存在しない raw path を参照している場合は，raw file の rename より source frontmatter の path 修正を優先する．
- raw file は編集しない．
