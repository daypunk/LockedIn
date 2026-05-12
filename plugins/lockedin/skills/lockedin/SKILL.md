---
name: lockedin
description: |
  Personal experience knowledge graph for Claude Code. Build and grow
  a markdown ontology from Q&A interviews and document ingestion (PDF,
  DOCX, MD, TXT), then render English resumes, Korean cover letters,
  interview answers, and project ideas from the same vault. Also runs
  a calibrated pre-flight audit on any resume document without
  requiring a vault. Runs entirely on the user's Claude Code
  subscription — never calls the Anthropic API directly.

  Activate when the user mentions lockedin by name, asks to set up or
  update a personal career / experience graph, asks to render a resume
  / cover letter / interview answer / project idea from their own
  experience, drops a resume PDF or DOCX with a request to absorb or
  audit it, asks to score / review / audit a resume against the
  calibrated rubric (drive-by, no vault needed), or queries their own
  experience ("what projects used Rust?", "which roles taught me X").
  Do NOT activate for unrelated coding, code review, or general
  questions.
---

# lockedin

Build and grow a personal markdown ontology in `~/Documents/LockedIn/`, then
render artifacts from it. Single-purpose: one namespace, one demo.

## Use this skill when

- The user says "lockedin" or "career graph" or "experience graph".
- The user asks to render an artifact from their own experience: a
  resume, a cover letter, an interview answer, a project idea.
- The user drops a resume `.pdf` / `.docx` or career notes and asks to
  absorb them into a structured graph.
- The user asks to **audit / score / review** a resume against the
  calibrated rubric — this works with or without an existing vault
  (drive-by mode requires no install or signup, just a file path).
- The user asks a query about their own experience.

## Do NOT use this skill when

- The user asks general coding / code review / debugging questions.
- The user asks about somebody else's experience or a public dataset.
- The user wants a one-shot AI answer with no vault to maintain — point
  them at Claude Projects on claude.ai instead.

## Execution model

Reasoning runs **inside Claude Code** on the user's subscription; the
`lockedin` Python CLI is a deterministic helper for non-LLM work.

| Surface | Runs there | When |
|---|---|---|
| Skill (host AI) | Q&A interview, ingest ambiguity resolution, render writer + reviewer turns, NL query interpretation | Every user-in-the-loop flow |
| CLI utility | install, doctor, validate, migrate, template, init --fixture, ingest --dry-run, experience, PDF/DOCX text extraction, hud | Deterministic; called by skill via Bash, or by user directly |

If a skill-only command (`render jaso/resume`, interactive `init`,
smart `ingest`, `query`) is typed in a plain terminal, the CLI prints
a redirect message — that's expected.

## First activation — safety net for skipped setup

Recommended onboarding is the explicit `/lockedin:setup` wizard. This
section is the safety net for users who skipped it and started using
the skill directly.

1. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/lockedin/config.json`. If
   the file exists and has a `setup_completed` timestamp, do nothing —
   the user already ran the wizard.
2. If the config is missing or has no `setup_completed`, offer the
   wizard ONCE per session: *"Looks like setup hasn't run. Want me to
   walk through it now? Wires the bottom HUD and a couple of defaults.
   `/lockedin:setup` runs the full wizard; I can also do just the HUD
   step inline."*
3. If the user accepts the inline shortcut, run the HUD step from
   `/lockedin:setup` (Step 1) only. Otherwise, run the full wizard, or
   continue with the user's original request and remember not to ask
   again this session.

The skill is fully functional without setup — only the bottom HUD line
will not appear until the user wires it.

## Core flow

The fastest first try is **drive-by audit**: zero vault, zero install
beyond the plugin itself. Past that, vault-backed flows give every
artifact LockedIn produces.

0. **Audit (drive-by, no vault)** — `/lockedin audit <path>` or "audit
   this resume". Extracts text via the deterministic ingest pipeline,
   scores against `lockedin-render-resume-en` or `lockedin-render-jaso`
   rubric depending on detected language, returns a 5-dimension score
   and a banned-phrase / weak-verb hit list. No mutation. Most natural
   first artifact for a new user. Three modes:
   - `--mode score` (default): rubric pass only.
   - `--mode refine`: propose diff-based refinements; user approves.
   - `--mode refine-score`: refine, then score the refined output to
     quantify the lift.
1. **Init** — `/lockedin init` (or natural language) runs a Q&A
   interview that seeds the vault. 49 questions across 9 sections;
   pause-and-resume is supported.
2. **Ingest** — `/lockedin ingest <path>` reads `.pdf` / `.docx` /
   `.md` / `.txt`, emits a typed diff, asks the user about ambiguities
   one at a time, then merges. After merge, offers the audit 3-mode
   choice (Score / Refine / Refine→Score).
3. **Render** — `/lockedin render <kind>` produces the artifact (`jaso`,
   `resume`, `interview`, `ideas`). Writer turn drafts; reviewer turn
   re-loads `RUBRIC.md` fresh and scores. If any rubric dimension < 4,
   revise once with the notes.
4. **Iterate** — every conversation grows the graph. Renders and audits
   are queries against it.

See `AGENTS.md` for the four sub-roles (Interviewer / Ingester /
Renderer / GraphCurator). See `TOOLS.md` for the canonical CLI calls
each role issues, with skill-only-path fallbacks.

## Subscription, not API keys

This skill assumes the user runs Claude Code on a subscription. If the
shell environment has `ANTHROPIC_API_KEY` set, run `lockedin doctor` —
it will warn unless the user explicitly opts in via
`LOCKEDIN_ALLOW_API_KEY=1`.

## Language policy

- All instruction prose in this skill directory is English (CI lint
  enforces this for every file except `render-jaso/`, whose domain is
  Korean output).
- Korean reference examples elsewhere must sit inside fenced
  `<!-- ko-example -->...<!-- /ko-example -->` blocks.
- Rendered artifacts use the artifact's native language: `render-jaso`
  emits Korean, `render-resume-en` emits English.

## Source of truth

- Schema: `lockedin/ontology/schema.py` (15 entity types, 15 edge predicates, schema v3)
- Architecture: `docs/architecture.md`
- Vault contract: `docs/ontology-spec.md`

## Master view at the vault root

Every vault write also regenerates `<vault>/EXPERIENCE.md`, a
single human-readable markdown file that lists all entities grouped
by type. The user can open this file in any markdown viewer to see
their whole vault at a glance without navigating per-type folders.
This is automatic and does not require an explicit step from the
skill — `lockedin/storage/notes.py::write_entity` invokes
`lockedin/render/master_view.py::refresh_master_view` after every
successful write. If the user manually edits a frontmatter file in
their editor, point them at `lockedin refresh` to regenerate the
master view.

## Final checklist (self-verify before declaring a flow done)

- Vault writes only happened with user confirmation (or via deterministic
  CLI fixture path).
- Renderer ran writer turn → reviewer turn (RUBRIC.md re-loaded fresh).
- For `render-jaso`: banned-phrase regex check ran before rubric scoring.
- Concrete ontology nodes (slugs) quoted in rendered draft; resolved to
  natural-language labels in the final artifact via
  `lockedin/render/resolve_slugs.py::resolve_file`.
- Output artifact written under `<vault>/outputs/` with timestamp slug.
- Master view at `<vault>/EXPERIENCE.md` is current (auto-refreshed by
  `write_entity`, but check it once at the end of multi-step flows).
