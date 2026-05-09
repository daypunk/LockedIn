"""lockedin init --non-interactive --fixture FILE — deterministic vault seed.

Pure-CLI path. The interactive Q&A interview lives in the skill (host AI
does the question generation and answer interpretation). This entry point
exists so CI smoke tests, scripted setups, and the skill-only fallback
can deterministically materialize a vault from a YAML fixture.
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path
from typing import Any

from lockedin.config import resolve_vault
from lockedin.ontology import Entity
from lockedin.storage.notes import write_entity


def _import_yaml():
    try:
        import yaml  # type: ignore[import-not-found]

        return yaml
    except ImportError:
        print(
            "lockedin init --fixture requires PyYAML. Install one of:\n"
            "  uv pip install PyYAML\n"
            '  pip install "lockedin[yaml]"\n'
            '  pip install "lockedin[all]"',
            file=sys.stderr,
        )
        return None


def _stringify_dates(value: Any) -> Any:
    """Recursively coerce ``datetime.date`` / ``datetime.datetime`` to ISO
    strings so the YAML-parsed fixture round-trips through our JSON-flavored
    frontmatter writer."""
    if isinstance(value, _dt.datetime):
        return value.replace(microsecond=0).isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _stringify_dates(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_stringify_dates(v) for v in value]
    return value


def _coerce_entity(raw: dict[str, Any]) -> Entity:
    required = ("type", "title", "slug")
    for r in required:
        if r not in raw:
            raise ValueError(f"fixture entity missing {r!r}: {raw!r}")
    return Entity(
        type=str(raw["type"]),
        title=str(raw["title"]),
        slug=str(raw["slug"]),
        body=str(raw.get("body") or ""),
        fields=_stringify_dates(dict(raw.get("fields") or {})),
        links=_stringify_dates(list(raw.get("links") or [])),
        created=raw.get("created"),
        updated=raw.get("updated"),
    )


def init_from_fixture(
    fixture_path: str,
    vault_arg: str | None = None,
    *,
    lang: str = "en",
) -> int:
    """Read a YAML fixture and write each entity into the vault.

    Fixture shape::

        schema_version: 1
        template: experience
        entities:
          - type: person
            title: Sample User
            slug: sample-user
            fields: {current_role: PM}
            links:
              - {predicate: works_on, object: project-a}
          - type: project
            title: Project A
            slug: project-a
    """
    del lang  # reserved; the locale of the prompts is irrelevant for fixtures
    yaml = _import_yaml()
    if yaml is None:
        return 1

    fixture = Path(fixture_path).expanduser()
    if not fixture.exists():
        print(f"fixture not found: {fixture}", file=sys.stderr)
        return 1

    try:
        data = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover
        print(f"failed to parse fixture: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print(
            f"fixture must be a YAML mapping at top level, got {type(data).__name__}",
            file=sys.stderr,
        )
        return 1

    template = str(data.get("template") or "experience")
    entities_raw = data.get("entities") or []
    if not isinstance(entities_raw, list):
        print("fixture 'entities' must be a list", file=sys.stderr)
        return 1

    vault = resolve_vault(vault_arg)
    vault.mkdir(parents=True, exist_ok=True)

    written = 0
    for raw in entities_raw:
        if not isinstance(raw, dict):
            print(f"  skipped non-dict entry: {raw!r}", file=sys.stderr)
            continue
        try:
            entity = _coerce_entity(raw)
        except (ValueError, KeyError) as exc:
            print(f"  skipped malformed entity: {exc}", file=sys.stderr)
            continue
        write_entity(vault, entity, domain=template)
        written += 1

    print(f"wrote {written} entities to {vault} (template={template})")
    return 0 if written else 1
