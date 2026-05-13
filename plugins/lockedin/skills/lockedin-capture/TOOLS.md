# TOOLS.md — lockedin-capture

Deterministic tools the skill calls. Each tool call has a defined
input, output, and failure mode. No LLM involved in these calls.

## lockedin validate

**When**: ValidatorDeterm step, after the writer turn produces a
proposal and before the reviewer turn runs.

**Call**: `lockedin validate --vault <vault_path>` or, for a dry-run
check of a proposed entity without writing it:
`lockedin validate --dry-run --entity-json <json>`

**Input**: proposed entity structure serialized as temporary markdown
file(s) under a temp vault directory.

**Output**: exits 0 on conformant structure; exits 1 with the offending
path and field on first violation.

**Failure mode**: if validation fails, the ValidatorDeterm step emits
a structured error to the writer for correction. The reviewer turn does
not run until validation passes.

---

## slug-grep (vault duplicate search)

**When**: Reviewer turn, dimension 5 — duplicate detection.

**Call**: `find <vault>/experience/<type>/ -name "*.md" | xargs grep -l "<name_fragment>"` or equivalent slug-distance check.

Specifically, for each proposed entity the reviewer checks:

1. **Exact slug match**: does `<vault>/experience/<type>/<proposed-slug>.md` exist?
2. **Name/title match**: do any files under `<vault>/experience/<type>/` have a
   `name:` or `title:` frontmatter field containing the proposed name (case-insensitive)?
3. **Alias match**: do any files have an `aliases:` list containing the proposed name?

**Input**: vault path + proposed entity type + proposed slug/name.

**Output**: list of matching file paths; empty list if none.

**Failure mode**: if the vault path does not exist (new user, no vault
yet), return empty list and note "vault not found — no duplicate check
possible".

---

## _infer_edges()

**When**: Writer turn, Step 3 — edge inference.

**What it is**: not a CLI tool but a mental operation. The writer turn
applies the EDGE_SCHEMAS domain/range rules from
`lockedin/ontology/schema.py` to derive valid edges from the set of
proposed entities.

**Implementation reference**: the Python function
`lockedin.storage.graph._infer_edges()` implements the same rules
deterministically. The skill writer turn replicates this logic without
calling the function.

**Input**: set of proposed entity types for the session.

**Output**: set of (subject_type, predicate, object_type) triples.

**Failure mode**: if the writer omits an inferable edge, the reviewer
catches it in dimension 2 and lists it in `missing_edges`.

---

## write_entity

**When**: Final step, after user confirmation in the ReconcileNegotiator.

**Call**: `lockedin` CLI write path or direct vault markdown write via
`lockedin/storage/notes.py::write_entity`.

**Input**: confirmed entity dict + edges list from the reconciled
proposal.

**Output**: markdown file written to `<vault>/experience/<type>/<slug>.md`;
edges encoded in the `links:` YAML frontmatter block of the file;
`EXPERIENCE.md` master view refreshed automatically by `write_entity`.

**Failure mode**: if a file for the slug already exists and the user
chose "create new separate entry", the slug is auto-suffixed with a
timestamp (`<slug>-20260513T1234`). Never overwrite silently.

---

## lockedin experience

**When**: Optional — when the orchestrator wants to provide the writer
turn with a vault snapshot for an existing entity.

**Call**: `lockedin experience <slug> [--vault <path>]`

**Input**: slug of an existing entity.

**Output**: denormalized markdown view of the entity and its first-hop
neighbors. Used as `vault_snapshot` input to the writer turn.

---

## Model tier guidance

| Step | Recommended tier |
| --- | --- |
| Writer turn — intent classification | haiku (fast, low-cost) |
| Writer turn — field extraction for long inputs | sonnet |
| ValidatorDeterm | n/a (deterministic, no LLM) |
| Reviewer turn | sonnet |
| ReconcileNegotiator | haiku (conversational Q&A) |

Bump to opus only if the user explicitly asks for best quality or the
capture input is highly ambiguous and requires nuanced entity-type
judgment.
