# CLAUDE.md

Project-level instructions, loaded automatically by Claude Code when
working in this repo. **Read this first** if you're picking up the
project in a fresh session — it's designed to be self-contained enough
that you can resume without prior conversation context.

## What this is

`selfgraph` is a Claude Code plugin that organizes a user's experience
(career, meetings, projects, learning) into a typed markdown ontology
they own at `~/.selfgraph/`, then renders artifacts (resume, cover
letter, portfolio, graph viz) from the same vault. Two stores by
design: **Store A** = user's input, structured into the vault.
**Store B** = `~/.selfgraph/outputs/` = artifacts rendered from A.

This repo holds the engine — the plugin manifests, skill files, CLI
helpers, and tests. Users' actual data lives at `~/.selfgraph/`,
**never** in this repo.

Tagline: *Personal experience knowledge graph for Claude Code. Zero
learning curve.* Distribution is the Claude Code plugin marketplace
(`/plugin marketplace add daypunk/selfgraph`).

## Current state — v0.0.1, pre-alpha

Single commit history. The shape is in place; behavior is partial.
Everything below is committed at HEAD.

| Layer | State |
| --- | --- |
| Plugin marketplace | manifests at `.claude-plugin/marketplace.json` and `plugins/selfgraph/.claude-plugin/plugin.json` |
| One-time setup wizard | `/selfgraph:setup` at `plugins/selfgraph/commands/setup.md` (HUD wiring + Q&A language + vault path) |
| Ontology | **v0.2** — 15 entity types, 15 edge predicates, JSON Resume / Schema.org / FOAF aligned. Per-type field contracts and edge domain/range enforced by `selfgraph validate`. See `selfgraph/ontology/schema.py`. |
| Render skills | `selfgraph` (main), `selfgraph-render-jaso`, `selfgraph-render-resume-en`, `selfgraph-render-portfolio` under `plugins/selfgraph/skills/`. Prompts/RUBRIC at v0.1 foundational; cultural calibration is the v1 blocker. |
| Render graph | DONE. Vendored force-graph 1.51.4 UMD bundle (~178 KB) in `plugins/selfgraph/scripts/vendor/force-graph.min.js`. Single-file interactive `graph.html` ~182 KB total. See `docs/adr/0001-viz-library.md`. |
| HUD | `selfgraph X.Y.Z │ 5h:NN% · wk:NN% │ vault: Nn · Me`. Counts user turns from `~/.claude/projects/*/*.jsonl`. Color on by default. Same script in two places (`plugins/selfgraph/scripts/hud.py` standalone, `selfgraph/commands/hud.py` package); the standalone defers to the package when available. |
| Deterministic CLI | `install` (with `--setup-hud` / `--remove-hud` / lifecycle), `init --fixture FILE`, `ingest --dry-run`, `render graph`, `validate`, `doctor`, `template`, `hud`. |
| Skill-only commands | `init` (interactive), `ingest` (smart), `render jaso/resume/portfolio`, `query`. Typed in plain shell, the CLI prints a redirect (exit 3) and points at Claude Code. |
| Tests | 52 passing across import, ontology, storage round-trip, install lifecycle, doctor, validate v0.2, render graph, init from fixture, template, ingest dry-run, hud. |

## Repo layout

```
.claude-plugin/marketplace.json     ← marketplace catalog
plugins/selfgraph/                  ← the plugin itself
├── .claude-plugin/plugin.json
├── commands/setup.md               ← /selfgraph:setup wizard
├── scripts/
│   ├── hud.py                      ← standalone HUD (no Python pkg required)
│   └── vendor/force-graph.min.js   ← vendored viz library
└── skills/
    ├── selfgraph/                  ← main skill (SKILL/AGENTS/TOOLS.md)
    │   └── templates/career/questions.yaml
    ├── selfgraph-render-jaso/      ← Korean cover letter (Korean OK in skill files)
    ├── selfgraph-render-resume-en/ ← English resume
    └── selfgraph-render-portfolio/ ← Static portfolio site

selfgraph/                          ← Python package (optional CLI accelerator)
├── cli.py · config.py · __main__.py · __init__.py
├── ontology/{__init__,schema}.py   ← 15 entity types, 15 edge predicates, v0.2
├── storage/{notes,graph}.py        ← markdown read/write, graph derivation
├── ingest/{interview,markdown,pdf,docx,text}.py
├── render/{_template,graph_html}.py
└── commands/{install,doctor,validate,init,ingest_dry,render_graph,template,hud}.py

docs/                               ← architecture / spec / mappings / guides
├── architecture.md · ontology-spec.md · ontology-mapping.md
├── orchestration.md · hud.md · cli.md
└── adr/0001-viz-library.md         ← ACCEPTED: vendored force-graph

tests/                              ← pytest suite + fixtures + research-allowlist
├── test_smoke · test_storage_roundtrip · test_commands · test_hud · test_init_template_ingest
└── fixtures/jaso/{pass,fail}/      ← TEMPLATE.md + .gitkeep, awaits domain reviewer

examples/sample-vault.yaml          ← fixture seed for `selfgraph init --fixture`
README.md · README.ko.md · CHANGELOG.md · LICENSE · .gitignore · pyproject.toml
```

## Working agreements

- **Never invent ontology data.** Notes get written from real user
  input or user-confirmed transformations only. Same for fixtures —
  do not fabricate Korean cover letters or English resumes; the
  `tests/fixtures/jaso/{pass,fail}/` directory awaits a real domain
  reviewer.
- **The markdown is the contract.** If `selfgraph/ontology/schema.py`
  changes, also update `docs/ontology-spec.md`,
  `docs/ontology-mapping.md`, and the renderer skills' SKILL.md.
- **stdlib-first Python.** `pyproject.toml` has `dependencies = []`.
  PDF (`pypdf`) and DOCX (`python-docx`) are optional extras.
- **English skills, polyglot output.** All files inside
  `plugins/selfgraph/skills/` are English **except** the
  `selfgraph-render-jaso/` directory which is exempt from the
  language-policy lint (its domain is Korean output). Korean inline
  examples elsewhere belong in fenced
  `<!-- ko-example -->...<!-- /ko-example -->` blocks.
- **Subscription, not API keys.** selfgraph reasoning runs through
  Claude Code skills on the user's existing subscription. The Python
  CLI never calls the Anthropic API directly. `selfgraph doctor`
  detects API key configuration and warns unless the user opts in via
  `SELFGRAPH_ALLOW_API_KEY=1`.
- **Two-turn writer/reviewer for renderers.** Writer turn drafts;
  reviewer turn re-loads `RUBRIC.md` fresh and emits a JSON score.
  Same-context self-evaluation inflates scores by ~1 point — split is
  load-bearing.
- **The user's vault is sacred.** Read freely; write only through
  documented CLI commands (with their `--dry-run` flags) or with
  explicit user instruction.
- **Single-commit history (for now).** All work amends `HEAD`. We
  preserve the option to push as one initial commit; if commits
  proliferate later we can switch policies, but right now amend is
  the default.
- **README has language switcher** at top: `English · [한국어]` and
  the inverse.

## What to NEVER do

- **Never refactor `plugins/selfgraph/skills/selfgraph-render-jaso/`
  to remove Korean.** It is the one English-policy exempt skill;
  its domain is Korean output.
- **Never write to `~/.selfgraph/`** from tests or scripts unless
  pointed at by `SELFGRAPH_VAULT` to a temp dir. The user's real
  vault is theirs.
- **Never auto-modify `~/.claude/settings.json`** outside the
  documented `selfgraph install --setup-hud` / `--remove-hud` flow.
  Setup is opt-in via the wizard; silent statusLine writes break
  trust.
- **Never crash the HUD.** The statusLine command runs every few
  hundred ms; on any unexpected error the HUD must fall back to the
  bare label `selfgraph` and exit 0.
- **Never fabricate a domain fixture.** Especially Korean cover
  letters. Use `tests/fixtures/jaso/TEMPLATE.md` as the contribution
  shape and wait for a real reviewer.

## Subscription path enforcement

`selfgraph doctor` is the canonical diagnostic. It reports:

- skill installation state at `~/.claude/skills/selfgraph/SKILL.md`
- whether `ANTHROPIC_API_KEY` is set vs `SELFGRAPH_ALLOW_API_KEY=1`
  opt-in
- vault path and Python version

CI exercises both paths: `ANTHROPIC_API_KEY=fake` should exit non-zero,
`unset` should exit zero.

## Open TBDs (v1 release blockers)

| TBD | What's needed | Where to leave the result |
| --- | --- | --- |
| Korean 자소서 fixtures (5 pass + 5 fail) | Domain reviewer to author / curate per `tests/fixtures/jaso/TEMPLATE.md` | `tests/fixtures/jaso/{pass,fail}/*.md` |
| `render-jaso` cultural reviewer | Named human + fallback channel | `plugins/selfgraph/skills/selfgraph-render-jaso/reviewers.md` |
| `render-resume-en` rubric + prompts | Author after `research-notes.md` is locked | `plugins/selfgraph/skills/selfgraph-render-resume-en/{RUBRIC,prompt-writer,prompt-reviewer}.md` |
| `render-resume-en` `banned_phrases.json` | Cross-check published resume guides | `plugins/selfgraph/skills/selfgraph-render-resume-en/banned_phrases.json` |
| GitHub repo + first marketplace install | User action (auth required) | `git remote add origin …; git push -u origin main` |
| v0.3 orchestration | Explicit 5-step render pipeline + parallel bulk-ingest dispatcher | See `docs/orchestration.md` |
| v0.4 graph curator | Quarterly duplicate-merge agent | See `docs/orchestration.md` |
| `selfgraph migrate` | Auto-migration for v0.1 → v0.2 vaults | `selfgraph/commands/migrate.py` (new) |

These are also listed in `CHANGELOG.md` "Known gaps before v1".

## Verification quick reference

```bash
python3 -m selfgraph --version                      # version banner
python3 -c "from selfgraph.ontology import ENTITY_TYPES, EDGE_PREDICATES; print(len(ENTITY_TYPES), len(EDGE_PREDICATES))"   # 15 15
python3 -m pytest -q                                # 52/52 expected
python3 -m selfgraph doctor                         # subscription/skill check
SELFGRAPH_VAULT=/tmp/sg python3 -m selfgraph init --fixture examples/sample-vault.yaml
SELFGRAPH_VAULT=/tmp/sg python3 -m selfgraph validate
SELFGRAPH_VAULT=/tmp/sg python3 -m selfgraph render graph
SELFGRAPH_VAULT=/tmp/sg python3 -m selfgraph hud
```

`tests/fixtures/sample-vault.yaml` and `examples/sample-vault.yaml` are
both authored to v0.2 schema (required fields per type). Use them as
shape references when authoring new fixtures.

## Resume protocol — fresh-session pickup

If you are a Claude session opened with **no prior context**:

1. Read this file (you're doing it).
2. Read `README.md` for the user-facing pitch and the install / use
   flow.
3. Read `docs/architecture.md` for the skill / CLI split.
4. Read `docs/ontology-spec.md` and `docs/ontology-mapping.md` for the
   data contract.
5. Skim `CHANGELOG.md` "Known gaps before v1" for what's outstanding.
6. If the working notes / spec / plan files exist locally at
   `.omc/specs/` and `.omc/plans/`, those are gitignored
   internal-only artifacts — they capture the original requirements
   interview and the architecture consensus pass. Read them only if
   you need history that's not in this CLAUDE.md.
7. Before any significant change, run `pytest -q` to confirm the
   baseline is green.
8. If a change touches the ontology, update **all four** of:
   `selfgraph/ontology/schema.py`, `docs/ontology-spec.md`,
   `docs/ontology-mapping.md`, and the renderer skills' SKILL.md
   that reference field shapes.
