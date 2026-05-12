# LockedIn

[English](README.md) | [한국어](README.ko.md) | **日本語** | [简体中文](README.zh.md)

<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

履歴書を Claude Code に投げ込むか、いくつかの質問に答えるだけで、自分の経歴を一度きちんと構造化できます。そのあとは、聞くだけです。英文レジュメ、韓国語の自己紹介書(자소서)、面接の回答、次のプロジェクトのアイデアが、すべて同じ素材から生まれます。

[![Claude Code](https://img.shields.io/badge/Claude%20Code-orange.svg?logo=anthropic&logoColor=white)](https://www.anthropic.com/claude-code)
[![version](https://img.shields.io/badge/version-1.2.0-orange.svg)](https://github.com/daypunk/LockedIn/releases)
[![license](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![stars](https://img.shields.io/github/stars/daypunk/LockedIn?color=orange&style=flat)](https://github.com/daypunk/LockedIn/stargazers)

## インストール

Claude Code の中で 3 つのコマンドを順に実行します。

```
/plugin marketplace add daypunk/LockedIn
/plugin install lockedin@lockedin
/lockedin:setup
```

3 番目のコマンドは一度きりのウィザードです。ステータスラインの HUD を接続し、デフォルトのインタビュー言語を選び、経歴の保存先を決めます。

## 使い方

LockedIn は Claude Code 上で自分の経歴について自然な言葉で話しかけたときに自動的に起動します。覚えるべきコマンドはありません。

経歴を記録したいときの言い回し:

- "経歴の整理を始めて"
- "今日のデザインチームのミーティングをまとめて"
- "履歴書 PDF を取り込んで"
- "今週の論文から学んだことを追加して"

蓄積した経歴から成果物を作りたいときの言い回し:

- "英文レジュメを作って"
- "X 社の Y 職に応募するから、Z の項目の答えを書いて"
- "先四半期の主要な意思決定をまとめて"

LockedIn は追加情報が必要なときは一度に一つだけ質問し、十分になったら止まります。

<p align="center">
  <img src="docs/assets/architecture.png" alt="LockedIn アーキテクチャ" width="100%" />
</p>

## なぜ作ったか

多くのキャリアツールは成果物をその都度ゼロから生成します。成果物が目的で、素材は蒸発します。LockedIn はその順序をひっくり返します。構造化された経歴はローカルの `~/Documents/LockedIn/` にプレーンな Markdown ファイルとして蓄積され、完全にあなたの所有物として他のツールに持ち出せます。レジュメ、カバーレター、ミーティングノートは、その記憶からの派生物であって、記憶そのものではありません。

## 特徴

- **覚えるコマンドはありません。** 話すように頼めば LockedIn が適切なスキルを選びます。
- **経歴を一緒に育てていきます。** レジュメ、カバーレター、面接回答、プロジェクトのアイデアが同じ経歴から生まれます。
- **成果物を採点します。** 書いた Claude とは別の Claude が、ドメインリサーチに基づいたルーブリックで採点します。
- **API キー不要。** 既存の Claude Code サブスクリプションで動きます。

## 仕組み

**1. 経歴が構造化されます。** 既存のレジュメを投げるか、いくつかの短い質問に答えれば、LockedIn が `~/Documents/LockedIn/` の中に 15 種類の型付き Markdown ファイルとして整理します。

**2. すべての主張が実在のエンティティに紐づきます。** 起草 turn は会社名、プロジェクト、指標を `[[type/slug]]` 形式の参照として vault ファイルに直接引用して書きます。あなたに見せる直前にスラッグは自然言語に置き換えられますが、対応するエンティティがなければスラッグはそのまま残り、LockedIn が「ここに対応するエンティティがありません、追加しますか?」と尋ねます。新しい事実が紛れ込む余地が最初からありません。

**3. 二つの Claude が採点します。** 起草 turn が終わると、別の reviewer turn が `RUBRIC.md` をディスクから読み直して採点します。成果物ごとに 5 次元が異なります (英文レジュメは指標密度、動詞品質、構造、お決まり表現、ペルソナ適合性)。結果は次元別 0~5 点、合計、引用エンティティ照合率、お決まり表現ヒット一覧を含む JSON が Markdown と一緒に返ります。4 点未満の次元があれば自動で一度だけ調整して見せます。

**4. 経歴と会話が常に同期します。** Markdown ファイルを手で編集したり、会話で言ったことが既存の経歴と食い違ったりすると、LockedIn が先に気づいて一度に一つだけ質問してすり合わせます。これが可能なのは、経歴が自由テキストではなく型付きエンティティとして構造化されているからです。AI は全体を読み直さず、変更されたフィールドだけを比較します。そのため同期コストは経歴全体のサイズではなく、変更された量にのみ比例します。経歴が豊富になるほど、この差は大きくなります。

## Skills

| 機能 | スキル | 役割 |
|---|---|---|
| LockedIn に話しかける | `/lockedin` | 自然言語のエントリーポイントです。あなたが言ったことを聞き、どのサブスキルに渡すかを決め、経歴が空なら Q&A インタビューを始め、会話と既存の経歴が食い違ったら気づいて一つずつ質問してすり合わせます。 |
| 英文レジュメを書く | `/lockedin-render-resume-en` | 経歴から引いてペルソナに合わせた英文レジュメを書きます。内蔵ペルソナは 10 種 (シニア IC、ミッドレベル、PM、バックエンド、フロントエンド、モバイル、データエンジニア、ML エンジニア、デザイナー、マーケター) で、他の職種でも動きます。指標密度、動詞品質、構造、お決まり表現、ペルソナ適合性の 5 次元で採点し、内蔵外の職種ではペルソナ次元のみ控えめに評価されます。 |
| 韓国語自己紹介書を書く | `/lockedin-render-jaso` | 会社名と質問を渡すと、あなたの経歴を引用して答えを書きます。韓国語 5 次元 (<!-- ko-example -->두괄식、구조화、구체성、표현、적합성<!-- /ko-example -->) で採点し、複数ソースで相互検証されたお決まり表現を避けます。 |
| 面接回答を起草する | `/lockedin-render-interview` | 会社、職種、質問を渡すと STAR または PAR の構造で答えます。一段落一経験、段落間には明示的な遷移文を入れて面接官が追いやすくします。明瞭性、根拠、ペルソナ適合性、簡潔性、トーンの 5 次元で採点します。 |
| 次のアイデアを提示する | `/lockedin-render-ideas` | あなたの経歴を読んで次に取りうる方向を 3 から 5 個提案します。各アイデアは一段落のピッチと、なぜそれがあなたに合うかを示す経歴の引用です。実現可能性、新規性、根拠、スコープ整合、動機整合の 5 次元で採点します。 |
| 任意のレジュメを監査する | `/lockedin-audit` | レジュメ PDF や DOCX を投げれば 5 次元スコアが返ります。 |

## ドキュメント

| ファイル | 内容 |
|---|---|
| [`docs/architecture.md`](./docs/architecture.md) | 各構成要素がどう噛み合うか |
| [`docs/ontology-spec.md`](./docs/ontology-spec.md) | Frontmatter の契約 |
| [`docs/ontology-mapping.md`](./docs/ontology-mapping.md) | JSON Resume、Schema.org、FOAF とのマッピング |
| [`docs/orchestration.md`](./docs/orchestration.md) | レンダリングと ingest のパイプライン |
| [`docs/cli.md`](./docs/cli.md) | オプションのパワーユーザー向け CLI |
| [`docs/hud.md`](./docs/hud.md) | ステータスライン連携 |

## ライセンス

MIT。[LICENSE](./LICENSE) を参照。
