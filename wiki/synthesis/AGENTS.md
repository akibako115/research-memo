# Synthesis — 執筆ガイドライン

synthesis を書く際の粒度・構成・articles との区別の指針．

## synthesis の役割

- **複数の articles を横断して，長く使える統合的な理解を置く．**
- 個々の article では書けない「比較・使い分け・全体像・相互関係」を説明する．
- articles が「1 概念とは何か」を説明するのに対し，synthesis は「複数概念がどう関係し，全体としてどう機能するか」を説明する．

## articles との区別

| 観点 | article | synthesis |
|---|---|---|
| 粒度 | 1 概念 1 ファイル | テーマ 1 つ，複数 article を横断 |
| 入力 | sources | articles |
| 問い | 「この概念とは何か」 | 「これらの概念はどう関係し，どう使い分けるか」 |
| frontmatter | `sources:` | `articles:` |
| 例 | FiLM，DAFT，Hidden_Stratification | Image_Tabular_Fusion，Medical_Image_Fairness_Audit_Loop |

### synthesis にすべきサイン

- 関連 article が 3 件以上あり，比較表・選択基準・全体像が必要になっている
- 複数 article に同じ比較や使い分けの記述が重複している
- 「A と B と C の違いは？」「どれを使うべき？」という問いに article 単独では答えられない

### synthesis にしてはいけないもの

- タスク一覧，短期計画，ロードマップ → queries/ か外部管理
- 1 つの概念の詳細説明 → articles/
- 手順書 → recipes/
- 判断理由 → decisions/

## 記事の構成パターン

### 1. フロントマター

```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
articles:
  - "[[Article_Name_1]]"
  - "[[Article_Name_2]]"
  - "[[Article_Name_3]]"
---
```

`articles:` には，この synthesis が横断する主要な article を列挙する．

### 2. 導入（冒頭1-2段落）

- このテーマで複数概念を横断して見る必要がある理由から入る．
- 「個々の概念は articles にあるが，全体としてどういう構造・選択肢があるか」を示す．

### 3. 全体像

- 比較表，フロー図，または層構造で全体を一望できるようにする．
- 各 article の位置づけと相互関係を明確にする．

### 4. 比較・使い分け・統合

- 概念間の違い，トレードオフ，適用条件を整理する．
- 「どの状況でどの概念を選ぶか」の指針を示す．

### 5. 未解決課題・今後の方向

- 横断して見えてくる gap や未解決の問いを整理する．

### 6. 関連概念（末尾）

- 統合した articles への wikilink
- 関連するが統合していない concepts への wikilink

## 文体・表記

- 日本語で記述．句読点はコンマ(，)とピリオド(．)を使用．
- 関連概念は `[[Concept_Name]]` で参照（Obsidian wikilink）．
- 見出しは内容に即した具体的な名前にする．

## やること・やらないこと

| やること | やらないこと |
|---|---|
| 複数 article を横断して構造化する | 1 つの概念を詳しく説明する（article の仕事） |
| 比較表・フロー図で全体像を示す | article の内容をそのまま繰り返す |
| 選択基準やトレードオフを整理する | 短期計画やタスク一覧を置く |
| 未解決の横断的な問いを示す | raw の詳細を直接引用する（source の仕事） |
| `articles:` frontmatter で入力を明示する | `sources:` を frontmatter に使う |
