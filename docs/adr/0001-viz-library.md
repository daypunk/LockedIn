# ADR-0001: Graph viz library choice

**Status**: ACCEPTED — vendored vasturiano/force-graph.
**Date**: 2026-05-01

## Context

lockedin's interactive `graph.html` is the highest-leverage visual asset
for launch. Library choice is functionally irreversible after v1 ships
(URLs, embed shapes, bundled JS, all baked in).

Three libraries were on the table:

| Library | Repo size | Stars | Last push | License | Note |
| --- | --- | --- | --- | --- | --- |
| **vasturiano/force-graph** | 2.7 MB | 2.0 k | 2026-04-16 | MIT | force-directed default, canvas, single-purpose |
| visjs/vis-network | 1.5 GB | 3.6 k | 2026-05-01 | Apache-2.0 | feature-rich, SVG, heavier API surface |
| cytoscape/cytoscape.js | 85 MB | 11 k | 2026-04-29 | MIT | graph-theory algorithms, plugin ecosystem |

(Earlier drafts called vis-network "stale" — that was based on outdated
2023 data. As of 2026-05 all three see active commits.)

## Decision

**Vendor `vasturiano/force-graph` v1.51.4 UMD minified bundle inline in
the generated `graph.html`.** Three reasons:

1. **Single-purpose match.** We need force-directed layout with
   click-to-focus, label-on-hover, drag-to-pan, scroll-to-zoom. We do
   not need hierarchical layouts, BFS, PageRank, or 100+ plugin
   ecosystem. force-graph is the smallest library that does exactly
   what's needed.
2. **Canvas rendering** keeps DOM cost low at 100+ nodes (career graphs
   for ~5-year-experience PMs land in that range), which matters more
   than vis-network's SVG ergonomics for our screenshot-and-share usage.
3. **Bundle size**. force-graph UMD min is **177 KB** (verified at
   integration time); the resulting `graph.html` for a small career
   vault lands at ~182 KB total — well under the 600 KB AC ceiling.

## Implementation

The bundle lives at:

```
plugins/lockedin/scripts/vendor/force-graph.min.js
```

`lockedin/commands/render_graph.py` reads this file at render time and
embeds the JS inline in a `<script>` block, followed by an
initialization script that wires:

- `graphData(...)` from `outputs/graph.json` (mapped: `edges` →
  force-graph's `links` schema).
- `nodeAutoColorBy('type')` so each ontology entity type gets its own
  color cluster.
- `nodeLabel` shows entity title + type on hover (HTML-escaped).
- `linkLabel` shows the edge predicate.
- `linkDirectionalArrowLength(4)` to make edges directional visually.
- `onNodeClick` — center-and-zoom on the clicked node.

Empty-vault path: render a friendly notice instead of the canvas.
Missing-bundle path: fall back to a plain HTML table view (a build-time
issue, but the script doesn't crash).

## Consequences

- The HTML opens fully offline — no CDN, no network.
- Bundle file (`force-graph.min.js`) is committed to the repo and
  shipped with the plugin. Repo size grows by ~180 KB; acceptable.
- Library lock-in: switching later requires editing
  `_interactive_html()` / `_init_script()` in `render_graph.py` and
  swapping the vendor bundle. Not free, but not dramatic either.
- License: MIT — compatible with lockedin's MIT.

## Update protocol

This ADR is ACCEPTED. Trigger a follow-up ADR (e.g.
`0002-viz-library-update.md`) if any of these happen:

- Bundle exceeds 600 KB (after, say, force-graph adds dependencies).
- A user-reported FPS regression on a 100+-node vault that we cannot
  fix with options.
- A materially better library appears (e.g., a tiny WebGL renderer with
  similar API, < 50 KB).

## Verification

- `lockedin render graph` on a 10-node fixture vault → 182 KB
  graph.html, opens cleanly in Chrome/Firefox/Safari.
- `lockedin render graph` on an empty vault → smaller HTML with the
  "vault is empty" notice; bundle still ships so the page loads.
- Test: `tests/test_commands.py::test_render_graph_emits_json_and_html`
  asserts the bundle marker is present and the file is < 600 KB.
