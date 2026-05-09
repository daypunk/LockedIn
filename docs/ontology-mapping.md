# Ontology mapping — lockedin ↔ professional schemas

Cross-walk between lockedin's ontology (v0.2 target) and three external
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
| `person` | `basics` | `Person` | `foaf:Person` | The user themselves; also any other person referenced |
| `company` | `work[].name` | `Organization` | `foaf:Organization` | Employer / school / client |
| `role` | `work` | `Occupation` | — | A position held at a company; carries start/end dates |
| `project` | `projects` | `CreativeWork` | — | Work, side, OSS, study |
| `achievement` | `awards` (partial) | `Award` (partial) | — | Quantified result; metric/delta/timeframe |
| `skill` | `skills` | `DefinedTerm` | — | Technical or soft skill |
| `education` | `education` | `EducationalOccupationalCredential` | — | Degree, course |
| **`certificate`** *(new)* | `certificates` | `EducationalOccupationalCredential` | — | Professional certification — added in v0.2 |
| **`publication`** *(new)* | `publications` | `CreativeWork` | — | Paper / article / talk |
| **`volunteer`** *(new)* | `volunteer` | `Organization` (target) | — | Volunteer role |
| **`language`** *(new)* | `languages` | `Language` | — | Language proficiency |
| `document` | — | `DigitalDocument` | — | Ingested source file (provenance) |
| `meeting` | — | `Event` | — | Meeting note |
| `decision` | — | — | — | Documented decision |
| `topic` | — | `DefinedTerm` | — | Learning topic / paper / area |

JSON Resume gaps remaining (not adopted in v0.2):

- `interests` — too soft, often noise. Defer.
- `references` — privacy concerns, defer.
- `basics.profiles` — covered by `fields.url` per-entity for now.

Total v0.2 entity count: **15** (was 11). 4 added (certificate / publication / volunteer / language).

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
| **`volunteered_at`** *(new)* | — | person → company / volunteer | yes |
| **`speaks`** *(new)* | — | person → language | — |
| **`authored`** *(new)* | `schema:author` (inverse) | person → publication | — |

Total v0.2 edge count: **15** (was 12). 3 added.

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

v0.2 introduces `schema_version: 2` at the vault root
(`<vault>/.lockedin/version.json`). v0.1 vaults (no version file or
`schema_version: 1`) auto-migrate on first `lockedin validate`:

- Promote `fields: dict[str, Any]` to typed fields where the keys map
  cleanly.
- Surface unmappable keys as warnings.

Migration happens once and is idempotent.
