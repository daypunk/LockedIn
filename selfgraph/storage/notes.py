"""Read and write Obsidian-compatible markdown notes.

The frontmatter format is a deterministic, JSON-flavored YAML subset:

    ---
    type: person
    title: Sample User
    slug: sample-user
    created: 2026-04-30T10:00:00Z
    updated: 2026-04-30T10:00:00Z
    fields: {"current_role": "PM"}
    links: [{"predicate": "works_on", "object": "project-a", "weight": 1.0}]
    ---
    <free-form markdown body>

Round-trip invariant: ``read_entity(p)`` followed immediately by
``write_entity(vault, entity)`` produces a file whose bytes match the
original. The skill-only Python helper and the CLI both rely on this.

stdlib-only (we control the format we write and parse the same format
back; a hand-edit in Obsidian that stays within this subset still works).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from selfgraph.ontology import Entity

FRONTMATTER_DELIM = "---"

_FRONTMATTER_RE = re.compile(
    r"\A---\n(?P<header>.*?)\n---\n(?P<body>.*)\Z",
    re.DOTALL,
)

_KNOWN_KEYS = ("type", "title", "slug", "created", "updated", "fields", "links")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _needs_quoting(s: str) -> bool:
    if s == "":
        return True
    if s[0] in "-?":
        return True
    return bool(re.search(r"[:\[\]{},&*#?|<>=!%@`\n\"']", s))


def _format_value(value: Any) -> str:
    """Render a frontmatter value in our JSON-flavored YAML subset."""
    if isinstance(value, str):
        if _needs_quoting(value):
            return json.dumps(value, ensure_ascii=False)
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):  # noqa: UP038 — keep tuple for Python 3.8 fallback
        return json.dumps(value)
    # dict / list → JSON flow-style (valid YAML too)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _parse_value(text: str) -> Any:
    s = text.strip()
    if s == "":
        return ""
    if s[0] in "\"[{":
        return json.loads(s)
    if s in ("true", "false"):
        return s == "true"
    if s == "null":
        return None
    if re.match(r"^-?\d", s):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass
    return s


def vault_path_for(vault: Path, entity: Entity, *, domain: str = "career") -> Path:
    """Return the canonical disk path for an entity inside a vault."""
    return vault / domain / entity.type / f"{entity.slug}.md"


def _serialize(entity: Entity) -> str:
    lines = [
        FRONTMATTER_DELIM,
        f"type: {_format_value(entity.type)}",
        f"title: {_format_value(entity.title)}",
        f"slug: {_format_value(entity.slug)}",
        f"created: {entity.created}",
        f"updated: {entity.updated}",
        f"fields: {_format_value(entity.fields)}",
        f"links: {_format_value(entity.links)}",
        FRONTMATTER_DELIM,
    ]
    body = entity.body or ""
    if body and not body.endswith("\n"):
        body += "\n"
    return "\n".join(lines) + "\n" + body


def write_entity(vault: Path, entity: Entity, *, domain: str = "career") -> Path:
    """Write entity to its canonical path inside the vault.

    Mutates ``entity.created`` / ``entity.updated`` only when they were
    ``None`` so that a read → write cycle stays byte-identical.
    """
    if entity.created is None:
        entity.created = _now_iso()
    if entity.updated is None:
        entity.updated = entity.created
    path = vault_path_for(vault, entity, domain=domain)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_serialize(entity), encoding="utf-8")
    return path


def read_entity(path: Path) -> Entity:
    """Read entity from a markdown file with our frontmatter."""
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: missing or malformed --- frontmatter ---")
    fm: dict[str, Any] = {}
    for line in match.group("header").split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        if key in _KNOWN_KEYS:
            fm[key] = _parse_value(val)
    for required in ("type", "title", "slug"):
        if required not in fm:
            raise ValueError(f"{path}: frontmatter missing required key {required!r}")
    return Entity(
        type=str(fm["type"]),
        title=str(fm["title"]),
        slug=str(fm["slug"]),
        body=match.group("body"),
        fields=fm.get("fields") or {},
        links=fm.get("links") or [],
        created=fm.get("created"),
        updated=fm.get("updated"),
    )
