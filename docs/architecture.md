# lockedin architecture

> Authoritative reference for how the pieces fit together.

## Execution model: skill-driven, CLI-assisted

lockedin is a Claude Code skill, not a standalone agent. Reasoning runs
inside the host AI assistant on the user's existing subscription. The
Python CLI is a deterministic helper, not a parallel runtime.

```
┌──────────────────────────────────────────────────────────────────────┐
│  Host: Claude Code session (user's subscription)                     │
│                                                                      │
│   ┌─ User says "/lockedin render jaso ..." or natural language      │
│   │                                                                  │
│   ▼                                                                  │
│   Skill activates (lockedin/skill/SKILL.md)                         │
│     ├─ Interviewer: ask the user one question at a time              │
│     ├─ Ingester: classify diff, resolve ambiguities by asking        │
│     ├─ Renderer: writer turn → reviewer turn (RUBRIC.md re-loaded)   │
│     └─ GraphCurator: surface dangling references in batches          │
│                                                                      │
│   When deterministic work is needed, the skill issues a Bash call:   │
│      lockedin validate                                              │
│      lockedin migrate                                               │
│      lockedin experience <slug>                                     │
│      lockedin install --check                                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Pure CLI utilities (no LLM, run anywhere)                           │
│                                                                      │
│   lockedin init --non-interactive --fixture FILE                    │
│   lockedin ingest <path> --dry-run     # diff preview, no merge     │
│   lockedin validate / doctor / install / template add/remove       │
│   lockedin migrate / experience <slug>                             │
│                                                                      │
│   Skill-required commands typed here print a redirect (exit 3).      │
└──────────────────────────────────────────────────────────────────────┘
```

**Why this split exists.** Claude's reasoning is the expensive resource
(tokens). Anything that does not need it (file I/O, AST/PDF/DOCX text
extraction, frontmatter parsing) belongs in the CLI so the skill stays
focused on the parts that genuinely require an LLM.



## Two install paths, one source of truth

lockedin ships as a single repo with **two install paths**:

```
                 ┌─────────────────────────────────────────────┐
                 │  ~/.claude/skills/lockedin/  (skill files) │
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
   │ git clone <repo> →         │──────┘      │ uv tool install lockedin  │
   │   ~/.claude/skills/...     │             │ lockedin install          │
   │ python3 only, system       │             │   --auto-register          │
   │ helpers via `python3 -c`   │             │ Adds: PDF ingest,          │
   └────────────────────────────┘             │       multi-template,      │
                                              │       validate, doctor     │
                                              └────────────────────────────┘
```

Both paths produce **byte-identical output** on shared fixtures (`init`,
notes round-trip, validate). CI enforces this via the parity test.

## The vault is the contract

```
~/Documents/LockedIn/                       ← user-owned, Obsidian-compatible
├── career/                         ← default template (vault folder)
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
`links:` frontmatter. The markdown is the source of truth. `lockedin
validate` walks the vault and reports any frontmatter that does not
conform to `lockedin/ontology/schema.py`.

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

`lockedin` is not an Anthropic API client. The Python CLI never calls
`anthropic.Client`. Reasoning steps run as Claude Code skill calls; the
user pays for them via their existing subscription. `lockedin doctor`
detects API key configuration and exits non-zero unless the user opts in
via `LOCKEDIN_ALLOW_API_KEY=1`.

## Roadmap shape

- Repo + ontology schema + CLI surface (current)
- Q&A interview engine + storage layer
- Document ingestion (.pdf / .docx / .md / .txt)
- Renderer skills with research-driven prompts and rubrics
- Skill polish + two-recipe CI
- Demo recording, README polish, soft launch
