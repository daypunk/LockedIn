# AGENTS.md — lockedin-audit agent orchestration

Describes the agent roles this skill orchestrates and the turn
sequencing for each mode.

## Agents

### Orchestrator

Role: the outermost Claude context. Receives the user's invocation,
detects entry point (drive-by vs. post-ingest), presents the 4-option
menu when in post-ingest mode, routes to the correct mode, and
assembles the final report.

Responsibilities:
- Run `lockedin ingest <path> --dry-run` to extract text for
  drive-by audits.
- Detect document type (English resume or Korean cover letter (jaso)).
- Present the mode-selection menu in post-ingest mode.
- Pass source text and context to the scorer and/or refiner.
- Collect the reviewer's JSON score and render the final report.
- In Mode 3, store the pre-refinement JSON score before launching
  the refiner, then pass it to the reviewer for delta computation.

The orchestrator does not score and does not refine. It only routes
and assembles.

### Scorer (writer turn)

Runs the writer-turn scoring pass (`prompt-scorer.md`). Produces
a markdown score narrative quoting specific evidence lines. Does
not emit final JSON scores. This is the first of the two-turn pair.

Constraints:
- Must load the correct rubric via RUBRIC.md routing before writing.
- Must quote at least one verbatim line per dimension.
- Must surface issues concretely (specific line + specific fix).
- Must not emit JSON.

### Reviewer (reviewer turn)

Runs in a SEPARATE Claude context from the scorer
(`prompt-reviewer.md`). Loads RUBRIC.md fresh from disk, then loads
the referenced render-skill rubric. Scores independently against the
five dimensions. Emits strict JSON. This is the second of the
two-turn pair.

Constraints:
- Must load rubric fresh (hard guard in prompt-reviewer.md).
- Must score independently; cannot use the scorer's preliminary
  scores as input to its own scoring.
- Must output only the JSON object with no surrounding prose.

### Refiner (writer turn)

Runs only for Mode 2 and Mode 3 (`prompt-refiner.md`). Proposes
targeted changes in three classes (metric normalization, action verb
replacement, highlight restructuring). Surfaces missing-data notes
when the source lacks the data needed for a stronger version of a
line.

Constraints:
- Never invents facts. Missing data -> ask, not fabricate.
- Presents every change individually for user yes/no confirmation.
- Does not write to the vault without final explicit confirmation.
- Limited to 10 proposed changes per pass; prioritized by class.

## Turn sequencing by mode

### Mode 1 — Score only

```
Orchestrator
  -> Scorer (writer turn, prompt-scorer.md)
     [source text + doc_type + context]
  -> Reviewer (separate Claude context, prompt-reviewer.md)
     [scorer narrative + source text + rubric path]
  <- JSON score
Orchestrator assembles markdown report
```

### Mode 2 — Refine only

```
Orchestrator
  -> Refiner (prompt-refiner.md)
     [source text + doc_type]
  <- diff blocks + notes (interactive)
User approves/rejects each change
Refiner emits approved revision plan
  (drive-by: revised document text)
  (post-ingest: vault update plan + final confirmation)
```

### Mode 3 — Refine then Score

```
Orchestrator
  -> Scorer (writer turn, prompt-scorer.md) -- PRE-REFINEMENT
     [source text + doc_type + context]
  -> Reviewer (separate Claude context, prompt-reviewer.md)
     [scorer narrative + source text + rubric path]
  <- pre_refinement JSON score (stored by orchestrator)

  -> Refiner (prompt-refiner.md)
     [source text + doc_type]
  <- diff blocks + notes (interactive)
User approves/rejects each change
Refiner emits approved revision plan + revised text

  -> Scorer (writer turn) -- POST-REFINEMENT
     [refined text + doc_type + context]
  -> Reviewer (separate Claude context, prompt-reviewer.md)
     [scorer narrative + refined text + rubric path + pre_refinement scores]
  <- post-refinement JSON score (with pre_refinement key for delta)

Orchestrator assembles final report with delta table
```

## Context isolation guarantee

The writer turns (Scorer, Refiner) and the reviewer turns share NO
context. The reviewer does not have access to the scorer's preliminary
scores when forming its own scores. This isolation is the load-bearing
mechanism that prevents same-context self-evaluation inflation.

In practice with Claude Code, this means:
- The orchestrator collects the scorer's output.
- The orchestrator opens a new Claude turn / subagent for the
  reviewer.
- The reviewer receives only: the source text, the rubric file paths,
  and the doc_type. It does NOT receive the scorer's narrative or
  preliminary scores.
