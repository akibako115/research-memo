# LLM Wiki

## Overview

Hypernetwork，画像 + テーブルデータのマルチモーダル学習，医療画像 Fairness に関する研究知識を，一次情報から再利用可能な概念知へ蒸留するための個人ナレッジベース．
Karpathy の LLM Wiki パターンに基づき，raw → wiki の2層構造で知識を蒸留・管理する．
一次情報から得た概念知に加えて，実装・運用・調査で得た実践知も wiki 層に蓄積する．

この wiki の詳しい目的，追っている問い，スコープは [purpose.md](purpose.md) を参照する．

## Directory Structure

```text
raw/                    # 一次情報（immutable）
├── papers/             # 論文 PDF・要約
├── articles/           # Web 記事・ブログ
├── notes/              # 手書きメモ・会議メモ・業務調査
├── datasets/           # データセット・スキーマ定義
└── misc/               # 画像・スライド・その他

wiki/                   # 精製済み知識（LLM が生成・更新・維持）
├── sources/            # raw 1 件 → 要約 1 件
├── articles/           # 概念記事（1 概念 1 ファイル）
├── synthesis/          # 複数概念を横断した統合ページ
├── queries/            # LLM との QA・調査・計画検討の記録
├── recipes/            # 次回も使える実装・運用手順
├── incidents/          # 詰まったこと，エラー，調査ログ
└── decisions/          # 設計・設定・運用方針の判断理由
```

## Rules

### Raw Layer

- **Immutable**: 一度追加したファイルは編集しない．LLM は読み取り専用でアクセスする．
- **原文を保存する**: raw には必ず一次情報の原文を保存する．Web 記事は Web Clipper 等で保存し，論文は元論文の PDF を保存する．AI が要約・再構成したものは raw に置かない．
- **情報ソース種別** でフォルダを分ける．トピック別ではない．raw は管理コストを最小限に抑えるためにも細かくフォルダを分け過ぎない．
- 保存時はファイル名に日付プレフィックスを付ける: `YYYY-MM-DD_{title}.md`
- raw の投入は人間の仕事，コンパイルは LLM の仕事．

| 役割 | 担当 |
| --- | --- |
| article / source の不足情報を特定する | LLM |
| 必要な公式ドキュメント等の URL を提示する | LLM |
| Web Clipper 等で原文を `raw/` に保存する | 人間 |
| raw → source → article のコンパイル・更新 | LLM |
| wiki に対して質問する | 人間 |
| 読んで方向づけ・軌道修正の指示を出す | 人間 |

```text
【raw 追加の流れ】
1. LLM が既存の article / source から不足情報を特定
2. LLM が取得すべきドキュメントの URL を提示
3. 人間が Web Clipper 等で raw/ に保存
4. LLM が source → article をコンパイル・更新
```

### Wiki Layer

Wiki 層はすべて LLM が生成・更新・維持する．人間は wiki を読み，質問や指示で方向づけする．

```text
raw/*  →  sources/  →  articles/  →  synthesis/
(一次情報)  (抽出)     (概念記事)     (横断統合)

実装・運用経験 → incidents/ → recipes/
              → decisions/
```

| Stage | フォルダ | 粒度 | 入力 | やること |
| --- | --- | --- | --- | --- |
| 1 | **sources/** | raw 1 件 → source 1 件 | raw の生ドキュメント | 「この記事に何が書いてあるか」を要約・抽出（ソースに忠実）．[執筆ガイドライン](wiki/sources/AGENTS.md) |
| 2 | **articles/** | 概念 1 つ → article 1 件 | 複数の sources | 「この概念とは何か」を複数ソースから構築．[執筆ガイドライン](wiki/articles/AGENTS.md) |
| 3 | **synthesis/** | テーマ 1 つ → synthesis 1 件 | 複数の articles | 複数概念を横断した統合ページ |
| - | **queries/** | Q&A / 調査 1 件 → query 1 件 | wiki 全体 | LLM との QA，調査，計画検討の履歴 |
| - | **recipes/** | 手順 1 件 → recipe 1 件 | 実装経験，incidents，decisions | 次回も使える実装・運用手順 |
| - | **incidents/** | 詰まり 1 件 → incident 1 件 | 実装中のエラー，失敗，調査 | 原因，再現条件，解決方法，再発防止 |
| - | **decisions/** | 判断 1 件 → decision 1 件 | 設計・設定・運用上の選択 | なぜその方針を採用したか |

- **まず articles に「使える記事」を揃えることを優先する．**
- すべての source が揃うのを待たず，今ある source から article を作成してよい．
- article に不足がある場合は，追加の raw を取得 → source を作成 → article を更新する．
- wiki 層の生成・更新・相互参照の維持はすべて LLM が行う．
- query は思考過程の記録であり，長く使える知識は articles / synthesis / recipes / decisions へ蒸留する．
- project roadmap や一時的な作業計画は synthesis に置かず，必要に応じて queries か実践知レイヤーへ分解する．

### Schema / Purpose

- `AGENTS.md` は，LLM が常に従う core schema として扱う．ディレクトリ構造，raw immutable，命名規則，wikilink，層の役割など，全作業に共通する規約を置く．
- 各フォルダの `README.md` は，その層の短い役割説明として扱う．
- 詳細な操作手順は必要になった時点で分離する．例: ingest，query，lint のように「いつ使わないか」が明確なものだけを独立させる．
- この wiki の目的・追っている問い・スコープは，`purpose.md` に分離して管理する．`AGENTS.md` には全作業に共通する core schema を置く．

### Wiki Article Conventions

- ファイル名: `Concept_Name.md`（英語，アンダースコア区切り）
- 概念間のリンク: `[[Concept_Name]]`（Obsidian wikilink）
- 内容は日本語で記述
- フロントマターに `created`，`updated`，`sources` を記載:

```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[sources/source_file]]"
---
```

## Domains

この wiki がカバーする主要ドメイン．詳細なスコープは [purpose.md](purpose.md) を参照する．

- Hypernetwork
- 画像 + テーブルデータのマルチモーダル学習
- 条件付きモデル・modulation・adapter
- 医療画像 Fairness
- Fairness 評価指標・データセット
- 条件付きモデルの解析
- 研究方向・アイデア探索
