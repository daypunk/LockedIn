# selfgraph tool catalog

Canonical calls each sub-role issues. Two layers exist:

* **Skill layer (this directory)** — drives all flows that need an LLM
  (interactive Q&A, render writer/reviewer turns, smart ingest, query).
  Lives in the host AI's loop.
* **CLI utility layer** — deterministic helpers the skill calls via Bash,
  and that the user can also call directly from any terminal. Two install
  paths exist: the **CLI accelerator path** (`selfgraph` on PATH via
  `uv tool install`) and the **skill-only path** (vendored single-file
  Python helpers, invoked via `python3 -c`). Both produce byte-identical
  output on shared fixtures.

## Where each call runs

Skill-only (LLM in the loop, Claude Code session required):

| Sub-role | Inside Claude Code | Notes |
| --- | --- | --- |
| Interviewer | `/selfgraph init [--lang en\|ko]` | one question at a time; user-facing |
| Ingester | `/selfgraph ingest <path> [--domain DOMAIN]` | resolves ambiguities by asking |
| Renderer (jaso) | `/selfgraph render jaso [--company C] [--question Q] [--self-evaluate]` | two-turn writer/reviewer |
| Renderer (resume) | `/selfgraph render resume [--target T] [--self-evaluate]` | two-turn writer/reviewer |
| Renderer (portfolio) | `/selfgraph render portfolio` | single-turn |
| Query | `/selfgraph query "<text>"` | natural-language graph query |

If the user types these as bare `selfgraph ...` in a plain terminal, the
CLI prints a redirect message and exits with code 3.

Pure CLI (deterministic, no LLM, run anywhere):

| Sub-role | Call | Notes |
| --- | --- | --- |
| Interviewer (seed) | `selfgraph init --non-interactive --fixture FILE [--vault PATH]` | YAML fixture → markdown vault, no LLM |
| Ingester (preview) | `selfgraph ingest <path> --dry-run [--domain DOMAIN]` | parse .pdf/.docx/.md/.txt and emit diff only |
| Renderer (graph) | `selfgraph render graph` | static HTML generation from `graph.json` |
| GraphCurator | `selfgraph validate [--vault PATH]` | exits 0 on conformant vault, 1 with offending path on first violation |
| Installer | `selfgraph install [--auto-register \| --upgrade \| --uninstall \| --check] [--target PATH] [--force]` | hash-aware; `--upgrade` refuses to clobber user-modified files without `--force` |
| Doctor | `selfgraph doctor` | prints subscription / API-key / skill-install state; exits non-zero on misconfig |
| Template | `selfgraph template {list,add,remove} [name]` | manage ontology templates |

## Skill-only path (no `pip install`)

When the user has not run `uv tool install selfgraph`, the skill calls the
vendored helpers directly:

```
python3 ~/.claude/skills/selfgraph/helpers/init.py --fixture ... --vault ...
python3 ~/.claude/skills/selfgraph/helpers/render_graph.py --vault ... --out ...
```

The helpers MUST stay in lockstep with `selfgraph/cli.py` — CI runs the
parity test on every PR. If you add a new subcommand to `cli.py`, also add
a helper script for the same behavior in `selfgraph/skill/helpers/`.

## Tool selection cheat sheet

- The user has `selfgraph` on PATH and a vault → use the CLI path.
- Fresh user, just installed via `git clone`, no Python package → use the
  helper path.
- The user already started a session and asked "what's selfgraph doing?" →
  point them at `selfgraph/skill/SKILL.md`.

## Model tier guidance

`selfgraph` works on the user's Claude Code subscription, so model
selection matters for token spend on their plan. Default tiers:

| Task | Tier |
| --- | --- |
| Q&A interview question generation | haiku |
| Ingest diff classification | haiku |
| Render jaso (writer turn) | sonnet |
| Render jaso (reviewer turn) | sonnet (reviewer) |
| Render resume_en | sonnet |
| Cultural review of jaso (deep cases) | opus |
| Graph derivation / validate | haiku |

Bump to opus only when the user explicitly asks for "best quality" or the
template requires nuanced judgment (e.g. cultural fit reviewer pass for
`render-jaso`).
