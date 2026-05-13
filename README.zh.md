# LockedIn

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | **简体中文**

<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

LockedIn 就在你的 Claude Code 会话里。当你写代码或写文档时,把有意义的工作存为结构化的经历。之后需要简历、韩文求职信、面试回答、项目想法时,LockedIn 会从这份结构化的经历里写出来。

[![Claude Code](https://img.shields.io/badge/Claude%20Code-orange.svg?logo=anthropic&logoColor=white)](https://www.anthropic.com/claude-code)
[![version](https://img.shields.io/badge/version-1.2.1-orange.svg)](https://github.com/daypunk/LockedIn/releases)
[![license](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![stars](https://img.shields.io/github/stars/daypunk/LockedIn?color=orange&style=flat)](https://github.com/daypunk/LockedIn/stargazers)

## 安装

在 Claude Code 内依次执行三条命令。

```
/plugin marketplace add daypunk/LockedIn
/plugin install lockedin@lockedin
/lockedin:setup
```

第三条命令会启动一次性向导:连接状态栏 HUD、选择默认的访谈语言、选择经历保存位置。

## 使用方式

没有要背的命令,也不用另外开标签页。在 Claude Code 里自然地开始就好。

想从零开始整理经历时:

- "帮我开始整理我的经历"
- "对我做一次工作经历的访谈"
- "吸收我的 resume.pdf"

工作进行中,想把刚发生的事捕获下来时:

- "把这个 commit 作为项目亮点保存"
- "刚开完会,把它记下来"
- "我刚学到这个,记一下"

需要产出的时候:

- "给我做一份英文简历"
- "我要投 X 公司的 Y 岗位,帮我写第 Z 题的答案"
- "审一下这份简历"

LockedIn 需要更多信息时会一次只问一个问题,够用了就停下。

<p align="center">
  <img src="docs/assets/architecture.png" alt="LockedIn 架构" width="100%" />
</p>

## 为什么要做这个

大多数整理经历的工具希望你停下手上的工作,登录到另一个地方,把所有重要的事情都回忆起来。那时候,一半已经从脑海里丢了。

其他工具在你的工作之外。LockedIn 在工作之内。合并一行代码的那一刻、定下会议结论的那一刻、做出一个新的设计决定的那一刻,都会被保存为结构化的经历。流程不会被打断。

一旦保存,你的经历就会和产出物连接起来。半年后需要简历的时候,这半年的真实经历就在那里。它们以 Markdown 的形式累积在你的文件系统里,而不是别人的数据库里,任何工具都能带走,任何产出物都能复用。

## 特性

- **没有要背的命令。** 像平时那样说,LockedIn 会选对技能。
- **工作中即时捕获。** Claude Code 会话里的一个瞬间,无需切换上下文,直接存为结构化经历。
- **给产出打分。** 和写作者不同的另一个 Claude,用基于领域研究的 rubric 进行评分。
- **不需要 API key。** 跑在你现有的 Claude Code 订阅上。

## 工作原理

**1. 经历会被结构化。** 把已有的简历丢进来,回答几个简短的访谈问题,或者把工作中的某个瞬间捕获下来。LockedIn 就会把它整理成 `~/Documents/LockedIn/` 中 15 种类型化的 Markdown 文件。

**2. 每一条主张都绑定到真实实体。** 写作 turn 把公司、项目、指标都以 `[[type/slug]]` 引用的形式直接绑到 vault 文件。展示给你之前会把 slug 替换成自然语言,但如果某条主张找不到对应实体,slug 就原样保留,LockedIn 会问"这里没有对应的实体,要不要加一个?",而不是自己编造。新事实没有进入的缝隙。

**3. 两个 Claude 分头打分。** 写作 turn 结束后,一个独立的 reviewer turn 会重新从磁盘读取 `RUBRIC.md` 进行打分。每种产出有各自的 5 维(英文简历:指标密度、动词质量、结构、banned 表达、persona 适配)。结果是一份 JSON,和 markdown 一起返回,包含每个维度 0~5 分、总分、引用实体匹配率、banned 表达命中清单。如果某个维度低于 4,LockedIn 会自动再优化一次再展示。

**4. 经历和对话始终同步。** 手动改了 markdown,或者对话里说的和现有经历对不上,LockedIn 会先察觉,一次只问一个问题来对齐。之所以能做到,是因为你的经历不是自由文本,而是按类型化实体结构化存储的。AI 只比较变化的字段,不必从头重读。所以同步成本只随变化量增长,而不随经历的总规模增长。经历越丰富,差异越明显。

## Skills

| 功能 | 技能 | 角色 |
|---|---|---|
| 和 LockedIn 对话 | `/lockedin` | 自然语言入口。听你的请求,决定路由到哪个子技能,经历为空时启动 Q&A 访谈,对话与现有经历出现分歧时主动一题一题询问对齐。 |
| 捕获工作瞬间 | `/lockedin-capture` | 把"存这个"、"记一下这个"、"跟踪这个"等捕获意图转换为结构化条目。writer/reviewer 模式,5 维评分(schema 准守、edge 完整度、字段具体性、语义准确度、重复检测)。发现相似候选时会浮现给你,由你决定合并还是保留;不会静默合并,也不会静默创建重复。 |
| 撰写英文简历 | `/lockedin-render-resume-en` | 从经历调取内容,按 persona 撰写英文简历。内置 10 种 persona(senior IC、mid 级、PM、后端、前端、移动端、数据工程、ML 工程、设计、市场),其他岗位也能用。从指标密度、动词质量、结构、banned 表达、persona 适配 5 维评分,内置之外的岗位只在 persona 维度上略保守。 |
| 撰写韩文求职信 | `/lockedin-render-jaso` | 给定公司和题目,会引用你的经历写出答案。按韩文 5 维(结论先行、结构化、具体性、表达、适配)评分,并避开跨源验证过的禁用表达。 |
| 起草面试回答 | `/lockedin-render-interview` | 给定公司、岗位和问题,以 STAR 或 PAR 结构作答。每段只放一个经验,段落间放显式过渡句让面试官更容易跟上。从清晰度、证据、persona 适配、简洁度、语气 5 维评分。 |
| 提出下一步想法 | `/lockedin-render-ideas` | 读你的经历,提出 3 到 5 个可走方向。每个想法一段。一句 pitch,加上引用你匹配经历作为依据。从可行性、新颖度、证据基础、范围匹配、动机对齐 5 维评分。 |
| 任意简历预审 | `/lockedin-audit` | 把简历 PDF 或 DOCX 丢进来,就能拿到 5 维评分。 |

## 文档

| 文件 | 内容 |
|---|---|
| [`docs/architecture.md`](./docs/architecture.md) | 各组件如何组合 |
| [`docs/ontology-spec.md`](./docs/ontology-spec.md) | Frontmatter 契约 |
| [`docs/ontology-mapping.md`](./docs/ontology-mapping.md) | 与 JSON Resume、Schema.org、FOAF 的映射 |
| [`docs/orchestration.md`](./docs/orchestration.md) | 渲染与 ingest 管线 |
| [`docs/cli.md`](./docs/cli.md) | 可选的高阶 CLI |
| [`docs/hud.md`](./docs/hud.md) | 状态栏集成 |

## 许可证

MIT。详见 [LICENSE](./LICENSE)。
