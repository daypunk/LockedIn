# LockedIn

**English** | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh.md)

<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

> ***Before Linked In, get Locked In.***

Drop a resume into Claude Code or answer a handful of questions to structure your experience once. After that, you just ask. English résumés, Korean cover letters, interview answers, and new project ideas all come out of calibrated skills.

[![Claude Code](https://img.shields.io/badge/Claude%20Code-orange.svg?logo=anthropic&logoColor=white)](https://www.anthropic.com/claude-code)
[![version](https://img.shields.io/badge/version-1.2.0-orange.svg)](https://github.com/daypunk/LockedIn/releases)
[![license](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![stars](https://img.shields.io/github/stars/daypunk/LockedIn?color=orange&style=flat)](https://github.com/daypunk/LockedIn/stargazers)

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

- **No commands to memorize.** Type the way you'd talk and LockedIn picks the right skill.
- **Builds your experience with you, over time.** Resumes, cover letters, interview answers, and project ideas all come from the same experience.
- **Scores your output.** A different Claude than the writer reviews it against a domain-researched rubric.
- **No API key needed.** Runs on your existing Claude Code subscription.

## How it works

**1. Your experience gets structured.** Drop a resume or answer a few short interview questions. LockedIn organizes it into 15 typed markdown files in `~/Documents/LockedIn/`.

**2. Every claim is bound to a real entity.** The writer turn cites companies, projects, and metrics as `[[type/slug]]` references pointing at specific vault files. Slugs are swapped for natural language right before you see the output. If no matching entity backs a claim, the slug stays in place and LockedIn asks you whether to add the entity rather than fabricating one. There is no opening for a new fact to slip in.

**3. Two Claudes grade.** Once the writer turn finishes, a separate reviewer turn reads `RUBRIC.md` fresh from disk and scores. Each artifact has its own 5 dimensions (for the English resume: metric density, action verb quality, structure, banned phrases, persona fit). You get a JSON alongside the markdown with per-dimension scores 0–5, a total, cited-entity recall, and any banned-phrase hits. If any dimension lands below 4, LockedIn auto-refines once before you see the result.

**4. Your experience and your conversation stay in sync.** If you edited a markdown file by hand, or said something in chat that conflicts with what's already there, LockedIn notices first and asks one focused question to reconcile. This is possible because your experience is stored as typed entities, not free-form text. The AI compares only the changed fields instead of re-reading everything. Sync cost scales with what changed, not with how large your experience grows. The richer your experience becomes, the more this matters.

## Skills

| Function | Skill | Role |
|---|---|---|
| Talk to LockedIn | `/lockedin` | The natural-language entry point. Hears what you ask, routes to the right sub-skill, runs the Q&A interview when your experience is empty, and notices when the conversation and your existing experience have drifted apart. |
| Write an English resume | `/lockedin-render-resume-en` | Pulls from your experience and writes a resume tuned to a target persona. 10 built-in personas cover senior IC, mid-level, PM, backend, frontend, mobile, data engineer, ML engineer, designer, and marketing roles. Other targets work too; the rubric stays calibrated and only the persona-fit dimension gets more conservative. Scored on metric density, action verb quality, structure, banned phrases, and persona fit. |
| Write a Korean cover letter | `/lockedin-render-jaso` | Give it a company and a question; it cites your experience and writes the answer. Reviewed against a five-dimension Korean rubric (<!-- ko-example -->두괄식, 구조화, 구체성, 표현, 적합성<!-- /ko-example -->) with a cross-source-verified list of banned phrases the draft must avoid. |
| Draft an interview answer | `/lockedin-render-interview` | Give it the company, the role, and the question; it answers in STAR or PAR shape, one experience per paragraph with explicit transition sentences so an interviewer can follow you. Scored on clarity, evidence, persona fit, conciseness, and tone. |
| Surface next project ideas | `/lockedin-render-ideas` | Reads your experience and pitches 3 to 5 directions you could take next, each one a one-paragraph pitch that cites the specific entries making it a fit for you. Scored on feasibility, novelty, evidence grounding, scope match, and motivation alignment. |
| Audit any resume | `/lockedin-audit` | Drop a resume PDF or DOCX and get a 5-dimension score. |

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
