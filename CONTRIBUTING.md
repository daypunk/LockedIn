# Contributing to LockedIn

Thanks for considering a contribution. LockedIn is a Claude Code
plugin that organizes personal experience into a typed markdown vault
and renders text artifacts (English resume, Korean cover letter) from
the same source. The project is small and intentionally so. Authoring
quality matters more than feature breadth.

This guide covers what we accept, how to set up locally, and the
specific contribution paths that need outside help right now.

## Project structure

If you are new to the codebase, read these in order:

1. [`CLAUDE.md`](./CLAUDE.md) — project bootstrap (current state,
   working agreements, repo layout, what to never do).
2. [`README.md`](./README.md) / [`README.ko.md`](./README.ko.md) —
   user-facing pitch and install flow.
3. [`docs/architecture.md`](./docs/architecture.md) — skill / CLI
   split, execution model.
4. [`docs/ontology-spec.md`](./docs/ontology-spec.md) — frontmatter
   contract for the markdown vault.

## What we accept

| Welcome | Maybe (open an issue first) | Not now |
| --- | --- | --- |
| Bug fixes with a regression test | New entity types in the ontology | New renderer skills before the existing ones are calibrated |
| New `render-resume-en` persona spec (under `personas/`) | A new ingest source (e.g., another file format) | API-key-based execution paths (we are subscription-only) |
| Documentation improvements | New CLI subcommands | Telemetry / phone-home features |
| Skill prompt refinements (with rubric scores before/after) | Translation of skills into other languages | Anything that writes outside `~/Documents/LockedIn/` and the documented CLI flow |
| Golden fixtures (with the rules below) | New banned-phrase entries (with ≥2 source URLs) | Auto-modification of `~/.claude/settings.json` outside the wizard |

## Development setup

Requirements: Python 3.10+, [`uv`](https://github.com/astral-sh/uv) or
plain `pip`, and a working Claude Code installation if you want to
exercise the skill paths.

```bash
git clone https://github.com/daypunk/lockedin.git
cd lockedin
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev,pdf,docx]"
pytest -q                  # baseline must be green before you start
python3 -m lockedin doctor # checks runtime / skill / API-key state
```

`pyproject.toml` keeps runtime dependencies empty (`dependencies = []`).
PDF (`pypdf`) and DOCX (`python-docx`) are optional extras. Please do
not introduce new runtime dependencies without an issue discussion.

## Running tests

```bash
pytest -q                                                       # full suite
pytest tests/test_validate.py -q                                # one file
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin init --fixture examples/sample-vault.yaml
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin validate
LOCKEDIN_VAULT=/tmp/sg python3 -m lockedin migrate
```

CI gates:

- **lint**: `ruff check lockedin tests`.
- **language policy**: skill meta files must be English except the
  `lockedin-render-jaso/` directory (its domain is Korean output).
  CJK outside fenced `<!-- ko-example -->...<!-- /ko-example -->`
  blocks fails the lint. Multilingual switcher links
  (`[한국어](README.ko.md)` etc.) are allowed.
- **tests**: `pytest -q` on macOS-latest and ubuntu-latest, Python
  3.12.
- **leakage scan**: tracked files must not reference internal-only
  terms. The `.github/workflows/ci.yml` enforces this.

## Contributing a fixture (any render skill)

Golden fixtures sharpen the calibrated rubrics. Each render skill
has its own pass / fail set:

- `tests/fixtures/jaso/{pass,fail}/` — Korean cover letter
- `tests/fixtures/resume-en/{pass,fail}/` — English resume
- `tests/fixtures/interview/{pass,fail}/` — interview answer
- `tests/fixtures/ideas/{pass,fail}/` — project ideas

Template: see [`tests/fixtures/jaso/TEMPLATE.md`](./tests/fixtures/jaso/TEMPLATE.md)
for the frontmatter shape. The other skills mirror it.

Rules:

- **No real names, companies, schools, or projects.** Fixtures are
  synthetic. If you base a fixture on your own experience, anonymize
  every identifier (replace company / school / colleague names with
  generic placeholders or fictional substitutes).
- **No verbatim copying from public sources.** You may read industry
  sites or published guides to internalize patterns; the fixture body
  itself must be original prose written by you.
- **`pass/` fixtures** must satisfy the rubric pass criterion (every
  dimension ≥ 4, zero high-severity banned-phrase hits). Frontmatter
  declares `fixture_kind: pass` and `expected_score`.
- **`fail/` fixtures** isolate ONE failure mode each. Frontmatter
  declares `fixture_kind: fail` and either `banned_phrases_hit: [...]`
  or `expected_revisions_required: true` for structural failures.
- **Coverage target for jaso**: pass fixtures should span 5 Korean
  market segments — IT conglomerate, foreign-tech (Korea offices of
  multinationals), finance, manufacturing, startup. See existing
  filenames in `tests/fixtures/jaso/pass/` for the canonical slugs.
- **Body length**: ≤ 1500 characters per fixture.

Open a PR with the fixture file. The calibration tests
(`tests/test_*_calibration.py`) automatically verify schema and
banned-phrase containment.

## Adding or refining a renderer skill

Skills live in `plugins/lockedin/skills/<skill-name>/`. Each skill
needs:

- `SKILL.md` — frontmatter description triggers natural-language
  activation. Keep it short and specific.
- `RUBRIC.md` — scoring contract with 5 dimensions and 0–5 score
  bands.
- `prompt-writer.md` — writer turn instruction.
- `prompt-reviewer.md` — reviewer turn instruction (loaded in a
  separate Claude turn; same-context self-evaluation inflates scores
  by ~1 point).
- `banned_phrases.json` — regex list of weak / vague / templated
  phrases.
- `research-notes.md` — citations with URL + ISO date + 2-sentence
  gloss per source.

Open an issue first if you are proposing a new renderer. The two
text renderers (Korean cover letter, English resume) form an
intentionally narrow surface, and the bar to add a third is high.

## Language policy

All files inside `plugins/lockedin/skills/` are English **except**
the `lockedin-render-jaso/` directory, which is exempt because its
domain is Korean output. Korean inline examples elsewhere belong in
fenced `<!-- ko-example -->...<!-- /ko-example -->` blocks. The CI
language-policy lint enforces this.

## Commit style

- One change per commit when possible. The history before v1.0 was
  a single amended commit; from v1.0 forward, atomic commits are
  welcome.
- Subject line: imperative present tense, ≤ 72 chars
  (`Add render-resume-en banned phrase: detail-oriented`).
- Body: explain *why* the change matters; the diff already shows
  *what*.
- Do not skip pre-commit hooks (`--no-verify`). If a hook fails,
  fix the underlying issue.

## Pull requests

- Reference the related issue (`Fixes #N` or `Refs #N`).
- Include test changes when behavior changes.
- For ontology / schema changes, also update `docs/ontology-spec.md`
  and `docs/ontology-mapping.md` and the renderer skills' SKILL.md if
  they reference field shapes (per `CLAUDE.md` working agreement).
- For renderer prompt / rubric changes, run the golden fixture set
  before / after and include the score deltas in the PR description.

## Code of conduct

This project adheres to the
[Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)
v2.1. By participating, you agree to uphold its terms. Report
incidents privately to the maintainer at
[business@daypunk.com](mailto:business@daypunk.com).

## Asking for help

Open a [Discussion](https://github.com/daypunk/lockedin/discussions)
for questions and ideas. Open an [Issue](https://github.com/daypunk/lockedin/issues/new/choose)
for bugs and concrete proposals. The maintainer reads everything but
may take a few days to respond.
