"""lockedin render graph — produce graph.json and an interactive graph.html.

Pure-CLI utility. The interactive HTML uses the bundled ``force-graph``
UMD library (vendored under ``plugins/lockedin/scripts/vendor/``) so the
result is fully self-contained — opens offline in any browser, no CDN.

Library choice rationale lives in ``docs/adr/0001-viz-library.md``.
Bundle ~178 KB; total graph.html for a small career vault is well under
the 600 KB AC ceiling.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from lockedin.config import resolve_vault
from lockedin.storage.graph import write_graph_json

VENDOR_BUNDLE_NAME = "force-graph.min.js"


def _vendor_bundle() -> str:
    """Read the vendored force-graph UMD bundle.

    Returns the JS source as a string. Raises FileNotFoundError if the
    vendor bundle is missing — that's a build-time issue, surface it
    rather than silently falling back to a CDN URL.
    """
    here = Path(__file__).resolve()
    repo_root = here.parent.parent.parent
    vendor = repo_root / "plugins" / "lockedin" / "scripts" / "vendor" / VENDOR_BUNDLE_NAME
    if not vendor.exists():
        raise FileNotFoundError(
            f"vendored force-graph bundle missing at {vendor}; "
            f"reinstall the plugin or vendor it manually."
        )
    return vendor.read_text(encoding="utf-8")


def _interactive_html(graph: dict, bundle_js: str) -> str:
    """Wrap the bundle and graph data in a self-contained HTML page."""
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    # force-graph expects `links` with source/target; our graph_json uses
    # `edges` with source/predicate/target — map the keys here.
    links = [
        {
            "source": e.get("source"),
            "target": e.get("target"),
            "predicate": e.get("predicate"),
            "weight": e.get("weight", 1.0),
        }
        for e in edges
    ]
    data = {"nodes": nodes, "links": links}
    data_json = json.dumps(data, ensure_ascii=False)
    n_nodes = len(nodes)
    n_edges = len(edges)

    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        "  <title>lockedin — graph</title>\n"
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "  <style>\n"
        "    :root { color-scheme: light dark; }\n"
        "    html, body { margin: 0; height: 100%; font-family: system-ui, -apple-system, sans-serif; }\n"
        "    body { background: #0f1115; color: #d4d6db; overflow: hidden; }\n"
        "    #graph { width: 100vw; height: 100vh; }\n"
        "    #meta { position: fixed; top: 12px; left: 14px; background: rgba(15,17,21,0.78);\n"
        "            padding: 8px 12px; border-radius: 6px; font-size: 13px; line-height: 1.4;\n"
        "            backdrop-filter: blur(6px); border: 1px solid rgba(255,255,255,0.08); }\n"
        "    #meta strong { color: #8ab4ff; }\n"
        "    #help { position: fixed; bottom: 12px; right: 14px; font-size: 11px;\n"
        "            color: #6b7280; opacity: 0.8; }\n"
        "    .empty { display: flex; align-items: center; justify-content: center;\n"
        "             height: 100vh; color: #9ca3af; font-size: 14px; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        + (
            f'  <div id="meta"><strong>lockedin</strong> — {n_nodes} nodes · {n_edges} edges</div>\n'
            '  <div id="help">drag to pan · scroll to zoom · click a node to focus</div>\n'
            '  <div id="graph"></div>\n'
            if n_nodes > 0
            else '  <div class="empty">vault is empty — run `/lockedin init` to seed it.</div>\n'
        )
        + "  <script>\n"
        + bundle_js
        + "\n  </script>\n"
        + ("" if n_nodes == 0 else _init_script(data_json))
        + "</body>\n"
        "</html>\n"
    )


def _init_script(data_json: str) -> str:
    return (
        "  <script>\n"
        "    const data = " + data_json + ";\n"
        "    const el = document.getElementById('graph');\n"
        "    const graph = ForceGraph()(el)\n"
        "      .graphData(data)\n"
        "      .nodeId('id')\n"
        "      .nodeLabel(n => `<b>${escapeHtml(n.label || n.id)}</b><br><small>${n.type}</small>`)\n"
        "      .nodeAutoColorBy('type')\n"
        "      .nodeRelSize(6)\n"
        "      .linkSource('source')\n"
        "      .linkTarget('target')\n"
        "      .linkLabel(l => l.predicate || '')\n"
        "      .linkDirectionalArrowLength(4)\n"
        "      .linkDirectionalArrowRelPos(1)\n"
        "      .backgroundColor('#0f1115')\n"
        "      .onNodeClick(n => {\n"
        "        graph.centerAt(n.x, n.y, 600);\n"
        "        graph.zoom(2.4, 600);\n"
        "      });\n"
        "    function escapeHtml(s) {\n"
        "      return String(s).replace(/[&<>\"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));\n"
        "    }\n"
        "    const resize = () => graph.width(el.clientWidth).height(el.clientHeight);\n"
        "    window.addEventListener('resize', resize); resize();\n"
        "  </script>\n"
    )


def _placeholder_html(graph: dict) -> str:
    """Pure-text fallback — only used when force-graph bundle is missing."""
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    rows_n = "\n".join(
        f"      <tr><td>{html.escape(str(n.get('id', '')))}</td>"
        f"<td>{html.escape(str(n.get('type', '')))}</td>"
        f"<td>{html.escape(str(n.get('label', '')))}</td></tr>"
        for n in nodes
    )
    rows_e = "\n".join(
        f"      <tr><td>{html.escape(str(e.get('source', '')))}</td>"
        f"<td>{html.escape(str(e.get('predicate', '')))}</td>"
        f"<td>{html.escape(str(e.get('target', '')))}</td></tr>"
        for e in edges
    )
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head><meta charset="utf-8"><title>lockedin — graph (fallback)</title>\n'
        "<style>body{font:14px/1.5 system-ui,sans-serif;margin:2rem;max-width:960px}"
        "table{border-collapse:collapse;width:100%}th,td{padding:4px 8px;border-bottom:1px solid #eee;text-align:left}"
        "th{background:#fafafa;font-weight:600}.warn{background:#fff8d5;border:1px solid #e7d780;"
        "padding:.75rem 1rem;border-radius:4px}</style></head>\n<body>\n"
        f"  <h1>lockedin — graph</h1>\n"
        f'  <div class="warn">Vendored force-graph bundle missing — falling back to a plain table view. '
        "Reinstall the plugin to restore the interactive viz.</div>\n"
        f"  <p>{len(nodes)} nodes · {len(edges)} edges</p>\n"
        "  <h2>Nodes</h2>\n  <table><thead><tr><th>id</th><th>type</th><th>label</th></tr></thead>\n"
        f"  <tbody>\n{rows_n}\n  </tbody></table>\n"
        "  <h2>Edges</h2>\n  <table><thead><tr><th>source</th><th>predicate</th><th>target</th></tr></thead>\n"
        f"  <tbody>\n{rows_e}\n  </tbody></table>\n"
        "</body>\n</html>\n"
    )


def run_render_graph(vault_arg: str | None = None) -> int:
    vault = resolve_vault(vault_arg)
    if not vault.exists():
        print(f"vault does not exist: {vault}")
        return 1
    json_path = write_graph_json(vault)
    graph = json.loads(json_path.read_text(encoding="utf-8"))
    html_path = vault / "outputs" / "graph.html"

    try:
        bundle_js = _vendor_bundle()
        html_text = _interactive_html(graph, bundle_js)
    except FileNotFoundError as exc:
        print(f"warning: {exc}")
        html_text = _placeholder_html(graph)

    html_path.write_text(html_text, encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {html_path} ({html_path.stat().st_size:,} bytes)")
    return 0
