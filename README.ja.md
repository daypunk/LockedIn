<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

# LockedIn

[English](README.md) | [한국어](README.ko.md) | **日本語** | [简体中文](README.zh.md)

[![version](https://img.shields.io/badge/version-1.2.0-orange.svg)](https://github.com/daypunk/LockedIn/releases)
[![license](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![stars](https://img.shields.io/github/stars/daypunk/LockedIn?color=orange&style=flat)](https://github.com/daypunk/LockedIn/stargazers)

> ***Before Linked In, get Locked In.***

履歴書を Claude Code に投げ込むか、いくつかの質問に答えるだけで、自分の経歴を一度きちんと構造化できます。そのあとは、聞くだけです。英文レジュメ、韓国語の自己紹介書(자소서)、面接の回答、次のプロジェクトのアイデアが、すべて同じ素材から生まれます。

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

- **自然言語で起動。** 覚えるコマンドなしで、いつもどおり Claude Code に話しかけるだけ。
- **一つの vault、四つの成果物。** レジュメ、カバーレター、面接回答、プロジェクトのアイデアが同じ素材から出てきます。
- **品質チェック内蔵。** 起草と採点が二つの独立した Claude turn で走り、すべての成果物に JSON のルーブリックスコアが添付されます。
- **事前監査 (pre-flight audit)。** vault を作る前でも、任意のレジュメを投げ込めばキャリブレーション済みのスコアが返ってきます。インストールも登録も不要。
- **サブスクリプションだけで動く。** Anthropic API キーは不要。既存の Claude Code サブスクリプションで完結します。

## 仕組み

経歴は frontmatter 付きの普通の Markdown ファイルとして保存されます。エンティティ一つにつき一つのファイル。エンティティの種類は 15 個: person、company、role、project、achievement、skill、education、certificate、publication、volunteer、language、document、meeting、decision、topic。エンティティ間の関係は frontmatter の link として書かれ、スキーマがどの型からどの型へ接続できるかを検証します。

レンダリングの要求が来ると、LockedIn はまず vault を照会し、一つの Claude turn で初稿を書き、さらに**別の独立した** Claude turn でキャリブレーションされたルーブリックに沿って初稿をレビューします。二つの turn を分けるのは自己評価バイアスを避けるためです。同じ Claude 呼び出しが書きながら採点すると、自分に対しておよそ 1 点ぶん甘くなる傾向があります。レビュアーの turn はルーブリックを最初から読み直すので、この甘さが消えます。

vault のルート (`~/Documents/LockedIn/`) では `EXPERIENCE.md` というマスター索引ファイルが自動的に更新されます。person・company・role・project などの型別サブフォルダがありますが、フォルダを一つずつ開かなくても、このファイルを開けば vault 全体を一度に見渡せます。手で Markdown を編集してマスターファイルが古く感じたら `lockedin refresh` で再構築できます。

LockedIn は既存の Claude Code サブスクリプションだけで動きます。Anthropic API キーは必要なく、外部にデータを送信することもありません。

## Skills

| Skill | 役割 |
|---|---|
| `lockedin` | メインスキル。自然言語のリクエストをルーティングし、vault を埋めるための Q&A インタビューを主導し、ingest と render のフローを調整します。 |
| `lockedin-render-jaso` | 韓国語自己紹介書(자기소개서)レンダラ。5 次元評価: 두괄식、구조화、구체성、표현、적합성。複数ソースで相互検証されたお決まり表現リストを内蔵。書き手 turn とレビュアー turn を厳密に分離し、レビュアー turn はルーブリックを再読込みします。 |
| `lockedin-render-resume-en` | 英文レジュメレンダラ。5 次元評価: metric density、action verb quality、structural adherence、banned phrase cleanliness、persona fit。内蔵ペルソナは us-tech-senior、us-tech-mid、pm-product の 3 種。他の職種にも使えます。前 4 次元は職種に依存しませんが、persona fit は内蔵 3 種で校正されているため、それ以外の職種では採点がやや保守的になることがあります。 |
| `lockedin-render-interview` | 面接回答レンダラ。STAR または PAR の構造で、一段落に一つの経験、段落の間には明示的な遷移文を入れます。5 次元評価: clarity、evidence density、persona fit、conciseness、tone。 |
| `lockedin-render-ideas` | vault に基づいて、次のプロジェクトやサイドプロジェクト、キャリアシフトのアイデアを 3–5 個提示します。各アイデアは一段落: 一文のピッチと、実在する vault エンティティを引用した根拠。5 次元評価: feasibility、novelty、evidence ground、scope match、motivation alignment。 |
| `lockedin-audit` | キャリブレーション済みの事前監査スコアラ。任意のレジュメ文書を受け取り、5 次元ルーブリックスコアと、お決まり表現や弱い動詞のヒットリストを返します。オプションの refinement パスでスコアの上昇幅まで定量化します。`render-resume-en` と `render-jaso` のルーブリックを再利用しているため、キャリブレーションの重複はありません。 |

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
