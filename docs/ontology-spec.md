# lockedin ontology specification (v0.2)

> The contract `lockedin validate` checks. If a note's frontmatter
> doesn't conform, validate exits non-zero.

For the cross-walk to JSON Resume / Schema.org / FOAF, see
`docs/ontology-mapping.md`. For per-entity field contracts and edge
domain/range, the source of truth is `lockedin/ontology/schema.py`.

## File layout

Every entity is one markdown file at:

```
<vault>/<domain>/<type>/<slug>.md
```

`<vault>` defaults to `~/Documents/LockedIn/`. `<domain>` matches the ontology
template (`career`, `meeting`, `project`, `learning`, …). `<slug>` is a
URL-safe lowercase identifier derived from the note's `title:` field.

## Frontmatter contract

```yaml
---
type: <one of lockedin.ontology.schema.ENTITY_TYPES>
title: <human-readable title>
slug: <url-safe identifier>
created: <ISO-8601 datetime>
updated: <ISO-8601 datetime>
fields:
  <type-specific fields, see ENTITY_SCHEMAS>
links:
  - predicate: <one of lockedin.ontology.schema.EDGE_PREDICATES>
    object: <slug of another note>
    weight: <optional float, default 1.0>
---
<free-form markdown body>
```

`type`, `title`, `slug`, `created`, `updated` are required at the
frontmatter level. Per-entity required fields live in `ENTITY_SCHEMAS`.

## Entity types (v0.2 — 15 types)

```
person       company      role         project      achievement
skill        education    certificate  publication  volunteer
language     document     meeting      decision     topic
```

Each has a typed field contract — required vs optional, with field
types (`string`, `text`, `url`, `email`, `date`, `year`, `int`,
`float`, `bool`, `list[string]`). See `ENTITY_SCHEMAS` for the full
spec.

Example — `person`:

```yaml
fields:
  name: "Sample User"          # required (string)
  current_role: "PM"           # optional (string)
  email: "x@y.com"             # optional (email — validated)
  based_in: "Seoul"            # optional (string)
  summary: |                    # optional (text)
    Multi-sentence summary.
```

## Edge predicates (v0.2 — 15 predicates)

```
works_on         held_role_at     has_role          produced
uses_skill       studied_at       earned            attended
made             covers           mentions          derived_from
volunteered_at   speaks           authored
```

Each carries a domain (allowed source types) and range (allowed target
types). Some carry an `inverse` (auto-emitted in graph derivation) and
a `temporal` flag (carries start/end dates on the edge if needed).

Example domain/range checks:

- `works_on` requires source `person`, target `project`. A `company
  --works_on--> project` link fails validation.
- `held_role_at` requires source `person`, target `company`. Temporal
  (start_date / end_date can be associated with the edge or with the
  related `role` node).
- `mentions` allows any → any (used by document ingest).

## Round-trip invariant

A note read by `storage.notes.read_entity` and immediately re-written
by `storage.notes.write_entity` MUST produce a byte-identical file.
Both the Python CLI and the skill-only helper must satisfy this; CI's
parity test diffs the two implementations against shared fixtures.

## Validation rules (full set in `lockedin validate` impl)

1. `type` must be in `ENTITY_TYPES`.
2. `slug` must be unique across the vault.
3. Required fields per `ENTITY_SCHEMAS[type]` must be present.
4. Field values must match expected types (date string, URL, email,
   etc. — best-effort regex check, not strict parse).
5. `links[].predicate` must be in `EDGE_PREDICATES`.
6. `links[].source` (the containing note's type) must be in
   `predicate.domain`.
7. `links[].object` (target slug) must reference an existing slug, and
   that target's type must be in `predicate.range`.
8. `created` ≤ `updated`, both ISO-8601 UTC.
9. `title` must be non-empty.

## Schema versioning

This is **schema_version 2**. v0.1 vaults (no version file or
`schema_version: 1`) are still readable, but `lockedin validate` will
report any v0.2 contract violations (typically: missing required
fields). Run the migration step (planned for a future `lockedin
migrate` command) to bring older vaults forward, or hand-edit the
flagged notes.

The vault root marker is `<vault>/.lockedin/version.json`:

```json
{ "schema_version": 2 }
```
