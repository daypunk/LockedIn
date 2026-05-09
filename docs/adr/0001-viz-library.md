# ADR-0001: Graph viz library choice

**Status**: SUPERSEDED — render-graph removed in LockedIn 1.1.
**Date accepted**: 2026-05-01.
**Date superseded**: 2026-05-09.

## Original decision (now superseded)

Vendored `vasturiano/force-graph` v1.51.4 UMD minified bundle inline in
a generated `graph.html`. Chosen over `visjs/vis-network` and
`cytoscape/cytoscape.js` for its single-purpose force-directed default,
canvas rendering, and small bundle (~177 KB). Bundle lived at
`plugins/lockedin/scripts/vendor/force-graph.min.js`. Render path lived
at `lockedin/commands/render_graph.py`. Output was
`<vault>/outputs/graph.html`.

## Why superseded

User testing of LockedIn 1.0 surfaced that `graph.html` did not deliver
clear value to a personal vault user. The artifact's positioning was
ambiguous and its quality was not high enough to confidently ship as a
hero deliverable. The render-graph surface was removed in 1.1.

Specifically:

- The visualization is most compelling at hundreds of nodes; personal
  career vaults realistically land in the dozens.
- The single-file HTML is a fine technical achievement but does not
  answer "what do I do with this?" for a user looking at their own
  career data.
- LockedIn's load-bearing artifacts are the calibrated text outputs
  (Korean cover letter, English resume). The graph viz is a side show
  that risks anchoring the user's perception of LockedIn quality on a
  weak surface.

## Disposition

- `lockedin/commands/render_graph.py` deleted.
- `lockedin/render/graph_html.py` deleted.
- `plugins/lockedin/scripts/vendor/force-graph.min.js` deleted.
- `lockedin render graph` CLI subcommand removed.
- README, CHANGELOG, CLAUDE.md, docs/ all updated to reflect the
  removal.
- Tests: `test_render_graph_*` removed from `tests/test_commands.py`.

## Consequences

- The vault still has all the structure to support a future visual
  surface, should one be reintroduced under a different design.
- Repo size shrinks by ~180 KB.
- No follow-up library swap is needed; the question is whether a
  visual surface deserves to exist at all, not which library to use.

## If a visual surface returns

A new ADR should be written. The ADR should:

- Explain the user value the visual answers (which it could not in 1.0).
- Justify the form factor (single-file HTML vs in-Claude-Code text vs
  external link).
- Re-evaluate library candidates from scratch; the 2026-05 comparison
  in the original ADR is preserved in git history if needed.
