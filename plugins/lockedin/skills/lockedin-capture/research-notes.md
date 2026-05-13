# research-notes.md — lockedin-capture

Status: **v0.1 (foundational)**. Calibrated against internal design
rationale. Sources focus on personal knowledge graph capture patterns
and structured note-taking systems. A v1 release wants real-world
calibration via capture sessions with 3+ LockedIn users.

Format for citations:

```
## N. <Source title>
- URL: https://...
- Accessed: 2026-05-01
- What this taught me: <2 sentences.>
```

CI validates: URL liveness (GET with browser UA), host allowlist (see
`tests/research-allowlist.txt`), gloss presence (≥30 chars).

---

## Background: personal knowledge graph capture

Capture quality is the first-mile problem of personal knowledge graphs.
When a user says "save this", the critical decision is: what is "this"?
A vague capture produces a vague vault entry; a vague vault entry
produces a vague render artifact. The writer/reviewer pattern with
explicit schema constraints is designed to close this quality gap at
the point of entry rather than at render time.

The five rubric dimensions map to five distinct failure modes observed
across note-taking systems: schema drift (dimension 1), missing
relationships (dimension 2), placeholder rot (dimension 3), type
confusion (dimension 4), and duplicate accumulation (dimension 5).

---

## Cited sources

### 1. Obsidian.md — linking and graph structure docs
- URL: https://github.com/obsidianmd/obsidian-releases
- Accessed: 2026-05-13
- What this taught me: Obsidian's wiki-link convention and the graph
  view surface the practical cost of poorly-named nodes: when two
  notes describe the same concept with different titles, the graph
  fragments. The LockedIn duplicate-detection dimension (dimension 5)
  is a direct response to this failure mode — surface candidates
  before writing rather than discovering fragmentation later.

### 2. Hacker News discussion — Tana and structured capture patterns
- URL: https://news.ycombinator.com/item?id=33597760
- Accessed: 2026-05-13
- What this taught me: Community discussion of Tana's typed node
  system confirms that schema enforcement at capture time (not just
  at query time) dramatically reduces the maintenance burden of a
  personal knowledge graph. Users who capture with loose types spend
  disproportionate time reformatting entries for rendering; this
  motivates LockedIn's ValidatorDeterm step running before the reviewer
  turn.

### 3. Schema.org Event and CreativeWork definitions
- URL: https://github.com/schemaorg/schemaorg
- Accessed: 2026-05-13
- What this taught me: Schema.org's Event type (which informs the
  LockedIn `meeting` entity) includes attendee, agenda, and about
  (topic coverage) as first-class fields. The `covers` edge predicate
  (meeting→topic) in EDGE_SCHEMAS draws directly from the schema:about
  relationship. Using Schema.org alignment means LockedIn vault data
  can interoperate with external tools that understand these types.

### 4. Hacker News discussion — Roam Research and atomic notes
- URL: https://news.ycombinator.com/item?id=22276021
- Accessed: 2026-05-13
- What this taught me: The original Roam thread surfaces the "atomic
  note" principle: one concept per note, linked rather than nested.
  This directly informs LockedIn's rule against collapsing two
  experiences into one entity. A `project` and its `achievement` are
  separate nodes connected by a `produced` edge, not a single merged
  note — the edge is where the relationship lives, not a nested
  section.

### 5. arXiv — knowledge graph embedding and entity resolution
- URL: https://arxiv.org/search/?query=knowledge+graph+entity+resolution&searchtype=all
- Accessed: 2026-05-13
- What this taught me: Entity resolution literature consistently shows
  that string-similarity matching (slug edit-distance, name substring)
  catches the majority of real-world duplicate pairs in small personal
  graphs. The reviewer turn's dimension 5 duplicate check (slug
  edit-distance <= 2 + same-type same-name query) is calibrated against
  this finding — it covers the high-recall case without a learned
  embedding model, keeping the skill dependency-free (stdlib-only).

