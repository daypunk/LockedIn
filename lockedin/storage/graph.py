"""Derive graph.json from the markdown vault.

Walks vault/**/*.md, parses frontmatter, follows ``links:`` predicates,
emits a node-edge JSON document. Both the skill-only path and the CLI
accelerator path call this and must produce byte-identical output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lockedin.storage.notes import read_entity


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    if path.name == "EXPERIENCE.md":
        return False
    if "outputs" in path.parts:
        return False
    return "templates" not in path.parts


def derive_graph_json(vault: Path) -> dict[str, Any]:
    """Walk a vault and return a {nodes, edges} dict.

    Malformed notes are skipped silently here; ``lockedin validate`` is
    the surface that reports them. Missing / non-existent vault is treated
    as an empty graph rather than an error.
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    if not vault.exists():
        return {"nodes": nodes, "edges": edges}

    for path in sorted(vault.rglob("*.md")):
        if not _is_vault_note(path):
            continue
        try:
            entity = read_entity(path)
        except (ValueError, json.JSONDecodeError):
            continue

        nodes.append(
            {
                "id": entity.slug,
                "type": entity.type,
                "label": entity.title,
                "fields": entity.fields,
            }
        )

        for link in entity.links:
            if not isinstance(link, dict):
                continue
            edges.append(
                {
                    "source": entity.slug,
                    "predicate": link.get("predicate"),
                    "target": link.get("object"),
                    "weight": link.get("weight", 1.0),
                }
            )

    return {
        "nodes": sorted(nodes, key=lambda n: n["id"]),
        "edges": sorted(
            edges,
            key=lambda e: (
                e["source"],
                str(e["predicate"]),
                str(e["target"]),
            ),
        ),
    }


def write_graph_json(vault: Path, out_path: Path | None = None) -> Path:
    """Derive and write graph.json. Default destination: <vault>/outputs/graph.json."""
    if out_path is None:
        out_path = vault / "outputs" / "graph.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    graph = derive_graph_json(vault)
    payload = json.dumps(graph, indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(payload, encoding="utf-8")
    return out_path
