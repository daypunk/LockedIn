<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

# LockedIn

**English** | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh.md)

[![version](https://img.shields.io/badge/version-1.2.0-orange.svg)](https://github.com/daypunk/LockedIn/releases)
[![license](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![stars](https://img.shields.io/github/stars/daypunk/LockedIn?color=orange&style=flat)](https://github.com/daypunk/LockedIn/stargazers)

> ***Before Linked In, get Locked In.***

Drop a resume into Claude Code or answer a handful of questions to structure your experience once. After that, you just ask. English résumés, Korean cover letters, interview answers, and new project ideas all come out of calibrated skills.

## Install

Inside Claude Code, run three commands.

```
/plugin marketplace add daypunk/LockedIn
/plugin install lockedin@lockedin
/lockedin:setup
```

The third command runs a one-time wizard. It wires the heads-up display, picks your default interview language, and chooses where to save your experience.

## How you use it

LockedIn activates when you talk to Claude Code about your experience. There are no commands to memorize.

When you want to capture experience:

- "start organizing my experience"
- "log today's meeting with the design team"
- "absorb my resume.pdf"
- "add what I learned this week from a paper"

When you want to produce something from what is already captured:

- "make me an English resume"
- "I'm applying to company X for role Y, write the answer to question Z"
- "summarize last quarter's decisions"

LockedIn asks one question at a time when it needs more from you, and it stops when it has enough.

<p align="center">
  <img src="docs/assets/architecture.png" alt="LockedIn architecture" width="100%" />
</p>

## Why it exists

Most career tools regenerate every artifact from scratch. The artifact is the point, the source evaporates. LockedIn treats the source as the point. Your structured experience accumulates at `~/Documents/LockedIn/` as plain markdown files that you own and can carry to other tools. Resumes, cover letters, and meeting notes are artifacts of that memory, not the memory itself.

## Features

- **Natural-language activation.** Talk to Claude Code the way you already do.
- **One vault, four artifacts.** Resumes, cover letters, interview answers, and project ideas all come from the same source.
- **Quality guard built in.** Drafting and scoring run as two separate Claude turns and every artifact ships with a JSON rubric score.
- **Pre-flight audit.** Drop any resume and get the same calibrated score before you commit to a vault — no install, no signup.
- **Subscription, not API keys.** Everything runs on your existing Claude Code subscription.

## How it works

Your experiences are stored as plain markdown files with frontmatter. Every entity becomes one file. There are fifteen entity types covering people, companies, roles, projects, achievements, skills, education, certificates, publications, volunteer work, languages, documents, meetings, decisions, and topics. Relationships between entities are stored as links inside frontmatter, and the schema enforces which type can connect to which.

When you ask for a render, LockedIn queries the vault, drafts the output in one Claude turn, and then reviews the draft against a calibrated rubric in a separate Claude turn. The split prevents self-evaluation bias. When the same Claude call both writes and scores, it tends to be lenient with itself by about one point. The reviewer turn runs separately and reloads the rubric from scratch, which removes the inflation.

A master file `EXPERIENCE.md` is automatically maintained at the vault root (`~/Documents/LockedIn/`). Your entries live in per-type subfolders (person, company, role, project, and so on); instead of opening each folder, you can open this one file to scan the whole vault at a glance. If you edited markdown by hand and the master view feels stale, `lockedin refresh` rebuilds it.

LockedIn runs on your existing Claude Code subscription. It does not require an Anthropic API key, and it does not phone home.

## Skills

| Skill | Role |
|---|---|
| `lockedin` | Main skill. Routes natural language requests, runs the Q&A interview that seeds your vault, coordinates ingest and render flows. |
| `lockedin-render-jaso` | Korean cover letter renderer with a five-dimension rubric (<!-- ko-example -->두괄식, 구조화, 구체성, 표현, 적합성<!-- /ko-example -->). Cross-source confirmed banned phrase list. Two-turn writer and reviewer with a hard guard for fresh rubric loading. |
| `lockedin-render-resume-en` | English resume renderer. Five dimensions: metric density, action verb quality, structural adherence, banned phrase cleanliness, persona fit. Built-in personas are us-tech-senior, us-tech-mid, and pm-product, and targeting other roles also works. The five dimensions apply regardless of target. The persona fit dimension is calibrated against the built-in three, so scores may be conservative for outside-set roles. |
| `lockedin-render-interview` | Interview answer renderer. STAR or PAR shape with one experience per paragraph and explicit transitions between paragraphs. Five dimensions: clarity, evidence density, persona fit, conciseness, tone. |
| `lockedin-render-ideas` | Surfaces 3 to 5 next-project or career-move ideas grounded in your vault. Each idea is one paragraph: pitch sentence plus rationale that cites real entities. Five dimensions: feasibility, novelty, evidence ground, scope match, motivation alignment. |
| `lockedin-audit` | Calibrated pre-flight scorer. Takes any resume document, returns a 5-dimension rubric score plus banned-phrase and weak-verb hits. Optional refinement pass quantifies the score lift. Reuses `render-resume-en` and `render-jaso` rubrics — same calibration, no duplication. |

## Documentation

| File | Purpose |
|---|---|
| [`docs/architecture.md`](./docs/architecture.md) | How the pieces fit together |
| [`docs/ontology-spec.md`](./docs/ontology-spec.md) | The frontmatter contract |
| [`docs/ontology-mapping.md`](./docs/ontology-mapping.md) | Cross-walk to JSON Resume, Schema.org, FOAF |
| [`docs/orchestration.md`](./docs/orchestration.md) | Render and ingest pipelines |
| [`docs/cli.md`](./docs/cli.md) | Optional power-user CLI |
| [`docs/hud.md`](./docs/hud.md) | Status line integration |

## License

MIT. See [LICENSE](./LICENSE).
