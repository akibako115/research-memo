---
name: wiki-health-check
description: この llm-wiki プロジェクトが，raw，sources，articles，synthesis，queries，recipes，incidents，decisions，my_space の各層に適切な内容を置けているか確認する．
---

このプロジェクトの llm-wiki が，層ごとの責務に沿って整理されているかを確認する．まず metadata-only の検査を行い，必要な場合だけ本文を読む．

## 基本方針

- raw は編集しない．
- まず `AGENTS.md`，各層 `README.md`，必要な層の `AGENTS.md` を確認する．
- source 本文や raw 本文は，置き場所の妥当性判断に必要な場合だけ読む．
- raw/source 対応は `$raw-source-lint` と同じ手順に従う．
- 結果は「重大度順の指摘」と「次に直す順番」で返す．

## Workflow

1. ルールを確認する．

```sh
sed -n '1,220p' AGENTS.md
find wiki -maxdepth 2 -name 'README.md' -print | sort
```

必要に応じて以下も読む．

```sh
sed -n '1,220p' wiki/sources/AGENTS.md
sed -n '1,260p' wiki/articles/AGENTS.md
sed -n '1,220p' wiki/synthesis/AGENTS.md
```

2. raw/source 対応を `$raw-source-lint` と同じ手順で軽量確認する．

3. frontmatter と参照を機械的に確認する．

```sh
rg -n '^---$|^created:|^updated:|^raw:|^raw_unit:|^scope:|^sources:|^related:' wiki --glob '*.md'
rg -n '\[\[' wiki --glob '*.md'
```

4. 層の混入を確認する．

見る観点:

| 層 | あるべき内容 | 混入のサイン |
|---|---|---|
| `raw/` | 一次情報，immutable | AI 要約，作業ログ，`.DS_Store`，加工済み知識 |
| `wiki/sources` | raw 1 件または grouped scope への忠実な抽出 | 複数 raw の横断解釈，LLM の意見/要約 |
| `wiki/articles` | 1概念1ファイルの再利用知識 | 一回限りの計画/知識，作業ログ，長いロードマップ |
| `wiki/synthesis` | 複数 article を横断する長期的統合理解 | タスク一覧，短期計画，汎用的でない知識/技術のまとめ |
| `wiki/queries` | QA，調査，計画検討の履歴 | 蒸留済みなのに frontmatter やリンクがない，長期知識が未分離 |
| `wiki/recipes` | 次回も使える手順 | 判断理由や概念説明が主役 |
| `wiki/incidents` | エラー，詰まり，原因，解決，再発防止 | 汎用手順や設計方針だけが置かれている |
| `wiki/decisions` | なぜその方針にしたか | 手順そのもの，単なる調査ログ |
| `my_space` | ユーザ自身の理解メモ | wiki 正式記事の代替，raw の代替 |

5. 必要に応じて候補ファイルだけ本文を読む．

例:

```sh
sed -n '1,180p' wiki/synthesis/<candidate>.md
sed -n '1,180p' wiki/queries/<candidate>.md
```

6. synthesis 欠落候補を確認する．

見る観点:

- 関連 article が 3 件以上あり，比較・使い分け・全体像が必要なのに synthesis がない
- 複数 article に同じ比較表，選択基準，メリット・デメリットが重複している
- `wiki/index.md` の `Synthesis Candidates` に候補があるのに，対応する synthesis が未作成のままになっている
- `queries/` に複数 article を横断する回答が残っているが，synthesis に蒸留されていない

7. navigation の古さを確認する．

この wiki では Reading Paths / Article Backlog / Synthesis Candidates を完全自動生成しない．health check は古さや欠落の検出までを行い，どの導線へ接続するかは LLM が `purpose.md` と現在の問いに照らして判断する．

見る観点:

- 新規 article が `wiki/index.md` の Articles に載っているか
- 重要 article が Reading Paths / Synthesis / Article Backlog のいずれかに接続されているか
- Reading Paths 内の wikilink が存在するか
- Backlog に既存 article が残っていないか
- Synthesis が作成済みなのに `wiki/index.md` の Synthesis に載っていないものがないか
- article 作成や synthesis 作成があったのに `wiki/log.md` に主要履歴が残っていない場合，必要に応じて記録を提案する

navigation 確認例:

```sh
find wiki/articles -maxdepth 1 -type f -name '*.md' -not -name 'AGENTS.md' | sort
rg -n '^## Reading Paths|^## Articles|^## Synthesis|^## Article Backlog|\\[\\[' wiki/index.md
find wiki/synthesis -maxdepth 1 -type f -name '*.md' -not -name 'AGENTS.md' | sort
```

synthesis 確認例:

```sh
find wiki/articles -maxdepth 1 -type f -name '*.md' -not -name 'AGENTS.md' | sort
rg -n '^## Synthesis Candidates|Authentication|認証|使い分け|比較|選択基準' wiki --glob '*.md'
```

## Report Format

報告は以下の形にする．

```md
## 総合評価

## 指摘

1. [重大度] 指摘タイトル
   - 対象: path
   - 問題: 何が llm-wiki の思想とズレているか
   - 推奨対応: どう直すか

## 層別評価

| 層 | 評価 | コメント |
|---|---|---|

## 優先対応順
```

## 判断ルール

- `synthesis/` に project roadmap や実行計画がある場合は原則として問題にする．
- 関連 article が 3 件以上あり，横断的な比較・使い分け・設計判断が発生しているのに synthesis がない場合は，synthesis 候補として指摘する．ただし，ユーザの明示依頼なしに自動作成はしない
- article に重複した比較表や選択基準が増えている場合は，synthesis へ蒸留する候補として提案する
- `queries/` に recipe / decision / article 相当の知識が残っているだけなら，すぐ削除ではなく「蒸留先を追記する」「必要に応じて分離する」と提案する．
- 未作成 wikilink は，今後の学習・インターン進捗で補充する backlog として扱う．参照数が多いものだけ優先指摘する．
- grouped raw unit の未処理 chapter は，full ingest completion を求められていない限り health check failure にしない．
- raw immutable の本質は原文内容を編集しないことであり，ファイル名のリネームを常に禁止するものではない．
- source frontmatter や参照を安全に追従できる場合は，raw の既存ファイル名を命名規則に合わせてリネームしてよい．
- すでに多くの wiki から参照されている raw，外部由来の正式ファイル名に意味がある raw，複数ファイルで 1 資料を構成する raw は，無理にリネームせず，例外ルールや raw unit manifest で管理する選択肢も検討する．

## 記録を残す場合

ユーザが記録を希望した場合だけ，`wiki/queries/YYYY-MM-DD_LLM_Wiki_Health_Check.md` のような query として保存する．保存時は，その時点の判断と未対応事項を明記する．
