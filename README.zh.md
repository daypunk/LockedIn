<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

# LockedIn

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | **简体中文**

[![version](https://img.shields.io/badge/version-1.2.0-orange.svg)](https://github.com/daypunk/LockedIn/releases)
[![license](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![stars](https://img.shields.io/github/stars/daypunk/LockedIn?color=orange&style=flat)](https://github.com/daypunk/LockedIn/stargazers)

> ***Before Linked In, get Locked In.***

把简历丢进 Claude Code,或者简单回答几个问题,就把你的经历整理好。之后,你只需要提问。英文简历、中文求职信、面试回答、新项目想法都会从同一份经历里自动产出。

## 安装

在 Claude Code 内依次执行三条命令。

```
/plugin marketplace add daypunk/LockedIn
/plugin install lockedin@lockedin
/lockedin:setup
```

第三条命令会启动一次性向导:连接状态栏 HUD、选择默认的访谈语言、选择经历保存位置。

## 使用方式

只要在 Claude Code 里用自然语言聊起你的经历,LockedIn 就会自动激活。没有需要记忆的命令。

记录经历时可以这样说:

- "帮我开始整理我的经历"
- "把今天和设计团队的会议记下来"
- "吃掉我的 resume.pdf"
- "把这周读的论文里学到的加进来"

从已有经历里产出材料时可以这样说:

- "给我做一份英文简历"
- "我要投 X 公司的 Y 岗位,帮我写第 Z 题的答案"
- "总结一下上个季度的关键决策"

LockedIn 需要更多信息时会一次只问一个问题,够用了就停下。

<p align="center">
  <img src="docs/assets/architecture.png" alt="LockedIn 架构" width="100%" />
</p>

## 为什么要做这个

大多数求职工具每次都从零生成产出,产出本身是目的,原始素材随之蒸发。LockedIn 反过来,把原始素材当成目的本身。结构化后的经历会作为普通 Markdown 文件累积在 `~/Documents/LockedIn/`,完全归你所有,可以随时带去其他工具。简历、求职信、会议记录只是这份记忆的派生产物,而不是记忆本身。

## 特性

- **自然语言激活。** 像平时那样跟 Claude Code 对话即可,没有要背的命令。
- **一个 vault,四种产出。** 简历、求职信、面试回答、项目想法都来自同一份素材。
- **内置质量校验。** 起草和打分跑在两个独立的 Claude turn 里,每个产出都附带 JSON 评分。
- **预审 audit。** 不必先建 vault — 任意一份简历丢进来,就能拿到同一套 calibrated 评分。无需安装、无需注册。
- **订阅即可,不需要 API key。** 全部跑在你现有的 Claude Code 订阅上。

## 工作原理

经历以带 frontmatter 的 Markdown 文件存储,每个实体一个文件。实体类型共 15 种:person、company、role、project、achievement、skill、education、certificate、publication、volunteer、language、document、meeting、decision、topic。实体之间的关系作为 link 写在 frontmatter 里,schema 会校验哪些类型可以连到哪些类型。

收到渲染请求时,LockedIn 会先查询 vault,然后在一个 Claude turn 里起草内容,再在**另一个独立的** Claude turn 里按 calibrated 评分表打分。两个 turn 分开是为了避免自我评估偏差——同一个 Claude 调用既写又打分时,往往会高估自己大约 1 分。评审 turn 会重新从头加载评分表,从而消除这一偏差。

vault 根目录(`~/Documents/LockedIn/`)会自动维护一份名为 `EXPERIENCE.md` 的主索引文件。各类型分别放在 person、company、role、project 等子目录下;不必逐一打开,只看这一个文件即可一次性扫完整个 vault。如果你手动改了 Markdown 且觉得主文件不同步,运行 `lockedin refresh` 即可重建。

LockedIn 跑在你现有的 Claude Code 订阅上,不需要 Anthropic API key,也不会上传任何数据。

## Skills

| Skill | 角色 |
|---|---|
| `lockedin` | 主 skill。路由自然语言请求,主持种子 Q&A 访谈,协调 ingest 与 render 流程。 |
| `lockedin-render-jaso` | 韩文求职信(자기소개서)渲染器。五维评分:두괄식、구조화、구체성、표현、적합성。内置跨源验证的禁用表达清单。写作 turn 与评审 turn 严格分离,评审 turn 会重新加载评分表。 |
| `lockedin-render-resume-en` | 英文简历渲染器。五维评分:metric density、action verb quality、structural adherence、banned phrase cleanliness、persona fit。内置 us-tech-senior、us-tech-mid、pm-product 三种 persona,对其他岗位也可使用。前四维与岗位无关,persona fit 这一维是按内置三种 persona calibrate 的,因此对内置之外的岗位评分可能偏保守。 |
| `lockedin-render-interview` | 面试回答渲染器。采用 STAR 或 PAR 结构,一个段落对应一个经历,段落之间有显式过渡句。五维评分:clarity、evidence density、persona fit、conciseness、tone。 |
| `lockedin-render-ideas` | 基于 vault 给出 3–5 个下一步项目或职业转向的想法。每个想法一段:一句 pitch + 引用真实 vault 实体的依据。五维评分:feasibility、novelty、evidence ground、scope match、motivation alignment。 |
| `lockedin-audit` | 经过校准的预审评分器。接收任意简历文档,返回 5 维 rubric 评分以及 banned phrase / 弱动词命中列表。可选的 refinement 流程会量化分数提升幅度。复用 `render-resume-en` 和 `render-jaso` 的 rubric,无校准重复。 |

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
