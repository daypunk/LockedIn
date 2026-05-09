# Architecture diagram — design reference

This file is the structural reference for the architecture image
shown in the README. The user designs the final image; this document
captures the layout and the labels so the design and the code stay
in lockstep. Each ASCII block below corresponds to a panel the
designer can compose freely.

## Big picture: three layers

Three time-scoped layers, left to right.

```
   INPUT                       KNOWLEDGE                    OUTPUT
  ─────────                   ──────────                   ─────────
  one-shot                    accumulating                 session-shaped


  Q&A interview          ┐                                  ┐
  resume PDF / DOCX     ─┤                                  ├ English resume
  meeting note          ─┤      ~/Documents/LockedIn/      ─┤
  free-form text        ─┤      experience/                 ├ 한국어 자소서
                         │      ├ person/                   │
                         │      ├ company/                  ┘
                         │      ├ role/
                         │      ├ project/
                         │      ├ skill/
                         │      ├ achievement/
                         │      └ ... (15 entity types)
                         │
                         │      EXPERIENCE.md
                         │      (auto-refreshed master view)
                         ┘
```

Notes for the designer:

- The three layer headers (INPUT / KNOWLEDGE / OUTPUT) are
  load-bearing labels. The under-label sub-text (one-shot,
  accumulating, session-shaped) communicates the time scope.
- The middle column is the only persistent surface the user owns.
  Both INPUT and OUTPUT are time-bounded. This asymmetry is the
  product's main idea, so visual weight should sit on KNOWLEDGE.
- The 15 entity types do not need to be enumerated in the final
  image. Five or six is enough for the eye; the rest can be implied
  with an ellipsis.
- `EXPERIENCE.md` deserves its own callout inside KNOWLEDGE because
  it is the user-facing master view; the per-type folders are how
  the engine reads, but the master file is what the user opens.

## Inside KNOWLEDGE: typed ontology

Inside the middle column, every entity is one file. Entities are
linked by typed predicates with a domain and a range constraint. The
schema rejects mismatched edges.

```
  entity                          entity
  ┌────────────────┐              ┌────────────────┐
  │ person         │              │ project        │
  │ frontmatter:   │              │ frontmatter:   │
  │   type, slug,  │  ──works_on→ │   name,        │
  │   name,        │              │   highlights,  │
  │   aliases,     │              │   provenance   │
  │   summary,     │              │                │
  │   provenance   │              │                │
  └────────────────┘              └────────────────┘
       │                                ↑
       │                                │
       └─ held_role_at →  [company]  ───┘
                                  has_role
                                  ↓
                              [role]
```

Notes for the designer:

- Every box is one markdown file. Every arrow is one entry in a
  note's `links:` frontmatter. The arrow direction matters because
  edges are typed.
- Field names inside the boxes are real. `provenance` is a system
  field that records where the record came from (interview,
  pdf_ingest, docx_ingest, user_edit, inferred). `aliases` is a
  list of alternative names so free-form ingest matches.

## Render loop: writer turn and reviewer turn

When the user asks for an artifact, two Claude turns run back to
back. They are deliberately separated so the second turn evaluates
the first turn's output against a freshly loaded rubric.

```
   writer turn                             reviewer turn
  ┌─────────────────┐                     ┌──────────────────────┐
  │ query KNOWLEDGE │                     │ load RUBRIC.md fresh │
  │ draft artifact  │   ──── output ────→ │ score 5 dimensions   │
  │ cite slugs      │                     │ verify cited slugs   │
  │                 │                     │ check banned phrases │
  └─────────────────┘                     └──────────────────────┘
                                                     │
                                                     ↓
                                       ┌────────────────────────┐
                                       │ JSON score             │
                                       │ revisions_required?    │
                                       │ → at most one revision │
                                       └────────────────────────┘
                                                     │
                                                     ↓
                                            slug → natural language
                                            resolution
                                                     │
                                                     ↓
                                            saved under
                                            ~/Documents/LockedIn/outputs/
```

Notes for the designer:

- "RUBRIC.md re-loaded fresh" is the hard guard that prevents
  self-evaluation bias. It is worth visual emphasis because
  collapsing it back into one turn inflates self-scores by about a
  point in practice.
- The slug-to-natural-language step happens between the reviewer
  approval and the saved artifact. The user never sees raw
  `[[type/slug]]` notation in their final output.

## HUD: ambient status line

The Claude Code status line shows three segments. The middle one is
the real Anthropic OAuth utilization, not a heuristic.

```
  lockedin 1.x.x  │  5h:NN%  ·  wk:NN%  │  experience: Nn · Me
  └─ version ─┘     └─ Anthropic OAuth  └─ vault state
                       utilization         (entity count, edge count)
```

Notes for the designer:

- The OAuth utilization is read through the same OAuth credential
  Claude Code already manages. macOS reads from Keychain; Linux and
  Windows from `~/.claude/.credentials.json`. The fallback when the
  OAuth call fails is a simpler heuristic; the user sees a coherent
  number either way.
- The `experience:` label was previously `vault:`; the rename
  reflects the broader umbrella the product covers.

## Footnotes the designer might want

- The vault path lives at `~/Documents/LockedIn/`, intentionally
  outside any dot-prefixed home directory so the user can find it
  in Finder or Explorer without enabling hidden files.
- LockedIn is distributed as a Claude Code plugin. There is no
  daemon, no separate desktop app, no GUI of its own. The
  interaction surface is whatever Claude Code provides plus the
  vault directory the user already understands.
- The five-dimension rubrics differ between renderers but the
  rubric → reviewer → score flow is the same shape across both.
  The designer can show one rubric explicitly and imply the other.

## What the final image should communicate

A new visitor should walk away knowing:

1. There are three time-scoped layers and the middle one is theirs.
2. The middle is a typed graph, not a flat note pile.
3. Outputs are queries against the middle, regenerable any time.
4. Quality comes from a separated writer-reviewer loop, not from a
   single AI call.
5. They run this on their existing Claude Code subscription with no
   extra key or service to manage.

Pick whichever subset of the panels above carries those five points
in the visual language you choose.
