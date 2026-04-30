"""selfgraph validate — check vault notes against the ontology schema.

Pure-CLI utility. Exit 0 on conformant vault, 1 otherwise.

Three layers of validation, surfaced as separate error messages:

1. **Frontmatter shape** — type/title/slug present and valid; slugs unique.
2. **Field contracts** — every required field present, every value's type
   plausible (not strict parse, but rejects obvious mismatches).
3. **Edge constraints** — predicate recognized; source/target types are in
   the predicate's domain/range; targets resolve to existing nodes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from selfgraph.config import resolve_vault
from selfgraph.ontology import (
    EDGE_SCHEMAS,
    ENTITY_SCHEMAS,
    Entity,
    FieldSpec,
)
from selfgraph.storage.notes import read_entity

_DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
_YEAR_RE = re.compile(r"^\d{4}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_URL_RE = re.compile(r"^https?://", re.I)


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    parts = path.parts
    return "outputs" not in parts and "templates" not in parts


def _check_field_value(value: Any, spec: FieldSpec) -> str | None:
    """Return an error message if value doesn't fit spec, else None."""
    if value is None or value == "":
        return None  # absence is handled by required-check elsewhere
    t = spec.type
    if t in ("string", "text"):
        return None if isinstance(value, str) else f"expected string, got {type(value).__name__}"
    if t == "url":
        if not isinstance(value, str):
            return f"expected url string, got {type(value).__name__}"
        return None if _URL_RE.match(value) else "url must start with http:// or https://"
    if t == "email":
        if not isinstance(value, str):
            return f"expected email string, got {type(value).__name__}"
        return None if _EMAIL_RE.match(value) else "email looks malformed"
    if t == "date":
        if not isinstance(value, str):
            return f"expected ISO date string (YYYY-MM-DD or YYYY-MM), got {type(value).__name__}"
        return None if _DATE_RE.match(value) else "date must be YYYY-MM-DD or YYYY-MM"
    if t == "year":
        if isinstance(value, int):
            return None if 1800 < value < 2200 else "year out of plausible range"
        if isinstance(value, str):
            return None if _YEAR_RE.match(value) else "year must be a 4-digit number"
        return f"expected year, got {type(value).__name__}"
    if t == "int":
        return None if isinstance(value, int) and not isinstance(value, bool) else "expected int"
    if t == "float":
        return None if isinstance(value, (int, float)) and not isinstance(value, bool) else "expected float"
    if t == "bool":
        return None if isinstance(value, bool) else "expected boolean"
    if t == "list[string]":
        if not isinstance(value, list):
            return "expected list of strings"
        bad = [i for i, v in enumerate(value) if not isinstance(v, str)]
        return None if not bad else f"list contains non-string at indices {bad}"
    return None  # unknown type — be permissive


def _check_entity_fields(path: Path, entity: Entity, errors: list[str]) -> None:
    spec = ENTITY_SCHEMAS.get(entity.type)
    if spec is None:
        return  # unknown type already reported as a type-level error
    fields = entity.fields or {}
    for name, fspec in spec.fields.items():
        present = name in fields and fields[name] not in (None, "")
        if fspec.required and not present:
            errors.append(f"{path}: required field {name!r} missing for {entity.type}")
            continue
        if present:
            err = _check_field_value(fields[name], fspec)
            if err:
                errors.append(f"{path}: field {name!r} ({fspec.type}): {err}")


def _check_edges(
    path: Path,
    entity: Entity,
    slug_to_type: dict[str, str],
    errors: list[str],
) -> None:
    for link in entity.links:
        if not isinstance(link, dict):
            errors.append(f"{path}: malformed link entry: {link!r}")
            continue
        pred = link.get("predicate")
        target = link.get("object")
        spec = EDGE_SCHEMAS.get(pred) if isinstance(pred, str) else None
        if spec is None:
            errors.append(f"{path}: unknown predicate {pred!r}")
            continue
        if entity.type not in spec.domain:
            errors.append(
                f"{path}: predicate {pred!r} not allowed from source type "
                f"{entity.type!r} (allowed: {list(spec.domain)})"
            )
        if isinstance(target, str) and target in slug_to_type:
            target_type = slug_to_type[target]
            if target_type not in spec.range:
                errors.append(
                    f"{path}: predicate {pred!r} target {target!r} is type "
                    f"{target_type!r}, not in allowed range {list(spec.range)}"
                )
        elif isinstance(target, str):
            errors.append(f"{path}: dangling reference to slug {target!r}")
        else:
            errors.append(f"{path}: link target missing or non-string: {target!r}")


def validate(vault_arg: str | None = None) -> int:
    vault = resolve_vault(vault_arg)
    if not vault.exists():
        print(f"vault does not exist: {vault}")
        return 1

    errors: list[str] = []
    slug_to_type: dict[str, str] = {}
    slug_to_path: dict[str, Path] = {}
    entities_by_path: dict[Path, Entity] = {}

    # First pass — parse + collect slugs
    for path in sorted(vault.rglob("*.md")):
        if not _is_vault_note(path):
            continue
        try:
            entity = read_entity(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: parse failed: {exc}")
            continue
        entities_by_path[path] = entity

        if entity.type not in ENTITY_SCHEMAS:
            errors.append(f"{path}: unknown type {entity.type!r}")
        if not str(entity.title).strip():
            errors.append(f"{path}: empty title")
        if entity.slug in slug_to_path:
            errors.append(
                f"{path}: duplicate slug {entity.slug!r} (also at {slug_to_path[entity.slug]})"
            )
        else:
            slug_to_path[entity.slug] = path
            slug_to_type[entity.slug] = entity.type

    # Second pass — fields + edges (needs slug_to_type for range check)
    for path, entity in entities_by_path.items():
        _check_entity_fields(path, entity, errors)
        _check_edges(path, entity, slug_to_type, errors)

    if errors:
        print(f"{len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {len(slug_to_path)} entities valid in {vault}.")
    return 0
