---
name: selfgraph
description: |
  Personal experience knowledge graph for Claude Code. Build and grow a
  markdown ontology from Q&A interviews and document ingestion (PDF, DOCX,
  MD, TXT), then render English resumes, Korean cover letters,
  portfolios, meeting notes, and an interactive graph visualization from
  the same vault. Runs entirely on the user's Claude Code subscription —
  never calls the Anthropic API directly.

  Activate when the user mentions selfgraph by name, asks to set up or
  update a personal career / experience graph, asks to render a resume /
  cover letter / portfolio / meeting note from their own experience,
  drops a resume PDF or DOCX with a request to absorb it, or queries
  their own experience ("what projects used Rust?", "which roles taught
  me X"). Do NOT activate for unrelated coding, code review, or general
  questions.
---

# selfgraph

Build and grow a personal markdown ontology in `~/.selfgraph/`, then
render artifacts from it. Single-purpose: one namespace, one demo.

## Use this skill when

- The user says "selfgraph" or "career graph" or "experience graph".
- The user asks to render an artifact from their own experience: a
  resume, a cover letter, a portfolio, a meeting note.
- The user drops a resume `.pdf` / `.docx` or career notes and asks to
  absorb them into a structured graph.
- The user asks a query about their own experience.

## Do NOT use this skill when

- The user asks general coding / code review / debugging questions.
- The user asks about somebody else's experience or a public dataset.
- The user wants a one-shot AI answer with no vault to maintain — point
  them at Claude Projects on claude.ai instead.

## Execution model

Reasoning runs **inside Claude Code** on the user's subscription; the
`selfgraph` Python CLI is a deterministic helper for non-LLM work.

| Surface | Runs there | When |
|---|---|---|
| Skill (host AI) | Q&A interview, ingest ambiguity resolution, render writer + reviewer turns, NL query interpretation | Every user-in-the-loop flow |
| CLI utility | install, doctor, validate, template, render graph, init --fixture, ingest --dry-run, PDF/DOCX text extraction, hud | Deterministic; called by skill via Bash, or by user directly |

If a skill-only command (`render jaso/resume/portfolio`, interactive
`init`, smart `ingest`, `query`) is typed in a plain terminal, the CLI
prints a redirect message — that's expected.

## First activation — safety net for skipped setup

Recommended onboarding is the explicit `/selfgraph:setup` wizard. This
section is the safety net for users who skipped it and started using
the skill directly.

1. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/selfgraph/config.json`. If
   the file exists and has a `setup_completed` timestamp, do nothing —
   the user already ran the wizard.
2. If the config is missing or has no `setup_completed`, offer the
   wizard ONCE per session: *"Looks like setup hasn't run. Want me to
   walk through it now? Wires the bottom HUD and a couple of defaults.
   `/selfgraph:setup` runs the full wizard; I can also do just the HUD
   step inline."*
3. If the user accepts the inline shortcut, run the HUD step from
   `/selfgraph:setup` (Step 1) only. Otherwise, run the full wizard, or
   continue with the user's original request and remember not to ask
   again this session.

The skill is fully functional without setup — only the bottom HUD line
will not appear until the user wires it.

## Core flow

1. **Init** — `/selfgraph init` (or natural language) runs a Q&A
   interview that seeds the vault with the user's first ontology nodes
   (career template by default).
2. **Ingest** — `/selfgraph ingest <path>` reads `.pdf` / `.docx` /
   `.md` / `.txt`, emits a typed diff, asks the user about ambiguities
   one at a time, then merges.
3. **Render** — `/selfgraph render <kind>` produces the artifact. Writer
   turn drafts; reviewer turn re-loads `RUBRIC.md` fresh and scores. If
   any rubric dimension < 4, revise once with the notes.
4. **Iterate** — every conversation grows the graph. Renders are queries
   against it.

See `AGENTS.md` for the four sub-roles (Interviewer / Ingester /
Renderer / GraphCurator). See `TOOLS.md` for the canonical CLI calls
each role issues, with skill-only-path fallbacks.

## Subscription, not API keys

This skill assumes the user runs Claude Code on a subscription. If the
shell environment has `ANTHROPIC_API_KEY` set, run `selfgraph doctor` —
it will warn unless the user explicitly opts in via
`SELFGRAPH_ALLOW_API_KEY=1`.

## Language policy

- All instruction prose in this skill directory is English (CI lint
  enforces this for every file except `render-jaso/`, whose domain is
  Korean output).
- Korean reference examples elsewhere must sit inside fenced
  `<!-- ko-example -->...<!-- /ko-example -->` blocks.
- Rendered artifacts use the artifact's native language: `render-jaso`
  emits Korean, `render-resume-en` emits English.

## Source of truth

- Schema: `selfgraph/ontology/schema.py` (11 entity types, 12 edge predicates)
- Architecture: `docs/architecture.md`
- Vault contract: `docs/ontology-spec.md`

## Final checklist (self-verify before declaring a flow done)

- Vault writes only happened with user confirmation (or via deterministic
  CLI fixture path).
- Renderer ran writer turn → reviewer turn (RUBRIC.md re-loaded fresh).
- For `render-jaso`: banned-phrase regex check ran before rubric scoring.
- Concrete ontology nodes (slugs) quoted in rendered text, not vague
  generalities.
- Output artifact written under `<vault>/outputs/` with timestamp slug.
