"""Resolve `[[type/slug]]` references in renderer output to natural-language labels.

Renderer writer turns are required to cite ontology entries by slug so the
reviewer turn can verify provenance. The slug notation is internal grammar
and must NOT reach the user's final artifact. This module reads the vault,
builds a slug-to-label map, and replaces `[[type/slug]]` tokens with
natural-language equivalents in the locale of the artifact.

Two locales:
- ``en``: prefer ``name`` / ``title`` / ``headline`` field. Plain English.
- ``ko``: prefer ``name`` / ``title`` / ``headline`` field, but fall back to
  the natural-language phrase the user wrote in the entity body if present.
  Korean output is sensitive to particle attachment, so this module emits
  the bare label and lets the writer turn handle particles.

The function never raises. If a slug does not resolve, the original
``[[type/slug]]`` token is left in place so QA surfaces the miss.
"""

from __future__ import annotations

import re
from pathlib import Path

from lockedin.config import resolve_vault
from lockedin.storage.notes import read_entity

_SLUG_TOKEN_RE = re.compile(r"\[\[(?P<type>[a-z_]+)/(?P<slug>[a-z0-9][a-z0-9\-_]*)\]\]")


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    parts = path.parts
    return "outputs" not in parts and "templates" not in parts


def _build_slug_map(vault: Path) -> dict[str, str]:
    """Walk the vault and build slug -> human label."""
    out: dict[str, str] = {}
    for path in sorted(vault.rglob("*.md")):
        if not _is_vault_note(path):
            continue
        try:
            ent = read_entity(path)
        except Exception:  # noqa: BLE001 — surface via validate, not here
            continue
        label = (
            ent.fields.get("name")
            or ent.fields.get("title")
            or ent.fields.get("headline")
            or ent.fields.get("institution")
            or ent.title
            or ent.slug
        )
        out[ent.slug] = str(label)
    return out


def resolve(text: str, vault: Path | str | None = None) -> str:
    """Replace ``[[type/slug]]`` tokens with the entity's natural-language label.

    Unresolved tokens are left as-is. The function is total: it never raises
    on missing or malformed vault.
    """
    vault_path = Path(vault).expanduser() if vault else resolve_vault(None)
    if not vault_path.exists():
        return text

    slug_map = _build_slug_map(vault_path)

    def _swap(match: re.Match[str]) -> str:
        slug = match.group("slug")
        return slug_map.get(slug, match.group(0))

    return _SLUG_TOKEN_RE.sub(_swap, text)


def resolve_file(path: Path, vault: Path | str | None = None) -> int:
    """In-place resolution of slug tokens in a rendered artifact.

    Returns the number of tokens replaced. Files that do not exist are a
    no-op and return 0.
    """
    if not path.exists():
        return 0
    original = path.read_text(encoding="utf-8")
    resolved = resolve(original, vault)
    if resolved == original:
        return 0
    path.write_text(resolved, encoding="utf-8")
    # Best-effort count of replacements.
    return len(_SLUG_TOKEN_RE.findall(original)) - len(_SLUG_TOKEN_RE.findall(resolved))
