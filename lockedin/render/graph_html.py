"""Generate the interactive single-file graph.html.

Stub. The viz library is intentionally NOT chosen here — see
`docs/adr/0001-viz-library.md` for the open spike between vis-network,
force-graph, and cytoscape.js.
"""

from __future__ import annotations

from pathlib import Path


def render_html(graph_json: dict, out_path: Path) -> Path:
    raise NotImplementedError(
        "render.graph_html.render_html: implement after the viz-library spike "
        "in docs/adr/0001-viz-library.md picks a winner"
    )
