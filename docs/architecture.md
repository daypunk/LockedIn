# selfgraph architecture

> Authoritative reference for how the pieces fit together.

## Execution model: skill-driven, CLI-assisted

selfgraph is a Claude Code skill, not a standalone agent. Reasoning runs
inside the host AI assistant on the user's existing subscription. The
Python CLI is a deterministic helper, not a parallel runtime.

```
┌──────────────────────────────────────────────────────────────────────┐
│  Host: Claude Code session (user's subscription)                     │
│                                                                      │
│   ┌─ User says "/selfgraph render jaso ..." or natural language      │
│   │                                                                  │
│   ▼                                                                  │
│   Skill activates (selfgraph/skill/SKILL.md)                         │
│     ├─ Interviewer: ask the user one question at a time              │
│     ├─ Ingester: classify diff, resolve ambiguities by asking        │
│     ├─ Renderer: writer turn → reviewer turn (RUBRIC.md re-loaded)   │
│     └─ GraphCurator: surface dangling references in batches          │
│                                                                      │
│   When deterministic work is needed, the skill issues a Bash call:   │
│      python3 ~/.claude/skills/selfgraph/helpers/render_graph.py ...  │
│      selfgraph validate                                              │
│      selfgraph render graph                                          │
│      selfgraph install --check                                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Pure CLI utilities (no LLM, run anywhere)                           │
│                                                                      │
│   selfgraph render graph                # graph.html from graph.json │
│   selfgraph init --non-interactive --fixture FILE                    │
│   selfgraph ingest <path> --dry-run     # diff preview, no merge     │
│   selfgraph validate / doctor / install / template add/remove        │
│                                                                      │
│   Skill-required commands typed here print a redirect (exit 3).      │
└──────────────────────────────────────────────────────────────────────┘
```

**Why this split exists.** Claude's reasoning is the expensive resource
(tokens). Anything that does not need it (file I/O, AST/PDF/DOCX text
extraction, graph JSON walking, HTML templating) belongs in the CLI so
the skill stays focused on the parts that genuinely require an LLM. This
also means the renderer's "interactive graph viz" deliverable is just an
HTML file you open in a browser — Claude Code's TUI itself is closed and
we don't try to render visuals inside it.



## Two install paths, one source of truth

selfgraph ships as a single repo with **two install paths**:

```
                 ┌─────────────────────────────────────────────┐
                 │  ~/.claude/skills/selfgraph/  (skill files) │
                 │   ├ SKILL.md / AGENTS.md / TOOLS.md         │
                 │   ├ render-jaso/ / render-resume-en/ / ...  │
                 │   └ helpers/  ← single-file Python helpers  │
                 │     for the skill-only path                 │
                 └─────────────────────────────────────────────┘
                                       ▲
                                       │ both paths register here
                                       │
   ┌────────────────────────────┐      │      ┌────────────────────────────┐
   │ Skill-only path            │      │      │ CLI accelerator path       │
   │ git clone <repo> →         │──────┘      │ uv tool install selfgraph  │
   │   ~/.claude/skills/...     │             │ selfgraph install          │
   │ python3 only, system       │             │   --auto-register          │
   │ helpers via `python3 -c`   │             │ Adds: PDF ingest,          │
   └────────────────────────────┘             │       multi-template,      │
                                              │       validate, doctor     │
                                              └────────────────────────────┘
```

Both paths produce **byte-identical output** on shared fixtures (`init`,
notes round-trip, graph derivation). CI enforces this via the parity test.

## The vault is the contract

```
~/.selfgraph/                       ← user-owned, Obsidian-compatible
├── career/                         ← default template (vault folder)
│   ├── person/<slug>.md            ← entity notes, frontmatter has type+links
│   ├── company/<slug>.md
│   ├── role/<slug>.md
│   └── ...
├── meeting/                        ← optional template (selfgraph template add meeting)
│   └── ...
└── outputs/                        ← rendered artifacts
    ├── graph.json
    ├── graph.html                  ← single-file viz, the project's hero asset
    ├── resume-us-tech-senior.md
    ├── jaso-<slug>-1.md
    └── portfolio/index.html
```

Every entity is one markdown file. Every edge is one entry in a note's
`links:` frontmatter. `graph.json` is derived; the markdown is the source
of truth. `selfgraph validate` walks the vault and reports any frontmatter
that does not conform to `selfgraph/ontology/schema.py`.

## Renderer two-turn pattern

```
┌─────────────────┐   ┌─────────────────┐   ┌──────────────────────────┐
│ Writer turn     │ → │ banned-phrase   │ → │ Reviewer turn            │
│ - query vault   │   │ regex check     │   │ - re-load RUBRIC.md      │
│ - draft jaso/   │   │ (jaso only)     │   │ - score 5 dimensions     │
│   resume        │   │                 │   │ - emit JSON              │
│ - quote slugs   │   │                 │   │ - revise once if any < 4 │
└─────────────────┘   └─────────────────┘   └──────────────────────────┘
```

The two turns are intentionally separate Claude contexts to prevent the
writer-reviewer fusion that inflates self-scores by ~1 point.

## Subscription path

`selfgraph` is not an Anthropic API client. The Python CLI never calls
`anthropic.Client`. Reasoning steps run as Claude Code skill calls; the
user pays for them via their existing subscription. `selfgraph doctor`
detects API key configuration and exits non-zero unless the user opts in
via `SELFGRAPH_ALLOW_API_KEY=1`.

## Roadmap shape

- Repo + ontology schema + CLI surface (current)
- Q&A interview engine + storage layer
- Document ingestion (.pdf / .docx / .md / .txt) + graph derivation + graph.html
- Renderer skills with research-driven prompts and rubrics
- Skill polish + two-recipe CI
- Demo recording, README polish, soft launch
