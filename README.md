# LLM Wiki Template

raw → wiki の2層構造で知識を蒸留・管理するためのテンプレート．

## Structure

| Layer | Path | Role |
| --- | --- | --- |
| Raw | `raw/` | 一次情報（immutable，情報ソース種別で整理） |
| Wiki | `wiki/` | 精製済み知識と実践知（LLM が蒸留・管理） |

### Knowledge Pipeline

```text
raw/*  →  wiki/sources/  →  wiki/articles/  →  wiki/synthesis/
(一次情報)   (抽出)         (概念記事)          (統合ページ)
```

実装・運用・調査で得た知見は，`wiki/incidents/`，`wiki/recipes/`，`wiki/decisions/` に分けて残す．

Wiki 層はすべて LLM が生成・更新・維持する．人間は raw の投入と質問・方向づけを担当する．

新しい wiki を作るときは，[AGENTS.md](AGENTS.md) の Overview と Domains を対象領域に合わせて更新する．
