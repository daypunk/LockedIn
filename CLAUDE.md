# CLAUDE.md

Project-level instructions, loaded automatically by Claude Code when
working in this repo. Read this first if you are picking up the
project in a fresh session. The file is designed to be self-contained
enough that you can resume without prior conversation context.

## What this is

`lockedin` is a Claude Code plugin that organizes a user's experience
(career, meetings, projects, learning) into a typed markdown ontology
they own at `~/Documents/LockedIn/`, then renders artifacts (resume, cover
letter, graph viz) from the same vault. Two stores by design.
**Store A** is the user's input, structured into the vault.
**Store B** is `~/Documents/LockedIn/outputs/`, the artifacts rendered from A.

This repo holds the engine. It contains the plugin manifests, skill
files, CLI helpers, and tests. Users' actual data lives at
`~/Documents/LockedIn/`, never in this repo.

Tagline: *Personal experience knowledge graph for Claude Code. Zero
learning curve.* Distribution is the Claude Code plugin marketplace
(`/plugin marketplace add daypunk/lockedin`).

## Current state

| Layer | State |
| --- | --- |
| Plugin marketplace | manifests at `.claude-plugin/marketplace.json` and `plugins/lockedin/.claude-plugin/plugin.json` |
| One-time setup wizard | `/lockedin:setup` at `plugins/lockedin/commands/setup.md` (HUD wiring, Q&A language, vault path) |
| Ontology | **v0.2**. 15 entity types, 15 edge predicates, JSON Resume / Schema.org / FOAF aligned. Per-type field contracts and edge domain and range enforced by `lockedin validate`. See `lockedin/ontology/schema.py`. |
| Render skills | `lockedin` (main), `lockedin-render-jaso` (calibrated, 5 pass + 5 fail fixtures), `lockedin-render-resume-en` (calibrated, 3 personas). All under `plugins/lockedin/skills/`. |
| Render graph | Done. Vendored force-graph 1.51.4 UMD bundle (~178 KB) in `plugins/lockedin/scripts/vendor/force-graph.min.js`. Single-file interactive `graph.html` ~182 KB total. See `docs/adr/0001-viz-library.md`. |
| HUD | `lockedin X.Y.Z │ 5h:NN% · wk:NN% │ vault: Nn · Me`. Counts user turns from `~/.claude/projects/*/*.jsonl`. Color on by default. Same script in two places (`plugins/lockedin/scripts/hud.py` standalone, `lockedin/commands/hud.py` package). The standalone defers to the package when available. |
| Deterministic CLI | `install` (with `--setup-hud`, `--remove-hud`, lifecycle), `init --fixture FILE`, `ingest --dry-run`, `render graph`, `validate`, `doctor`, `template`, `hud`. |
| Skill-only commands | `init` (interactive), `ingest` (smart), `render jaso/resume`, `query`. Typed in plain shell, the CLI prints a redirect (exit 3) and points at Claude Code. |
| OSS infrastructure | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `.github/ISSUE_TEMPLATE/{bug_report, feature_request, korean_reviewer_onboarding, config}.yml`. |
| Tests | 52+ passing across import, ontology, storage round-trip, install lifecycle, doctor, validate v0.2, render graph, init from fixture, template, ingest dry-run, hud, plus non-LLM jaso fixture validation. |

## Repo layout

```
.claude-plugin/marketplace.json     ← marketplace catalog
.github/
├── ISSUE_TEMPLATE/                 ← bug, feature, Korean reviewer, config
└── workflows/ci.yml                ← lint, test, language policy, leakage scan
plugins/lockedin/                  ← the plugin itself
├── .claude-plugin/plugin.json
├── commands/setup.md               ← /lockedin:setup wizard
├── scripts/
│   ├── hud.py                      ← standalone HUD (no Python pkg required)
│   └── vendor/force-graph.min.js   ← vendored viz library
└── skills/
    ├── lockedin/                  ← main skill (SKILL/AGENTS/TOOLS.md)
    │   └── templates/career/questions.yaml
    ├── lockedin-render-jaso/      ← Korean cover letter (Korean OK in skill files)
    │   └── RUBRIC + prompts + banned_phrases + reviewers + research-notes
    └── lockedin-render-resume-en/ ← English resume (us-tech-senior, mid, pm-product)
        └── RUBRIC + prompts + banned_phrases + research-notes

lockedin/                          ← Python package (optional CLI accelerator)
├── cli.py · config.py · __main__.py · __init__.py
├── ontology/{__init__,schema}.py   ← 15 entity types, 15 edge predicates, v0.2
├── storage/{notes,graph}.py        ← markdown read/write, graph derivation
├── ingest/{interview,markdown,pdf,docx,text}.py
├── render/{_template,graph_html}.py
└── commands/{install,doctor,validate,init,ingest_dry,render_graph,template,hud}.py

docs/                               ← architecture, spec, mappings, guides
├── architecture.md · ontology-spec.md · ontology-mapping.md
├── orchestration.md · hud.md · cli.md
└── adr/0001-viz-library.md         ← ACCEPTED: vendored force-graph

tests/                              ← pytest suite + fixtures
├── test_smoke · test_storage_roundtrip · test_commands · test_hud · test_init_template_ingest
└── fixtures/jaso/{pass,fail}/      ← 5 pass + 5 fail synthetic golden fixtures (research-based)

examples/sample-vault.yaml          ← fixture seed for `lockedin init --fixture`
README.md · README.ko.md · CHANGELOG.md · CONTRIBUTING.md · CODE_OF_CONDUCT.md · LICENSE
```

## Working agreements

- **Never invent ontology data for users.** Notes get written from
  real user input or user-confirmed transformations only. Synthetic
  fixtures used for tests must be clearly labeled (`composite`,
  placeholder names like `SOME_COMPANY` or `GLOBAL_TECH`). Never use
  real persons, real companies, or quotes from real published 자소서.
- **The markdown is the contract.** If
  `lockedin/ontology/schema.py` changes, also update
  `docs/ontology-spec.md`, `docs/ontology-mapping.md`, and the
  renderer skills' SKILL.md.
- **stdlib-first Python.** `pyproject.toml` has `dependencies = []`.
  PDF (`pypdf`) and DOCX (`python-docx`) are optional extras.
- **English skills, polyglot output.** All files inside
  `plugins/lockedin/skills/` are English with one exception. The
  `lockedin-render-jaso/` directory is exempt from the
  language-policy lint because its domain is Korean output. Korean
  inline examples elsewhere belong inside fenced
  `<!-- ko-example -->...<!-- /ko-example -->` blocks.
- **Subscription, not API keys.** lockedin reasoning runs through
  Claude Code skills on the user's existing subscription. The Python
  CLI never calls the Anthropic API directly. `lockedin doctor`
  detects API key configuration and warns unless the user opts in via
  `LOCKEDIN_ALLOW_API_KEY=1`.
- **Two-turn writer/reviewer for renderers.** Writer turn drafts.
  Reviewer turn re-loads `RUBRIC.md` fresh and emits a JSON score.
  Same-context self-evaluation inflates scores by about one point.
  The split is load-bearing.
- **The user's vault is sacred.** Read freely. Write only through
  documented CLI commands (with their `--dry-run` flags) or with
  explicit user instruction.
- **README has language switcher** at top: `English | [한국어]` and
  the inverse.

## What to NEVER do

- **Never refactor `plugins/lockedin/skills/lockedin-render-jaso/`
  to remove Korean.** It is the one English-policy exempt skill. Its
  domain is Korean output.
- **Never write to `~/Documents/LockedIn/`** from tests or scripts unless
  pointed at by `LOCKEDIN_VAULT` to a temp dir. The user's real
  vault is theirs.
- **Never auto-modify `~/.claude/settings.json`** outside the
  documented `lockedin install --setup-hud` and `--remove-hud` flow.
  Setup is opt-in via the wizard. Silent statusLine writes break
  trust.
- **Never crash the HUD.** The statusLine command runs every few
  hundred ms. On any unexpected error the HUD must fall back to the
  bare label `lockedin` and exit 0.
- **Never copy real published 자소서 or resume text into fixtures.**
  Reading them as research input is fine, the same activity as a user
  reading them to form a strategy. Copying verbatim into
  `tests/fixtures/jaso/{pass,fail}/*.md` is not. Fixtures must be
  original synthesized prose with placeholder identifiers.

## Subscription path enforcement

`lockedin doctor` is the canonical diagnostic. It reports:

- skill installation state at `~/.claude/skills/lockedin/SKILL.md`
- whether `ANTHROPIC_API_KEY` is set, or `LOCKEDIN_ALLOW_API_KEY=1`
  opt-in is in effect
- vault path and Python version

CI exercises both paths. `ANTHROPIC_API_KEY=fake` should exit
non-zero. Unset should exit zero.

## Future work

See `CHANGELOG.md` "Future work" for the canonical list. Highlights:

- Q&A interview buildout (highest leverage)
- Quick-start path (PDF-first onboarding, demo vault loading)
- Automatic LOCKEDIN_REPORT.md, provenance tags, evidence_recall
  instrumentation
- Named human reviewer engagement for both render skills
- `lockedin migrate` command
- v1.2 orchestration and v1.3 graph curator

## Verification quick reference

```bash
python3 -m lockedin --version                      # version banner
python3 -c "from lockedin.ontology import ENTITY_TYPES, EDGE_PREDICATES; print(len(ENTITY_TYPES), len(EDGE_PREDICATES))"   # 15 15
python3 -m pytest -q                                # 52+ expected
python3 -m lockedin doctor                         # subscription/skill check
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin init --fixture examples/sample-vault.yaml
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin validate
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin render graph
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin hud
```

`tests/fixtures/sample-vault.yaml` and `examples/sample-vault.yaml`
are both authored to v0.2 schema (required fields per type). Use them
as shape references when authoring new fixtures.

## Resume protocol — fresh-session pickup

If you are a Claude session opened with no prior context:

1. Read this file (you are doing it).
2. Read `README.md` for the user-facing pitch and the install / use
   flow.
3. Read `docs/architecture.md` for the skill / CLI split.
4. Read `docs/ontology-spec.md` and `docs/ontology-mapping.md` for
   the data contract.
5. Skim `CHANGELOG.md` "Future work" for what is outstanding.
6. If working notes / spec / plan files exist locally at
   `.omc/specs/` and `.omc/plans/`, those are gitignored
   internal-only artifacts. Read them only if you need history that
   is not in this CLAUDE.md.
7. Before any significant change, run `pytest -q` to confirm the
   baseline is green.
8. If a change touches the ontology, update all four of:
   `lockedin/ontology/schema.py`, `docs/ontology-spec.md`,
   `docs/ontology-mapping.md`, and the renderer skills' SKILL.md
   that reference field shapes.
