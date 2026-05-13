# lockedin architecture

> Authoritative reference for how the pieces fit together.

## Design posture: harness-engineering patterns

lockedin implements the harness-engineering patterns that the
LLM-agent discourse keeps returning to: writer/reviewer separation in
distinct contexts, rubric-as-contract with JSON output, state
externalized to disk for resumable sessions, deterministic feedback
sensors (banned-phrase regex, schema validate, edge domain/range)
running *before* the LLM judges, and an "AI surfaces, user decides"
control flow that never silent-merges or fabricates. The control
plane lives in the skill manifests and the Python CLI; the model
chooses content, the harness chooses what happens next.

## Execution model: plugin + CLI

lockedin is a Claude Code plugin composed of seven focused skills, not
a standalone agent. Reasoning runs inside the host Claude Code session
on the user's existing subscription. The Python CLI is a deterministic
helper for file I/O and validation, not a parallel runtime.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Host: Claude Code session (user's subscription)                       │
│                                                                        │
│   ┌─ User talks naturally, or invokes /lockedin /lockedin-capture      │
│   │  /lockedin-render-jaso /lockedin-render-resume-en                  │
│   │  /lockedin-render-interview /lockedin-render-ideas /lockedin-audit │
│   ▼                                                                    │
│   Router skill (plugins/lockedin/skills/lockedin/SKILL.md)             │
│     ├─ routes to the right sub-skill based on intent                   │
│     ├─ runs the Q&A interview when the vault is empty                  │
│     └─ notices when conversation and vault drift; asks one question    │
│                                                                        │
│   Sub-skills (one focused responsibility each)                         │
│     ├─ lockedin-capture        in-session work capture                 │
│     ├─ lockedin-render-jaso    Korean cover letter                     │
│     ├─ lockedin-render-resume-en  English resume (10 personas)         │
│     ├─ lockedin-render-interview  STAR/PAR interview answers           │
│     ├─ lockedin-render-ideas   project direction proposals             │
│     └─ lockedin-audit          drive-by resume scoring                 │
│                                                                        │
│   When deterministic work is needed, any skill issues a Bash call:     │
│      lockedin validate / migrate / experience <slug>                   │
│      lockedin install --check / doctor                                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  Pure CLI utilities (no LLM, run anywhere)                             │
│                                                                        │
│   lockedin init --non-interactive --fixture FILE                       │
│   lockedin ingest <path> --dry-run     # diff preview, no merge        │
│   lockedin validate / doctor / install / template add/remove           │
│   lockedin migrate / experience <slug>                                 │
│                                                                        │
│   Skill-required commands typed here print a redirect (exit 3).        │
└────────────────────────────────────────────────────────────────────────┘
```

**Why this split exists.** Claude's reasoning is the expensive resource
(tokens). Anything that does not need it (file I/O, AST/PDF/DOCX text
extraction, frontmatter parsing) belongs in the CLI so the skill stays
focused on the parts that genuinely require an LLM.



## Install model: plugin + optional Python CLI

lockedin ships as a single repo with **one primary install path** and
an optional Python CLI accelerator:

```
                 ┌─────────────────────────────────────────────┐
                 │  Claude Code plugin (primary)               │
                 │   /plugin marketplace add daypunk/LockedIn  │
                 │   /plugin install lockedin@lockedin         │
                 │   /lockedin:setup                           │
                 │                                             │
                 │  Installs the skills, the HUD wrapper,      │
                 │  and the setup wizard. Reasoning runs       │
                 │  through Claude Code on the user's          │
                 │  existing subscription.                     │
                 └─────────────────────────────────────────────┘
                                       ▲
                                       │ optional accelerator
                                       │
                 ┌─────────────────────────────────────────────┐
                 │  Python CLI (optional)                      │
                 │   pip install -e .  /  python3 -m lockedin  │
                 │                                             │
                 │  Adds deterministic file I/O: validate,     │
                 │  migrate, init --fixture, ingest --dry-run, │
                 │  doctor, template, experience, refresh,     │
                 │  hud, install. stdlib-only by default; PDF, │
                 │  DOCX, and YAML support are optional        │
                 │  extras.                                    │
                 └─────────────────────────────────────────────┘
```

The plugin is enough on its own. The Python CLI exists so that
deterministic operations (frontmatter parsing, PDF/DOCX extraction,
graph derivation, validation) do not have to consume tokens. Both
surfaces read and write the same vault layout.

## The vault is the contract

```
~/Documents/LockedIn/                ← user-owned, Obsidian-compatible
├── experience/                     ← default template (vault folder)
│   ├── person/<slug>.md            ← entity notes, frontmatter has type+links
│   ├── company/<slug>.md
│   ├── role/<slug>.md
│   └── ...
├── meeting/                        ← optional template (lockedin template add meeting)
│   └── ...
└── outputs/                        ← rendered artifacts
    ├── resume-us-tech-senior.md
    └── jaso-<slug>-1.md
```

Every entity is one markdown file. Every edge is one entry in a note's
`links:` frontmatter, inferred from the interview session by domain/range
rules in `lockedin/ontology/schema.py`. Edges are explicit and auditable;
the renderer turn cites entity slugs but does not require edge traversal.
`lockedin validate` walks the vault and reports any frontmatter that does
not conform to the schema.

## Renderer two-turn pattern

```
┌─────────────────┐   ┌─────────────────┐   ┌──────────────────────────┐
│ Writer turn     │ → │ banned-phrase   │ → │ Reviewer turn            │
│ - query vault   │   │ regex check     │   │ - re-load RUBRIC.md      │
│ - draft output  │   │ (deterministic, │   │ - score 5 dimensions     │
│ - quote slugs   │   │  pre-rubric)    │   │ - emit JSON              │
│                 │   │                 │   │ - revise once if any < 4 │
└─────────────────┘   └─────────────────┘   └──────────────────────────┘
```

All six calibrated skills (jaso, resume-en, interview, ideas, capture,
audit) ship a `banned_phrases.json` regex pass that runs *before* the
reviewer turn. The two turns are intentionally separate Claude contexts
to prevent the writer-reviewer fusion that inflates self-scores by
~1 point. Slugs quoted by the writer are resolved to natural language
at render time; if no matching entity backs a claim, the slug stays
in place and the skill asks the user whether to add the entity rather
than fabricating one.

## Subscription path

`lockedin` is not an Anthropic API client. The Python CLI never calls
`anthropic.Client`. Reasoning steps run as Claude Code skill calls; the
user pays for them via their existing subscription. `lockedin doctor`
detects API key configuration and exits non-zero unless the user opts in
via `LOCKEDIN_ALLOW_API_KEY=1`.

