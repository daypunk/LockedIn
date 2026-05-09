"""Tiny stdlib-only template engine for renderer skills.

Only two constructs:
    {{ name }}                  variable
    {% for x in xs %}...{% endfor %}   for-loop

Kept intentionally minimal so the project can stay stdlib-only. Extend as
the renderers need more, but do **not** import Jinja2 — `pyproject.toml`
keeps `dependencies = []`.
"""

from __future__ import annotations

import re

_VAR = re.compile(r"\{\{\s*([a-zA-Z_][\w\.]*)\s*\}\}")


def render(template: str, context: dict) -> str:
    """Tiny renderer; intentionally limited to keep stdlib-only."""

    def lookup(path: str) -> str:
        node: object = context
        for part in path.split("."):
            node = node.get(part, "") if isinstance(node, dict) else getattr(node, part, "")
        return "" if node is None else str(node)

    return _VAR.sub(lambda m: lookup(m.group(1)), template)
