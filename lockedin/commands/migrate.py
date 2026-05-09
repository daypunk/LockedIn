"""lockedin migrate — upgrade a vault to the latest layout and schema.

Forward-only and idempotent. A vault that already conforms to the latest
layout and schema is a no-op.

The current target is LockedIn 1.1, schema v3:

- Top-level template directory ``career/`` is renamed to ``experience/``
  (the umbrella covers meetings, decisions, learning, and side projects,
  not only career history). The rename is in-place and atomic from the
  filesystem's perspective.
- Every entity gains a ``provenance`` field with default ``inferred`` if
  the field is missing.
- ``person`` and ``company`` entities gain ``aliases: []`` if missing.

Older fields are never removed. Migrations always preserve user data.
"""

from __future__ import annotations

from pathlib import Path

from lockedin.config import resolve_vault
from lockedin.ontology import SCHEMA_VERSION
from lockedin.storage.notes import read_entity, write_entity


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    parts = path.parts
    return "outputs" not in parts and "templates" not in parts


def _rename_career_to_experience(vault: Path, dry_run: bool) -> int:
    """If <vault>/career/ exists, rename to <vault>/experience/.

    Returns 1 when a rename was performed (or would be performed in
    dry-run), 0 otherwise. Refuses to overwrite when both already exist;
    user must resolve that conflict manually.
    """
    src = vault / "career"
    dst = vault / "experience"
    if not src.exists() or not src.is_dir():
        return 0
    if dst.exists():
        print(
            "warning: both 'career/' and 'experience/' exist in the vault. "
            "Refusing to merge automatically. Move contents manually then re-run migrate."
        )
        return 0
    if dry_run:
        print(f"would rename {src} → {dst}")
        return 1
    src.rename(dst)
    print(f"renamed {src} → {dst}")
    return 1


def migrate(vault_arg: str | None = None, dry_run: bool = False) -> int:
    """Walk the vault and apply layout and schema migrations in place.

    Returns 0 on success, 1 if the vault does not exist.
    """
    vault = resolve_vault(vault_arg)
    if not vault.exists():
        print(f"vault does not exist: {vault}")
        return 1

    # Layout migration: career/ → experience/ if applicable.
    _rename_career_to_experience(vault, dry_run)

    upgraded = 0
    skipped = 0
    inspected = 0

    for path in sorted(vault.rglob("*.md")):
        if not _is_vault_note(path):
            continue
        inspected += 1
        try:
            entity = read_entity(path)
        except Exception:  # noqa: BLE001 — skip malformed notes; validate reports them
            skipped += 1
            continue

        changed = False

        # v3 migration: add provenance if missing.
        if "provenance" not in entity.fields:
            entity.fields["provenance"] = "inferred"
            changed = True

        # v3 migration: add aliases for person and company if missing.
        if entity.type in ("person", "company") and "aliases" not in entity.fields:
            entity.fields["aliases"] = []
            changed = True

        if changed:
            upgraded += 1
            if not dry_run:
                # Determine the domain from the entity's current path so we
                # write back to the same template folder rather than the
                # default. Path shape: <vault>/<domain>/<type>/<slug>.md
                rel = path.relative_to(vault)
                domain = rel.parts[0] if len(rel.parts) >= 3 else "experience"
                write_entity(vault, entity, domain=domain)

    label = "would upgrade" if dry_run else "upgraded"
    print(
        f"schema migration target v{SCHEMA_VERSION}: "
        f"{label} {upgraded} of {inspected} entities in {vault}."
    )
    if skipped:
        print(
            f"  ({skipped} unreadable notes skipped, run `lockedin validate` to surface them)"
        )
    return 0
