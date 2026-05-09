"""selfgraph experience — synthesize a denormalized "experience" view.

Walks the vault from a person entity, follows held_role_at, has_role,
works_on, produced, and uses_skill edges, and surfaces role with
overlapping projects, achievements, and skills as a single
time-bounded summary. No new edges are stored. The view is computed
on demand from the typed ontology.

Used by the renderer skills as a query helper, and callable directly
by power users for ad hoc inspection.
"""

from __future__ import annotations

import re
from pathlib import Path

from selfgraph.config import resolve_vault
from selfgraph.ontology import Entity
from selfgraph.storage.notes import read_entity

_DATE_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")


def _is_vault_note(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    parts = path.parts
    return "outputs" not in parts and "templates" not in parts


def _parse_iso_date(s: object) -> tuple[int, int, int] | None:
    """Parse a date string into (year, month, day). Defaults month and
    day to 1 when omitted. Returns None if unparseable or empty."""
    if not isinstance(s, str) or not s.strip():
        return None
    m = _DATE_RE.match(s.strip())
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2)) if m.group(2) else 1
    day = int(m.group(3)) if m.group(3) else 1
    return (year, month, day)


def _parse_time_range(
    s: str,
) -> tuple[tuple[int, int, int] | None, tuple[int, int, int] | None]:
    """Parse YYYY-MM/YYYY-MM or YYYY/YYYY into (start, end) tuples."""
    if "/" not in s:
        return None, None
    left, right = s.split("/", 1)
    return _parse_iso_date(left.strip()), _parse_iso_date(right.strip())


def _date_overlap(
    a_start: tuple[int, int, int] | None,
    a_end: tuple[int, int, int] | None,
    b_start: tuple[int, int, int] | None,
    b_end: tuple[int, int, int] | None,
) -> bool:
    """Two date ranges overlap if a_start <= b_end and a_end >= b_start.
    Missing endpoints are treated as open."""
    a_s = a_start or (0, 0, 0)
    a_e = a_end or (9999, 12, 31)
    b_s = b_start or (0, 0, 0)
    b_e = b_end or (9999, 12, 31)
    return a_s <= b_e and a_e >= b_s


def _entity_dates(
    entity: Entity,
) -> tuple[tuple[int, int, int] | None, tuple[int, int, int] | None]:
    """Get (start, end) date tuples from entity fields. Reads
    start_date / end_date / year, in that priority."""
    fields = entity.fields or {}
    start = _parse_iso_date(fields.get("start_date"))
    end = _parse_iso_date(fields.get("end_date"))
    if start is None and "year" in fields:
        try:
            year = int(fields["year"])
            start = (year, 1, 1)
            end = (year, 12, 31)
        except (TypeError, ValueError):
            pass
    return start, end


def _walk(vault: Path) -> dict[str, Entity]:
    """Load every vault entity into a slug -> Entity map."""
    by_slug: dict[str, Entity] = {}
    for path in sorted(vault.rglob("*.md")):
        if not _is_vault_note(path):
            continue
        try:
            ent = read_entity(path)
        except Exception:  # noqa: BLE001 — surface via validate, not here
            continue
        by_slug[ent.slug] = ent
    return by_slug


def _outgoing(entity: Entity, predicate: str) -> list[str]:
    """Slugs targeted by edges from this entity matching the predicate."""
    out: list[str] = []
    for link in entity.links or []:
        if isinstance(link, dict) and link.get("predicate") == predicate:
            tgt = link.get("object")
            if isinstance(tgt, str):
                out.append(tgt)
    return out


def _achievement_line(by_slug: dict[str, Entity], ach_slug: str) -> str | None:
    a = by_slug.get(ach_slug)
    if not a:
        return None
    head = a.fields.get("headline", a.title)
    metric = a.fields.get("metric") or ""
    delta = a.fields.get("delta") or ""
    if metric or delta:
        return f"- {head} ({metric} {delta})".replace("(  )", "").replace("( ", "(").rstrip()
    return f"- {head}"


def _skill_names(by_slug: dict[str, Entity], slugs: list[str]) -> list[str]:
    names: list[str] = []
    for s in slugs:
        ent = by_slug.get(s)
        if ent:
            name = ent.fields.get("name") or ent.title or s
            names.append(str(name))
    return names


def experience(
    person_slug: str,
    time_range: str | None = None,
    vault_arg: str | None = None,
) -> int:
    """Print a markdown experience view to stdout.

    Returns 0 on success, 1 if the vault is missing or the person is not
    found.
    """
    vault = resolve_vault(vault_arg)
    if not vault.exists():
        print(f"vault does not exist: {vault}")
        return 1

    by_slug = _walk(vault)
    person = by_slug.get(person_slug)
    if person is None or person.type != "person":
        print(f"person {person_slug!r} not found in {vault}.")
        return 1

    range_start, range_end = (None, None)
    if time_range:
        range_start, range_end = _parse_time_range(time_range)
        if range_start is None and range_end is None:
            print(f"could not parse --time-range {time_range!r} (expected YYYY-MM/YYYY-MM).")
            return 1

    # Roles: person held_role_at company; company has_role role.
    held_companies = _outgoing(person, "held_role_at")
    role_entities: list[Entity] = []
    for company_slug in held_companies:
        company = by_slug.get(company_slug)
        if not company:
            continue
        for role_slug in _outgoing(company, "has_role"):
            role = by_slug.get(role_slug)
            if role is not None and role.type == "role":
                role_entities.append(role)

    if time_range:
        role_entities = [
            r
            for r in role_entities
            if _date_overlap(*_entity_dates(r), range_start, range_end)
        ]

    # Projects: person works_on project; filter by date overlap if range given.
    project_slugs = _outgoing(person, "works_on")
    projects: list[Entity] = []
    for ps in project_slugs:
        proj = by_slug.get(ps)
        if proj is None or proj.type != "project":
            continue
        if time_range and not _date_overlap(*_entity_dates(proj), range_start, range_end):
            continue
        projects.append(proj)

    # Output
    person_name = person.fields.get("name") or person.title or person_slug
    print(f"# Experience: {person_name}")
    if time_range:
        print(f"\n_Time range: {time_range}_")

    if not role_entities and not projects:
        print(f"\nNo roles or projects found for {person_slug}.")
        return 0

    for role in role_entities:
        title = role.fields.get("title") or role.title
        start = role.fields.get("start_date") or ""
        end = role.fields.get("end_date") or "(current)"
        print(f"\n## {title}  ({start} — {end})")

        ach_lines = [
            line
            for line in (_achievement_line(by_slug, s) for s in _outgoing(role, "produced"))
            if line
        ]
        if ach_lines:
            print("\n### Achievements\n")
            for line in ach_lines:
                print(line)

        skills = _skill_names(by_slug, _outgoing(role, "uses_skill"))
        if skills:
            print(f"\n### Skills\n\n- {', '.join(skills)}")

    if projects:
        print("\n## Projects")
        for proj in projects:
            name = proj.fields.get("name") or proj.title
            start = proj.fields.get("start_date") or proj.fields.get("year") or ""
            end = proj.fields.get("end_date") or ""
            range_str = f"  ({start} — {end})" if (start or end) else ""
            print(f"\n### {name}{range_str}")

            ach_lines = [
                line
                for line in (_achievement_line(by_slug, s) for s in _outgoing(proj, "produced"))
                if line
            ]
            for line in ach_lines:
                print(line)

            skills = _skill_names(by_slug, _outgoing(proj, "uses_skill"))
            if skills:
                print(f"  Skills: {', '.join(skills)}")

    return 0
