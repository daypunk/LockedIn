# LockedIn

**English** | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh.md)

<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

LockedIn lives inside your Claude Code session. While you're coding or writing docs, save the work that matters as structured experience. When you need a resume, a Korean cover letter, an interview answer, or a project idea, LockedIn writes it from that structured experience.

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

No commands to memorize, no extra tab to open. Just start naturally inside Claude Code.

To start fresh, build your experience from zero:

- "start organizing my experience"
- "interview me about my work history"
- "absorb my resume.pdf"

While you're working, capture moments as they happen:

- "save this commit as a project highlight"
- "this meeting just wrapped, log it"
- "I just learned how to use X, track it"

When you need to produce something:

- "make me an English resume"
- "I'm applying to company X for role Y, write the answer to question Z"
- "audit this resume PDF"

LockedIn asks one question at a time when it needs more from you, and it stops when it has enough.

<p align="center">
  <img src="docs/assets/architecture.png" alt="LockedIn architecture" width="100%" />
</p>

## Why it exists

Most tools for organizing experience want you to leave your work, log in somewhere else, and remember everything that mattered. By then, half of it is already gone from your head.

LockedIn lives where the work happens. While you're coding, writing docs, or reviewing a PR in Claude Code, you can say "save this to LockedIn" and the moment accumulates locally as a structured markdown file. No second tool to manage your experience, no context switch.

The files are yours. Open them in any editor, carry them to any tool. When you need a resume, a cover letter, or an interview answer, LockedIn writes one from your structured experience and skills.

## Features

- **No commands to memorize.** Type the way you'd talk and LockedIn picks the right skill.
- **Captures while you work.** Save a moment from your Claude Code session as structured experience, no context switch.
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
| Write a Korean cover letter | `/lockedin-render-jaso` | Give it a company and a question; it cites your experience and writes the answer. Reviewed against a five-dimension Korean rubric (lead-with-conclusion, structure, specificity, phrasing, fit) with a cross-source-verified list of banned phrases the draft must avoid. |
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
