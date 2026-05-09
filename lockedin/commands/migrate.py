"""lockedin migrate — upgrade vault frontmatter to the latest schema version.

The migration is forward-only and idempotent. A vault that already conforms
to the latest schema is a no-op. The current target is SCHEMA_VERSION 3:

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


def migrate(vault_arg: str | None = None, dry_run: bool = False) -> int:
    """Walk the vault and apply schema migrations in place.

    Returns 0 on success, 1 if the vault does not exist.
    """
    vault = resolve_vault(vault_arg)
    if not vault.exists():
        print(f"vault does not exist: {vault}")
        return 1

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
                write_entity(vault, entity)

    label = "would upgrade" if dry_run else "upgraded"
    print(f"schema migration target v{SCHEMA_VERSION}: {label} {upgraded} of {inspected} entities in {vault}.")
    if skipped:
        print(f"  ({skipped} unreadable notes skipped, run `lockedin validate` to surface them)")
    return 0
