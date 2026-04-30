# selfgraph

**English** · [한국어](README.ko.md)

> **Personal experience knowledge graph for Claude Code. Zero learning curve.**
> Don't learn schemas. Don't learn commands. Talk to Claude — selfgraph
> structures your experience and renders any artifact you ask for.

[![Status](https://img.shields.io/badge/status-pre--alpha-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

## Install

Inside Claude Code, three commands:

```
/plugin marketplace add daypunk/selfgraph
/plugin install selfgraph@selfgraph
/selfgraph:setup
```

The third one is a one-time wizard (HUD wiring + a couple of preferences).
After it restarts your Claude Code window, the bottom of the chat shows
a status line with your Claude Code usage and vault state, and the
skill activates on natural language.

## Use it

Just say what you want.

Capture experience:

- *"start organizing my experience"*
- *"log today's meeting with the design team"*
- *"absorb this resume.pdf"*
- *"add what I learned this week from the LLM agents paper"*

Render from what's already there:

- *"make me a resume targeted at us-tech-senior"*
- *"write me a Korean cover letter for company X, question 1"*
- *"summarize last quarter's decisions"*
- *"show me my graph"*

selfgraph picks the right flow and asks one question at a time when it
needs more from you. Slash commands (`/selfgraph init`, `/selfgraph
render resume`, …) work too if you prefer them.

## The two stores

<!-- diagram-store-ab : leave this block empty for the image to be inserted -->

## Why this exists

selfgraph is a tool for **organizing experience**. Meetings, learning,
work, side projects, decisions — every domain becomes a folder of
typed markdown notes you own. Once that structured store exists,
downstream uses are queries against it: a resume, a cover letter,
talking points, a quarterly retrospective, an idea derived from past
work.

Most tools regenerate every artifact from scratch. The artifact isn't
the truth — **the structured experience behind it is**.

## Features

- **Talk to it.** Natural-language activation. No commands required.
- **One graph, many renders.** English resume, Korean cover letter,
  static portfolio site, interactive graph viz — all from the same
  vault.
- **Two-turn writer/reviewer.** Renderers self-evaluate in separate
  Claude turns against a rubric. JSON score tells you if a draft is
  good before you submit.
- **Subscription, not API keys.** Reasoning runs through Claude Code
  skills. Lowest-viable model tier per task — small for diff sniff,
  mid for drafting, large only when nuance demands it.
- **You own everything.** Plain markdown on your disk at
  `~/.selfgraph/`. Obsidian-compatible. Portable. No phone-home.

## Status

Pre-alpha. The skill scaffold and CLI surface are in place. Renderer
prompts and rubrics are v0.1 foundational; ontology is v0.2 (15 entity
types, 15 edge predicates, JSON Resume / Schema.org / FOAF aligned).

## Advanced

Power-user CLI, statusLine HUD, vault schema, architecture, ontology
alignment, orchestration plan — see `docs/`:

- `docs/architecture.md` · `docs/ontology-spec.md` · `docs/ontology-mapping.md`
- `docs/orchestration.md` · `docs/hud.md` · `docs/cli.md`
- `docs/adr/` — architecture decisions (viz library, …)

## License

MIT. See [LICENSE](./LICENSE).
