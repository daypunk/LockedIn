# CLAUDE.md

Project-level instructions, loaded automatically by Claude Code when
working in this repo. **Read this first** if you're picking up the
project in a fresh session — it's designed to be self-contained enough
that you can resume without prior conversation context.

## What this is

`selfgraph` is a Claude Code plugin that organizes a user's experience
(career, meetings, projects, learning) into a typed markdown ontology
they own at `~/.selfgraph/`, then renders artifacts (resume, cover
letter, graph viz) from the same vault. Two stores by design:
**Store A** = user's input, structured into the vault.
**Store B** = `~/.selfgraph/outputs/` = artifacts rendered from A.

This repo holds the engine — the plugin manifests, skill files, CLI
helpers, and tests. Users' actual data lives at `~/.selfgraph/`,
**never** in this repo.

Tagline: *Personal experience knowledge graph for Claude Code. Zero
learning curve.* Distribution is the Claude Code plugin marketplace
(`/plugin marketplace add daypunk/selfgraph`).

## Current state — v1.0.0 (Beta), first public release

All v1.0 features land in this commit. Shipped as Beta — renderers
have research-based calibration but no named-human-reviewer pass yet
(v1.1 target). From v1.0 forward, history can grow with atomic
commits.

| Layer | State |
| --- | --- |
| Plugin marketplace | manifests at `.claude-plugin/marketplace.json` and `plugins/selfgraph/.claude-plugin/plugin.json` |
| One-time setup wizard | `/selfgraph:setup` at `plugins/selfgraph/commands/setup.md` (HUD wiring + Q&A language + vault path) |
| Ontology | **v0.2** — 15 entity types, 15 edge predicates, JSON Resume / Schema.org / FOAF aligned. Per-type field contracts and edge domain/range enforced by `selfgraph validate`. See `selfgraph/ontology/schema.py`. |
| Render skills | `selfgraph` (main), `selfgraph-render-jaso` (v1.0 calibrated, 5 + 5 fixtures), `selfgraph-render-resume-en` (v1.0 calibrated, 3 personas). All under `plugins/selfgraph/skills/`. (`render-portfolio` removed from v1.0 scope — see CHANGELOG "Removed before public Beta".) |
| Render graph | DONE. Vendored force-graph 1.51.4 UMD bundle (~178 KB) in `plugins/selfgraph/scripts/vendor/force-graph.min.js`. Single-file interactive `graph.html` ~182 KB total. See `docs/adr/0001-viz-library.md`. |
| HUD | `selfgraph X.Y.Z │ 5h:NN% · wk:NN% │ vault: Nn · Me`. Counts user turns from `~/.claude/projects/*/*.jsonl`. Color on by default. Same script in two places (`plugins/selfgraph/scripts/hud.py` standalone, `selfgraph/commands/hud.py` package); the standalone defers to the package when available. |
| Deterministic CLI | `install` (with `--setup-hud` / `--remove-hud` / lifecycle), `init --fixture FILE`, `ingest --dry-run`, `render graph`, `validate`, `doctor`, `template`, `hud`. |
| Skill-only commands | `init` (interactive), `ingest` (smart), `render jaso/resume`, `query`. Typed in plain shell, the CLI prints a redirect (exit 3) and points at Claude Code. |
| OSS infrastructure | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `.github/ISSUE_TEMPLATE/{bug_report, feature_request, korean_reviewer_onboarding, config}.yml`. |
| Tests | 52+ passing across import, ontology, storage round-trip, install lifecycle, doctor, validate v0.2, render graph, init from fixture, template, ingest dry-run, hud, plus non-LLM jaso fixture validation. |

## Repo layout

```
.claude-plugin/marketplace.json     ← marketplace catalog
.github/
├── ISSUE_TEMPLATE/                 ← bug / feature / Korean reviewer / config
└── workflows/ci.yml                ← lint, test, language policy, leakage scan
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
    │   └── RUBRIC + prompts + banned_phrases + reviewers + research-notes
    └── selfgraph-render-resume-en/ ← English resume (us-tech-senior / mid / pm-product)
        └── RUBRIC + prompts + banned_phrases + research-notes

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

tests/                              ← pytest suite + fixtures
├── test_smoke · test_storage_roundtrip · test_commands · test_hud · test_init_template_ingest
└── fixtures/jaso/{pass,fail}/      ← 5 + 5 synthetic golden fixtures (research-based)

examples/sample-vault.yaml          ← fixture seed for `selfgraph init --fixture`
README.md · README.ko.md · CHANGELOG.md · CONTRIBUTING.md · CODE_OF_CONDUCT.md · LICENSE
```

## Working agreements

- **Never invent ontology data for users.** Notes get written from
  real user input or user-confirmed transformations only. Synthetic
  fixtures used for tests must be clearly labeled (`composite`,
  placeholder names like `SOME_COMPANY` / `GLOBAL_TECH`); never use
  real persons, real companies, or quotes from real published 자소서.
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
- **Atomic commits welcome from v1.0+.** Single-commit history was
  the v0.x policy; v1.0 onwards, atomic commits are encouraged. See
  `CONTRIBUTING.md` "Commit style".
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
- **Never copy real published 자소서 / resume text into fixtures.**
  Reading them as research input is fine (same activity as a user
  reading them to form their own strategy); copying verbatim into
  `tests/fixtures/jaso/{pass,fail}/*.md` is not. Fixtures must be
  original synthesized prose with placeholder identifiers.

## Subscription path enforcement

`selfgraph doctor` is the canonical diagnostic. It reports:

- skill installation state at `~/.claude/skills/selfgraph/SKILL.md`
- whether `ANTHROPIC_API_KEY` is set vs `SELFGRAPH_ALLOW_API_KEY=1`
  opt-in
- vault path and Python version

CI exercises both paths: `ANTHROPIC_API_KEY=fake` should exit non-zero,
`unset` should exit zero.

## Resolved in v1.0 (formerly Open TBDs)

| Item | v1.0 status |
| --- | --- |
| Korean 자소서 fixtures (5 pass + 5 fail) | DONE — synthetic composites, research-based, under `tests/fixtures/jaso/{pass,fail}/`. |
| `render-jaso` calibration | DONE — research-based v1.0; 28-entry banned_phrases.json with HR-survey citations; named human reviewer awaited for v1.1 via `.github/ISSUE_TEMPLATE/korean_reviewer_onboarding.yml`. |
| `render-resume-en` rubric + prompts | DONE — `RUBRIC.md` (5 dimensions), `prompt-writer.md`, `prompt-reviewer.md`, `banned_phrases.json` (44 + 5 soft-overuse). |
| `render-resume-en` `banned_phrases.json` | DONE — cross-source confirmed across The Pragmatic Engineer, Lenny's, MIT CAPD, Harvard FAS, Yale OCS, Workology, Tealhq, ResumeWorded, IGotAnOffer, Toptal. |
| OSS infrastructure | DONE — `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`. |

## Future work (post v1.0, deferred to v1.1+)

| Item | Where to leave the result |
| --- | --- |
| `render-jaso` named human reviewer | `plugins/selfgraph/skills/selfgraph-render-jaso/reviewers.md` (v1.1) |
| `render-resume-en` 5 + 5 fixture set per persona | `tests/fixtures/resume-en/{pass,fail}/*.md` (v1.1) |
| `render-resume-en` named human reviewer (US tech recruiter / hiring manager) | `plugins/selfgraph/skills/selfgraph-render-resume-en/reviewers.md` (v1.1, new file) |
| `selfgraph migrate` | `selfgraph/commands/migrate.py` — deferred until first user lands; v1.0 is first public release so no v0.1 users exist yet. |
| v1.2 orchestration | Explicit 5-step render pipeline + parallel bulk-ingest dispatcher. See `docs/orchestration.md`. |
| v1.3 graph curator | Quarterly duplicate-merge agent. See `docs/orchestration.md`. |

These are also listed in `CHANGELOG.md` "Future work (post v1.0)".

## Verification quick reference

```bash
python3 -m selfgraph --version                      # version banner
python3 -c "from selfgraph.ontology import ENTITY_TYPES, EDGE_PREDICATES; print(len(ENTITY_TYPES), len(EDGE_PREDICATES))"   # 15 15
python3 -m pytest -q                                # 52+/52+ expected
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
5. Skim `CHANGELOG.md` "Future work (post v1.0)" for what's
   outstanding.
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
