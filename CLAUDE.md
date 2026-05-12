# CLAUDE.md

Project-level instructions, loaded automatically by Claude Code when
working in this repo. Read this first if you are picking up the
project in a fresh session. The file is designed to be self-contained
enough that you can resume without prior conversation context.

## What this is

LockedIn is a Claude Code plugin that organizes a user's experience
(career, meetings, projects, learning, decisions) into a typed
markdown ontology they own at `~/Documents/LockedIn/`, then renders
text artifacts (English resume, Korean cover letter) from the same
vault. Two stores by design.

- **Store A** is the user's input, structured into the vault under
  `~/Documents/LockedIn/experience/`.
- **Store B** is `~/Documents/LockedIn/outputs/`, the artifacts
  rendered from A.

This repo holds the engine. It contains the plugin manifests, skill
files, CLI helpers, and tests. Users' actual data lives at
`~/Documents/LockedIn/`, never in this repo.

Tagline: *Personal experience knowledge graph for Claude Code. Zero
learning curve.* Distribution is the Claude Code plugin marketplace
(`/plugin marketplace add daypunk/LockedIn`).

The lowercase identifier `lockedin` is used everywhere a machine
parses it (Python package, plugin name, slash command, env vars). The
brand display `LockedIn` is used in user-facing copy (README headers,
descriptions, sentences in prose).

## Current state

| Layer | State |
| --- | --- |
| Plugin marketplace | manifests at `.claude-plugin/marketplace.json` and `plugins/lockedin/.claude-plugin/plugin.json` |
| One-time setup wizard | `/lockedin:setup` at `plugins/lockedin/commands/setup.md` (HUD wiring, Q&A language, vault path) |
| Ontology | **v3**. 15 entity types, 15 edge predicates, JSON Resume / Schema.org / FOAF aligned. Per-type field contracts plus `aliases` (person, company) and `provenance` (every type). Edge domain and range enforced by `lockedin validate`. See `lockedin/ontology/schema.py`. |
| Render skills | `lockedin` (main), `lockedin-render-jaso` (calibrated, 5 pass + 5 fail fixtures), `lockedin-render-resume-en` (calibrated, 3 personas). All under `plugins/lockedin/skills/`. |
| HUD | `lockedin X.Y.Z │ 5h:NN% · wk:NN% │ experience: Nn · Me`. Pulls real utilization from Anthropic OAuth API, falls back to vault-only display when OAuth is unavailable. Same script in two places (`plugins/lockedin/scripts/hud.py` standalone, `lockedin/commands/hud.py` package). The standalone defers to the package when available. |
| Deterministic CLI | `install` (with `--setup-hud`, `--remove-hud`, lifecycle), `init --fixture FILE`, `ingest --dry-run`, `validate`, `migrate`, `experience`, `doctor`, `template`, `hud`. |
| Skill-only commands | `init` (interactive), `ingest` (smart), `render jaso/resume`, `query`. Typed in plain shell, the CLI prints a redirect (exit 3) and points at Claude Code. |
| OSS infrastructure | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `.github/ISSUE_TEMPLATE/{bug_report, feature_request, korean_reviewer_onboarding, config}.yml`. |
| Tests | 200+ passing across import, ontology, storage round-trip, install lifecycle, doctor, validate v3, init from fixture, template, ingest dry-run, ingest format parsers (pdf/docx/markdown/text), hud, interview resumability, render-interview and render-ideas calibration, README-promise lint. |

## Repo layout

```
.claude-plugin/marketplace.json     ← marketplace catalog
.github/
├── ISSUE_TEMPLATE/                 ← bug, feature, Korean reviewer, config
└── workflows/ci.yml                ← lint, test, language policy, leakage scan
plugins/lockedin/                   ← the plugin itself
├── .claude-plugin/plugin.json
├── commands/setup.md               ← /lockedin:setup wizard
├── scripts/
│   └── hud.py                      ← standalone HUD (no Python pkg required)
└── skills/
    ├── lockedin/                   ← main skill (SKILL/AGENTS/TOOLS.md)
    │   └── templates/experience/questions.yaml
    ├── lockedin-render-jaso/       ← Korean cover letter (Korean OK in skill files)
    │   └── RUBRIC + prompts + banned_phrases + reviewers + research-notes
    └── lockedin-render-resume-en/  ← English resume (10 personas in personas/)
        └── RUBRIC + prompts + banned_phrases + research-notes + personas/

lockedin/                           ← Python package (optional CLI accelerator)
├── cli.py · config.py · __main__.py · __init__.py
├── ontology/{__init__,schema}.py   ← 15 entity types, 15 edge predicates, v3
├── storage/{notes,graph}.py        ← markdown read/write, edge derivation
├── ingest/{interview,markdown,pdf,docx,text}.py
├── render/_template.py
├── hud/oauth_usage.py              ← Anthropic OAuth credential reader + caller
└── commands/{install,doctor,validate,init,ingest_dry,migrate,experience,template,hud}.py

docs/                               ← architecture, spec, mappings, guides
├── architecture.md · ontology-spec.md · ontology-mapping.md
└── orchestration.md · hud.md · cli.md

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
- **The markdown is the contract.** If `lockedin/ontology/schema.py`
  changes, also update `docs/ontology-spec.md`,
  `docs/ontology-mapping.md`, and the renderer skills' SKILL.md.
- **stdlib-first Python.** `pyproject.toml` has `dependencies = []`.
  PDF (`pypdf`), DOCX (`python-docx`), and YAML (`PyYAML`) are
  optional extras.
- **English skills, polyglot output.** All files inside
  `plugins/lockedin/skills/` are English with one exception. The
  `lockedin-render-jaso/` directory is exempt from the
  language-policy lint because its domain is Korean output. Korean
  inline examples elsewhere belong inside fenced
  `<!-- ko-example -->...<!-- /ko-example -->` blocks.
- **Subscription, not API keys.** LockedIn reasoning runs through
  Claude Code skills on the user's existing subscription. The Python
  CLI never calls the Anthropic API directly for reasoning. The HUD
  reads Anthropic OAuth utilization through the OAuth credential
  Claude Code already manages. `lockedin doctor` warns when
  `ANTHROPIC_API_KEY` is set unless the user opts in via
  `LOCKEDIN_ALLOW_API_KEY=1`.
- **AI-native solution.** Rubric calibration, banned-phrase corpora,
  and fixture generation go through cross-source AI research (Claude
  Code skill calls), not human domain-reviewer engagements. The
  two-turn writer/reviewer split with fresh `RUBRIC.md` reload is the
  load-bearing quality mechanism, not external sign-off. Renderer
  prompts and reviewer prompts are the contract; revising them is how
  calibration improves.
- **Two-turn writer/reviewer for renderers.** Writer turn drafts.
  Reviewer turn re-loads `RUBRIC.md` fresh and emits a JSON score.
  Same-context self-evaluation inflates scores by about one point.
  The split is load-bearing.
- **Resolve `[[type/slug]]` references at render time.** The writer
  turn quotes ontology slugs to ground its claims, but the final
  artifact shown to the user must replace them with natural-language
  labels. Raw slug notation in user-facing output is a quality bug.
- **One experience per paragraph in renderer output.** When a slot
  pulls in more than one experience, the writer must add an explicit
  transition sentence between them. Mixing two experiences in one
  paragraph creates reader cognitive load.
- **The user's vault is sacred.** Read freely. Write only through
  documented CLI commands (with their `--dry-run` flags) or with
  explicit user instruction.
- **README has language switcher** at top: `English | [한국어]` and
  the inverse.

## What to NEVER do

- **Never refactor `plugins/lockedin/skills/lockedin-render-jaso/` to
  remove Korean.** It is the one English-policy exempt skill. Its
  domain is Korean output.
- **Never write to `~/Documents/LockedIn/`** from tests or scripts
  unless pointed at by `LOCKEDIN_VAULT` to a temp dir. The user's
  real vault is theirs.
- **Never auto-modify `~/.claude/settings.json`** outside the
  documented `lockedin install --setup-hud` and `--remove-hud` flow.
  Setup is opt-in via the wizard. Silent statusLine writes break
  trust.
- **Never crash the HUD.** The statusLine command runs every few
  hundred ms. On any unexpected error the HUD must fall back to the
  bare label `lockedin` and exit 0.
- **Never copy real published 자소서 or resume text into fixtures.**
  Reading them as research input is fine, the same activity as a
  user reading them to form a strategy. Copying verbatim into
  `tests/fixtures/jaso/{pass,fail}/*.md` is not. Fixtures must be
  original synthesized prose with placeholder identifiers.

## Subscription path enforcement

`lockedin doctor` is the canonical diagnostic. It reports:

- skill installation state at `~/.claude/skills/lockedin/SKILL.md`
- whether `ANTHROPIC_API_KEY` is set, or `LOCKEDIN_ALLOW_API_KEY=1`
  opt-in is in effect
- vault path and Python version
- HUD OAuth credential availability per OS

CI exercises both paths. `ANTHROPIC_API_KEY=fake` should exit
non-zero. Unset should exit zero.

## Verification quick reference

```bash
python3 -m lockedin --version                      # version banner
python3 -c "from lockedin.ontology import ENTITY_TYPES, EDGE_PREDICATES, SCHEMA_VERSION; print(len(ENTITY_TYPES), len(EDGE_PREDICATES), SCHEMA_VERSION)"   # 15 15 3
python3 -m pytest -q                                # 200+ expected
python3 -m lockedin doctor                         # subscription/skill check
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin init --fixture examples/sample-vault.yaml
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin validate
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin migrate
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin experience sample-user
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin hud
```

`tests/fixtures/sample-vault.yaml` and `examples/sample-vault.yaml`
are both authored to schema v3 (required fields per type). Use them
as shape references when authoring new fixtures.

## Resume protocol — fresh-session pickup

If you are a Claude session opened with no prior context:

1. Read this file (you are doing it).
2. Read `README.md` for the user-facing pitch and the install / use
   flow.
3. Read `docs/architecture.md` for the skill / CLI split.
4. Read `docs/ontology-spec.md` and `docs/ontology-mapping.md` for
   the data contract.
5. Skim `CHANGELOG.md` for the most recent shipped release notes.
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
