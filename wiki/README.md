# wiki

LLM が生成・更新・維持する知識層．

`sources/`，`articles/`，`synthesis/` は raw 由来の資料知を段階的に蒸留する．`queries/` は LLM との調査・QA の履歴を残す．`recipes/`，`incidents/`，`decisions/` は実装・運用・調査から得た実践知を残す．

```text
raw/* -> sources/ -> articles/ -> synthesis/
                      ^
queries/ -------------|

実装・運用経験 -> incidents/ -> recipes/
              -> decisions/
```

迷った場合は，長く使う概念知は `articles/`，横断理解は `synthesis/`，一回の会話や調査の記録は `queries/`，再実行できる手順は `recipes/`，詰まりと解決は `incidents/`，判断理由は `decisions/` に置く．
