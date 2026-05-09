"""Canonical ontology schema for lockedin (v0.2).

Aligned with JSON Resume / Schema.org / FOAF where it makes sense — see
``docs/ontology-mapping.md`` for the cross-walk. The design goal is
"professional but practical": typed contracts and edge constraints that
the AI can follow when filling the vault, while staying markdown-
authorable for users who prefer to edit by hand.

Three primitives:

- ``ENTITY_SCHEMAS[type]`` → an :class:`EntitySpec` describing the
  required and optional fields, the field types, and external-vocab
  aliases.
- ``EDGE_SCHEMAS[predicate]`` → an :class:`EdgeSpec` describing the
  allowed source/target types, the inverse predicate (if any), and
  whether the edge can carry temporal bounds.
- ``SCHEMA_VERSION`` → bumped on breaking changes; surfaced via
  ``lockedin validate`` so vaults pinned to an older version can be
  migrated explicitly.

The dataclasses :class:`Entity` and :class:`Edge` enforce the simplest
contract — that ``type`` / ``predicate`` are recognized values. Field-
level and edge domain/range validation lives in
``lockedin/commands/validate.py`` so authoring stays cheap (you can
build a partial Entity in code) while the vault on disk stays clean.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Field type system
# ---------------------------------------------------------------------------

FieldType = Literal[
    "string",        # short identifier or label
    "text",          # multi-sentence free text
    "url",           # URL string
    "email",         # email string
    "date",          # ISO-8601 date (YYYY-MM-DD or YYYY-MM)
    "year",          # 4-digit year
    "int",           # integer
    "float",         # float
    "bool",          # boolean
    "list[string]",  # list of strings
]


@dataclass(frozen=True)
class FieldSpec:
    """Contract for a single entity field."""

    type: FieldType
    description: str = ""
    required: bool = False


@dataclass(frozen=True)
class EntitySpec:
    """Contract for an entity type."""

    type: str
    description: str
    fields: dict[str, FieldSpec]
    aliases: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Entity schemas
# ---------------------------------------------------------------------------
# Keep this dict the single source of truth for "what fields an entity has".
# `lockedin/commands/validate.py` reads it; renderers query it; tests fix
# against it.

ENTITY_SCHEMAS: dict[str, EntitySpec] = {
    "person": EntitySpec(
        type="person",
        description="An individual. Typically the user, but can reference others.",
        fields={
            "name": FieldSpec("string", "Full name", required=True),
            "aliases": FieldSpec(
                "list[string]",
                "Alternative names this person is known by (e.g., Jim, 제인). Used by free-form ingest matching.",
            ),
            "current_role": FieldSpec("string", "One-sentence role summary"),
            "email": FieldSpec("email", "Contact email"),
            "based_in": FieldSpec("string", "City or region"),
            "summary": FieldSpec("text", "Multi-sentence summary"),
        },
        aliases=("foaf:Person", "schema:Person", "jsonresume:basics"),
    ),
    "company": EntitySpec(
        type="company",
        description="An employer, school, client, or other organization.",
        fields={
            "name": FieldSpec("string", "Company name", required=True),
            "aliases": FieldSpec(
                "list[string]",
                "Alternative names this organization is known by (acronyms, romanizations, brand variations).",
            ),
            "industry": FieldSpec("string", "Industry tag"),
            "employees": FieldSpec("int", "Approximate headcount"),
            "url": FieldSpec("url", "Website"),
            "description": FieldSpec("text"),
        },
        aliases=("foaf:Organization", "schema:Organization"),
    ),
    "role": EntitySpec(
        type="role",
        description="A position held at a company; carries start/end dates.",
        fields={
            "title": FieldSpec("string", "Job title", required=True),
            "start_date": FieldSpec("date", "ISO date the role started", required=True),
            "end_date": FieldSpec("date", "Omit while currently held"),
            "level": FieldSpec("string", "junior / mid / senior / lead / etc."),
            "summary": FieldSpec("text"),
            "highlights": FieldSpec("list[string]", "Bulleted highlights"),
        },
        aliases=("schema:Occupation", "jsonresume:work"),
    ),
    "project": EntitySpec(
        type="project",
        description="A body of work — work, side, OSS, or study.",
        fields={
            "name": FieldSpec("string", "Project name", required=True),
            "year": FieldSpec("year"),
            "start_date": FieldSpec("date"),
            "end_date": FieldSpec("date"),
            "url": FieldSpec("url"),
            "description": FieldSpec("text"),
            "keywords": FieldSpec("list[string]"),
            "highlights": FieldSpec("list[string]"),
        },
        aliases=("schema:CreativeWork", "jsonresume:projects"),
    ),
    "achievement": EntitySpec(
        type="achievement",
        description="A quantified result, typically attached to a role or project.",
        fields={
            "headline": FieldSpec("string", "One-line achievement summary", required=True),
            "metric": FieldSpec("string", "What was measured"),
            "delta": FieldSpec("string", "How it changed (e.g., +30%, -2 weeks)"),
            "timeframe": FieldSpec("string", "When (e.g., 2024-Q3)"),
            "evidence": FieldSpec("text"),
        },
        aliases=("schema:Award", "jsonresume:awards"),
    ),
    "skill": EntitySpec(
        type="skill",
        description="A technical or soft skill.",
        fields={
            "name": FieldSpec("string", required=True),
            "level": FieldSpec("string", "beginner / intermediate / advanced / expert"),
            "keywords": FieldSpec("list[string]"),
        },
        aliases=("schema:DefinedTerm", "jsonresume:skills"),
    ),
    "education": EntitySpec(
        type="education",
        description="A degree, course, or credential.",
        fields={
            "institution": FieldSpec("string", required=True),
            "area": FieldSpec("string", "Field of study"),
            "study_type": FieldSpec("string", "Bachelor / Master / Course"),
            "start_date": FieldSpec("date"),
            "end_date": FieldSpec("date"),
            "score": FieldSpec("string", "GPA or grade"),
            "courses": FieldSpec("list[string]"),
        },
        aliases=("schema:EducationalOccupationalCredential", "jsonresume:education"),
    ),
    "certificate": EntitySpec(
        type="certificate",
        description="A professional certification or license.",
        fields={
            "name": FieldSpec("string", required=True),
            "issuer": FieldSpec("string"),
            "date": FieldSpec("date"),
            "url": FieldSpec("url"),
        },
        aliases=("jsonresume:certificates",),
    ),
    "publication": EntitySpec(
        type="publication",
        description="A paper, article, talk, or other published work.",
        fields={
            "name": FieldSpec("string", required=True),
            "publisher": FieldSpec("string"),
            "release_date": FieldSpec("date"),
            "url": FieldSpec("url"),
            "summary": FieldSpec("text"),
        },
        aliases=("schema:CreativeWork", "jsonresume:publications"),
    ),
    "volunteer": EntitySpec(
        type="volunteer",
        description="A volunteer role at an organization.",
        fields={
            "organization": FieldSpec("string", required=True),
            "position": FieldSpec("string"),
            "start_date": FieldSpec("date"),
            "end_date": FieldSpec("date"),
            "summary": FieldSpec("text"),
            "highlights": FieldSpec("list[string]"),
        },
        aliases=("jsonresume:volunteer",),
    ),
    "language": EntitySpec(
        type="language",
        description="A spoken or written language proficiency.",
        fields={
            "language": FieldSpec("string", required=True),
            "fluency": FieldSpec("string", "native / fluent / professional / conversational / beginner"),
        },
        aliases=("jsonresume:languages",),
    ),
    "document": EntitySpec(
        type="document",
        description="An ingested source file — provenance for derived nodes.",
        fields={
            "filename": FieldSpec("string", required=True),
            "format": FieldSpec("string", "pdf / docx / md / txt"),
            "ingested_at": FieldSpec("date"),
            "source_path": FieldSpec("string"),
        },
        aliases=("schema:DigitalDocument",),
    ),
    "meeting": EntitySpec(
        type="meeting",
        description="A meeting note.",
        fields={
            "title": FieldSpec("string", required=True),
            "date": FieldSpec("date", required=True),
            "duration_minutes": FieldSpec("int"),
            "agenda": FieldSpec("list[string]"),
            "summary": FieldSpec("text"),
        },
        aliases=("schema:Event",),
    ),
    "decision": EntitySpec(
        type="decision",
        description="A documented decision.",
        fields={
            "headline": FieldSpec("string", required=True),
            "date": FieldSpec("date"),
            "context": FieldSpec("text"),
            "options_considered": FieldSpec("list[string]"),
            "rationale": FieldSpec("text"),
        },
    ),
    "topic": EntitySpec(
        type="topic",
        description="A learning topic, paper, or area of interest.",
        fields={
            "name": FieldSpec("string", required=True),
            "summary": FieldSpec("text"),
            "url": FieldSpec("url"),
            "tags": FieldSpec("list[string]"),
        },
        aliases=("schema:DefinedTerm",),
    ),
}

ENTITY_TYPES: tuple[str, ...] = tuple(ENTITY_SCHEMAS.keys())


# ---------------------------------------------------------------------------
# Edge predicates
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EdgeSpec:
    """Contract for an edge predicate."""

    predicate: str
    description: str
    domain: tuple[str, ...]   # allowed source entity types
    range: tuple[str, ...]    # allowed target entity types
    inverse: str | None = None
    aliases: tuple[str, ...] = ()
    temporal: bool = False


def _all_types() -> tuple[str, ...]:
    return tuple(ENTITY_SCHEMAS.keys())


EDGE_SCHEMAS: dict[str, EdgeSpec] = {
    "works_on": EdgeSpec(
        predicate="works_on",
        description="A person actively working on a project.",
        domain=("person",),
        range=("project",),
        inverse="worked_on_by",
        aliases=("foaf:currentProject",),
        temporal=True,
    ),
    "held_role_at": EdgeSpec(
        predicate="held_role_at",
        description="A person who held a role at a company.",
        domain=("person",),
        range=("company",),
        inverse="was_held_by",
        aliases=("schema:hasOccupation",),
        temporal=True,
    ),
    "has_role": EdgeSpec(
        predicate="has_role",
        description="A company that owns a role position.",
        domain=("company",),
        range=("role",),
    ),
    "produced": EdgeSpec(
        predicate="produced",
        description="A project or role that produced an achievement.",
        domain=("project", "role"),
        range=("achievement",),
        inverse="produced_by",
    ),
    "uses_skill": EdgeSpec(
        predicate="uses_skill",
        description="A project or role that exercises a skill.",
        domain=("project", "role"),
        range=("skill",),
        inverse="used_by",
    ),
    "studied_at": EdgeSpec(
        predicate="studied_at",
        description="A person who studied at an institution.",
        domain=("person",),
        range=("company", "education"),
        inverse="had_student",
        aliases=("schema:alumniOf",),
        temporal=True,
    ),
    "earned": EdgeSpec(
        predicate="earned",
        description="A person who earned an education credential or certificate.",
        domain=("person",),
        range=("education", "certificate"),
        aliases=("schema:hasCredential",),
    ),
    "attended": EdgeSpec(
        predicate="attended",
        description="A person who attended a meeting.",
        domain=("person",),
        range=("meeting",),
        inverse="attended_by",
        aliases=("schema:attendee",),
    ),
    "made": EdgeSpec(
        predicate="made",
        description="A person or meeting that made a decision.",
        domain=("person", "meeting"),
        range=("decision",),
        inverse="made_by",
    ),
    "covers": EdgeSpec(
        predicate="covers",
        description="A meeting, project, or publication that covers a topic.",
        domain=("meeting", "project", "publication"),
        range=("topic",),
        inverse="covered_by",
        aliases=("foaf:topic_interest",),
    ),
    "mentions": EdgeSpec(
        predicate="mentions",
        description="A weak reference from any node to any node (from doc ingest).",
        domain=_all_types(),
        range=_all_types(),
    ),
    "derived_from": EdgeSpec(
        predicate="derived_from",
        description="Provenance: a node derived from a document.",
        domain=_all_types(),
        range=("document",),
        inverse="gave_rise_to",
    ),
    "volunteered_at": EdgeSpec(
        predicate="volunteered_at",
        description="A person who volunteered at an organization.",
        domain=("person",),
        range=("company", "volunteer"),
        inverse="had_volunteer",
        temporal=True,
    ),
    "speaks": EdgeSpec(
        predicate="speaks",
        description="A person who speaks a language.",
        domain=("person",),
        range=("language",),
    ),
    "authored": EdgeSpec(
        predicate="authored",
        description="A person who authored a publication.",
        domain=("person",),
        range=("publication",),
        inverse="authored_by",
        aliases=("schema:author",),
    ),
}

EDGE_PREDICATES: tuple[str, ...] = tuple(EDGE_SCHEMAS.keys())


# ---------------------------------------------------------------------------
# Schema versioning
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 3
"""Bumped on breaking changes. Surfaced via ``lockedin validate``.

v3 (2026-05): added per-entity ``provenance`` system field across all
entity types. Added ``aliases: list[string]`` to ``person`` and
``company`` entities to support free-form ingest matching.
"""


# ---------------------------------------------------------------------------
# Provenance system field
# ---------------------------------------------------------------------------
# Every entity record carries a ``provenance`` field that traces where the
# record came from. Renderers surface this in their reviewer JSON so the
# user can audit the origin of each cited fact.

PROVENANCE_VALUES: tuple[str, ...] = (
    "interview",
    "pdf_ingest",
    "docx_ingest",
    "user_edit",
    "inferred",
)

_PROVENANCE_FIELD = FieldSpec(
    type="string",
    description=(
        "Source of this entity record. "
        f"Allowed values: {', '.join(PROVENANCE_VALUES)}."
    ),
    required=False,
)

# Inject ``provenance`` into every entity type. This keeps the field schema
# DRY while still being visible to ``lockedin validate``.
for _spec in ENTITY_SCHEMAS.values():
    _spec.fields.setdefault("provenance", _PROVENANCE_FIELD)


# ---------------------------------------------------------------------------
# Runtime dataclasses (used by code; storage uses the same shape)
# ---------------------------------------------------------------------------


@dataclass
class Entity:
    """An ontology node, persisted as a markdown file with frontmatter.

    Field-level validation against ``ENTITY_SCHEMAS`` is performed by
    ``lockedin validate``. Construction here only checks that ``type``
    is a recognized entity type.
    """

    type: str
    title: str
    slug: str
    body: str = ""
    fields: dict[str, Any] = field(default_factory=dict)
    links: list[dict[str, Any]] = field(default_factory=list)
    created: str | None = None
    updated: str | None = None

    def __post_init__(self) -> None:
        if self.type not in ENTITY_SCHEMAS:
            raise ValueError(
                f"unknown entity type: {self.type!r}; expected one of {sorted(ENTITY_SCHEMAS)}"
            )


@dataclass
class Edge:
    """A directional ontology edge: subject --predicate--> object."""

    subject: str
    predicate: str
    object: str
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.predicate not in EDGE_SCHEMAS:
            raise ValueError(
                f"unknown edge predicate: {self.predicate!r}; expected one of {sorted(EDGE_SCHEMAS)}"
            )
