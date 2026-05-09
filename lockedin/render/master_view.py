"""Render the master ``EXPERIENCE.md`` view at the vault root.

The master view is a single human-readable markdown file at
``<vault>/EXPERIENCE.md`` that summarises every entity in the vault
grouped by type. The point is to give the user one place to scan
their whole vault without navigating per-type folders. The structure
is similar to how ``CLAUDE.md`` works in this repo: one canonical
file, regenerated in place whenever the underlying source changes.

Entities are listed under headings by type, sorted by ``updated``
date when available, then by slug. For each entity the line shows
the title, a one-line summary if a summary-shaped field is present,
the entity's slug, and the file path relative to the vault.

The rendering is deterministic. The skill calls
``refresh_master_view`` after any vault mutation; ``lockedin refresh``
exposes the same behaviour as a CLI command.
"""

from __future__ import annotations

from pathlib import Path

from lockedin.config import resolve_vault
from lockedin.ontology import ENTITY_SCHEMAS
from lockedin.storage.notes import read_entity

MASTER_FILENAME = "EXPERIENCE.md"

# Order entity types in a way a human reader expects to scan a career
# vault. Types not in this list go alphabetically at the end.
_PREFERRED_ORDER: tuple[str, ...] = (
    "person",
    "company",
    "role",
    "project",
    "achievement",
    "skill",
    "education",
    "certificate",
    "publication",
    "volunteer",
    "language",
    "topic",
    "decision",
    "meeting",
    "document",
)


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    parts = path.parts
    return "outputs" not in parts and "templates" not in parts


def _summary_field(fields: dict) -> str:
    """Pick the best one-line summary for an entity."""
    for key in ("summary", "headline", "description", "current_role", "title"):
        value = fields.get(key) if isinstance(fields, dict) else None
        if isinstance(value, str) and value.strip():
            line = value.strip().splitlines()[0]
            return line[:140] + ("…" if len(line) > 140 else "")
    return ""


def _label(entity_type: str, fields: dict, fallback_title: str) -> str:
    """Pick the user-readable label, preferring name/title/headline."""
    if isinstance(fields, dict):
        for key in ("name", "title", "headline", "institution", "language"):
            value = fields.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return fallback_title or entity_type


def _sort_key(entity) -> tuple:
    # Newest-updated first; fallback to slug.
    return (entity.updated or "", entity.slug)


def _ordered_types(seen: set[str]) -> list[str]:
    ordered = [t for t in _PREFERRED_ORDER if t in seen]
    extras = sorted(t for t in seen if t not in _PREFERRED_ORDER)
    return ordered + extras


def _render(vault: Path) -> str:
    """Build the master markdown text from the vault's current state."""
    by_type: dict[str, list] = {}
    total = 0
    for path in sorted(vault.rglob("*.md")):
        if not _is_vault_note(path):
            continue
        if path.name == MASTER_FILENAME:
            continue
        try:
            entity = read_entity(path)
        except Exception:  # noqa: BLE001 — surface via validate, not here
            continue
        by_type.setdefault(entity.type, []).append((entity, path))
        total += 1

    if not by_type:
        return (
            "# EXPERIENCE\n\n"
            f"_Master view of `{vault}`._\n\n"
            "Vault is empty. Start an interview with `/lockedin init` "
            "or drop a resume PDF into the chat to get going.\n"
        )

    out: list[str] = []
    out.append("# EXPERIENCE")
    out.append("")
    out.append(
        f"_Master view of `{vault}`. Auto-regenerated whenever the vault "
        f"changes. {total} entries across {len(by_type)} type(s)._"
    )
    out.append("")

    for entity_type in _ordered_types(set(by_type.keys())):
        spec = ENTITY_SCHEMAS.get(entity_type)
        type_label = entity_type.capitalize()
        type_subtitle = spec.description if spec and spec.description else ""

        entries = sorted(by_type[entity_type], key=lambda pair: _sort_key(pair[0]))

        out.append(f"## {type_label} ({len(entries)})")
        if type_subtitle:
            out.append(f"_{type_subtitle}_")
        out.append("")
        for entity, path in entries:
            label = _label(entity.type, entity.fields, entity.title)
            summary = _summary_field(entity.fields)
            rel = path.relative_to(vault).as_posix()
            line = f"- **{label}** `{entity.slug}` — [{rel}](./{rel})"
            if summary and summary != label:
                line += f"\n  {summary}"
            out.append(line)
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def refresh_master_view(vault_arg: str | Path | None = None) -> Path | None:
    """Regenerate ``<vault>/EXPERIENCE.md`` from the current vault state.

    Returns the path on success, ``None`` when the vault directory does
    not exist. Never raises; the master view is best-effort and a
    failure here must not block the underlying vault write.
    """
    vault = resolve_vault(str(vault_arg) if vault_arg else None)
    if not vault.exists():
        return None
    try:
        text = _render(vault)
        target = vault / MASTER_FILENAME
        target.write_text(text, encoding="utf-8")
        return target
    except Exception:  # noqa: BLE001 — best effort
        return None
