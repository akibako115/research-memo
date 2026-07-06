
このリポジトリは，Hypernetwork，画像 + テーブルデータのマルチモーダル学習，医療画像 Fairness に関する研究メモを，一次情報から再利用可能な概念知へ蒸留するための個人ナレッジベースである．

単なるメモ置き場ではなく，論文整理と複数論文を横断した知識抽出を行い，患者属性条件付きモデルが医療画像分類の subgroup reliability / fairness に与える影響を調べるための外部記憶として運用する．

## 目的

- Hypernetwork，画像 + テーブルデータのマルチモーダル学習，医療画像 Fairness，関連する機械学習・評価手法の論文を raw に保存し，出典を失わずに蓄積する．
- raw の内容を sources に要約し，複数論文から articles と synthesis を育てる．
- 個別論文の理解で終わらせず，手法・問題設定・評価軸・限界・未解決課題を横断的に整理する．
- 研究の方向性，仮説，実験アイデアを考えるための材料を，後から検索・接続・再利用できる形に変換する．

## 追っている問い

- 医療画像分類において，患者属性を明示的に使う条件付きモデルは subgroup fairness / reliability を改善するのか．
- 改善する場合，それはどの融合方式，どの層，どの属性，どの複雑度に由来するのか．
- Hypernetwork，FiLM，adapter，late fusion などの条件付きモデルは，医療画像 Fairness のどの問題設定に使えるのか．
- 医療画像 Fairness では，どの属性・データセット・タスク・評価指標が使われているのか．
- 既存研究は，公平性と精度，汎化性能，分布シフト，少数群性能の関係をどう扱っているのか．
- 条件付きモデルは属性情報をどのように使っているのか．性能改善は疾患特徴の補強なのか，shortcut / leakage / group-specific specialization なのか．
- 複数論文を横断すると，どの研究方向が有望で，どこに未解決課題が残っているのか．
- 次に読むべき論文，整理すべき概念，検証すべき研究アイデアは何か．

## スコープ

主な対象は，患者属性条件付きモデルと医療画像 Fairness を接続する研究知識である．

サーベイの主軸:

- Fairness in medical imaging: subgroup reliability，bias，protected attribute，評価指標，データセット
- 画像 + テーブルデータ / 属性条件付きモデル: late fusion，FiLM，conditional normalization，hypernetwork，adapter，LoRA / PEFT
- 条件付きモデルの解析: 属性情報の使われ方，特徴空間・activation・attention・adapter weight の subgroup 差，shortcut / leakage の検出

対象に含めるもの:

- Hypernetwork，メタラーニング，条件付きモデル生成，パラメータ生成に関する論文・概念
- 画像 + tabular / EHR / patient metadata の multimodal integration に関する論文・概念
- FiLM，conditional normalization，adapter，LoRA，PEFT などの軽量な条件付き変調手法
- 医療画像における Fairness，bias，subgroup performance，domain shift に関する論文・概念
- Fairness 評価指標，データセット，実験設定，ベンチマーク
- 条件付きモデルやマルチモーダルモデルの解析手法
- 複数論文から導いた研究方向，未解決課題，実験アイデア

対象に含めないもの:

- 日記
- 雑なリンク集
- プロジェクト管理
- 一時的な TODO
- AI の出力だけのメモ

この wiki はトピック別の収集棚ではなく，問いと再利用可能性を中心に育てる．一時的な会話や調査の記録は queries に置き，長く使える知識だけを articles / synthesis / decisions に蒸留する．

## 運用方針

- raw は一次情報の保管場所として immutable に扱う．
- wiki は LLM が編集・整理・相互参照を維持する作業場所として扱う．
- 不足している情報がある場合，まず必要な一次情報を特定し，人間が raw に追加する．
- 完璧に揃ってから書くのではなく，今ある source から article を作り，不足が見えたら更新する．
- この wiki は自分だけの研究用であり，外部公開やチーム共有を前提にしない．
- 特定の1論文や1実装に研究全体を依存させず，手法群・評価軸・解析軸を横断して研究方針を検討する．
