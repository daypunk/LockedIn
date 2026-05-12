# Ontology mapping — lockedin ↔ professional schemas

Cross-walk between lockedin's ontology (v3) and three external
references. Use this when (a) extending lockedin's schema, (b) building
import/export adapters, or (c) deciding whether to add a new entity type
versus extending an existing one.

References:

- **JSON Resume** — https://jsonresume.org/schema/ — community career
  schema, widely supported by resume tools.
- **Schema.org** — https://schema.org — the broadest practical
  knowledge-graph vocabulary.
- **FOAF** — http://xmlns.com/foaf/spec/ — RDF vocabulary for people
  and relationships.

## Entity types

| lockedin type | JSON Resume | Schema.org | FOAF | Notes |
| --- | --- | --- | --- | --- |
| `person` | `basics` | `Person` | `foaf:Person` | The user themselves; also any other person referenced. v3 adds `aliases` for ingest matching |
| `company` | `work[].name` | `Organization` | `foaf:Organization` | Employer / school / client. v3 adds `aliases` for ingest matching |
| `role` | `work` | `Occupation` | — | A position held at a company; carries start/end dates |
| `project` | `projects` | `CreativeWork` | — | Work, side, OSS, study |
| `achievement` | `awards` (partial) | `Award` (partial) | — | Quantified result; metric/delta/timeframe |
| `skill` | `skills` | `DefinedTerm` | — | Technical or soft skill |
| `education` | `education` | `EducationalOccupationalCredential` | — | Degree, course |
| `certificate` | `certificates` | `EducationalOccupationalCredential` | — | Professional certification |
| `publication` | `publications` | `CreativeWork` | — | Paper / article / talk |
| `volunteer` | `volunteer` | `Organization` (target) | — | Volunteer role |
| `language` | `languages` | `Language` | — | Language proficiency |
| `document` | — | `DigitalDocument` | — | Ingested source file (provenance) |
| `meeting` | — | `Event` | — | Meeting note |
| `decision` | — | — | — | Documented decision |
| `topic` | — | `DefinedTerm` | — | Learning topic / paper / area |

JSON Resume gaps remaining (not adopted in v3):

- `interests` — too soft, often noise. Defer.
- `references` — privacy concerns, defer.
- `basics.profiles` — covered by `fields.url` per-entity for now.

Total v3 entity count: **15**. v3 adds the `provenance` system field
across every type, and `aliases` on `person` and `company`.

## Edge predicates

| lockedin predicate | FOAF / Schema.org alignment | Domain → Range | Temporal? |
| --- | --- | --- | --- |
| `works_on` | `foaf:currentProject` | person → project | yes |
| `held_role_at` | `schema:hasOccupation` | person → company | yes |
| `has_role` | — | company → role | — |
| `produced` | — | project / role → achievement | — |
| `uses_skill` | — | project / role → skill | — |
| `studied_at` | `schema:alumniOf` | person → company / education | yes |
| `earned` | `schema:hasCredential` | person → education / certificate | — |
| `attended` | `schema:attendee` | person → meeting | — |
| `made` | — | person / meeting → decision | — |
| `covers` | `foaf:topic_interest` | meeting / project / publication → topic | — |
| `mentions` | — | any → any (weak link from ingest) | — |
| `derived_from` | — | any → document (provenance) | — |
| `volunteered_at` | — | person → company / volunteer | yes |
| `speaks` | — | person → language | — |
| `authored` | `schema:author` (inverse) | person → publication | — |

Total v3 edge count: **15**.

## Field-level coverage examples

JSON Resume `work` entry → lockedin `role` entity:

| JSON Resume field | lockedin field | Type |
| --- | --- | --- |
| `name` (company name) | (relation: `held_role_at` → company entity) | edge |
| `position` | `title` | string, required |
| `startDate` | `start_date` | date, required |
| `endDate` | `end_date` | date, optional (omit if current) |
| `summary` | `summary` | text |
| `highlights[]` | `highlights` | list[string] |
| `url` | `fields.url` | url |

Schema.org `Person` → lockedin `person`:

| Schema.org property | lockedin field |
| --- | --- |
| `name` | `name` (required) |
| `email` | `email` (FieldSpec type=email) |
| `address.addressLocality` | `based_in` |
| `description` | `summary` |
| `jobTitle` | `current_role` |

## Inverse links

When `works_on` is recorded, graph derivation auto-emits the inverse
`worked_on_by` so that walking from project → person works without an
extra round-trip:

| Forward | Inverse |
| --- | --- |
| `works_on` | `worked_on_by` |
| `held_role_at` | `was_held_by` |
| `produced` | `produced_by` |
| `uses_skill` | `used_by` |
| `studied_at` | `had_student` |
| `attended` | `attended_by` |
| `made` | `made_by` |
| `covers` | `covered_by` |
| `derived_from` | `gave_rise_to` |
| `volunteered_at` | `had_volunteer` |
| `authored` | `authored_by` |

`mentions` and `earned` do not auto-emit inverses (mentions is too noisy,
earned has no clean inverse name).

## Compatibility map

If we ever need to **export** to JSON Resume:

```
person.fields → resume.basics
roles where end_date ≥ active or absent → resume.work[]
education entries → resume.education[]
certificate entries → resume.certificates[]
project entries → resume.projects[]
publication entries → resume.publications[]
skill entries → resume.skills[]
language entries → resume.languages[]
volunteer entries → resume.volunteer[]
achievement entries (not in JSON Resume directly) → flatten into work.highlights
```

Importing from a JSON Resume document is the inverse map and trivial
once v0.2 lands.

## Schema versioning

v3 sets `schema_version: 3` at the vault root
(`<vault>/.lockedin/version.json`). Older vaults (`schema_version: 1`
or `2`, or no version file at all) migrate via `lockedin migrate`:

- Rename the default template directory `career/` → `experience/`.
- Inject `provenance` defaults on every entity (existing entries get
  `provenance: user_edit`).
- Seed empty `aliases` lists on `person` and `company`.
- Promote `fields: dict[str, Any]` to typed fields where the keys map
  cleanly; surface unmappable keys as warnings.

Migration is idempotent.
