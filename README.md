# selfgraph

**English** | [한국어](README.ko.md)

selfgraph is a Claude Code plugin that organizes your career experience into a structured knowledge graph. You feed it your projects, roles, achievements, and learning over time. It writes your resumes, your Korean cover letters, and renders an interactive graph from the same source.

## Install

Inside Claude Code, run three commands.

```
/plugin marketplace add daypunk/selfgraph
/plugin install selfgraph@selfgraph
/selfgraph:setup
```

The third command runs a one-time wizard. It wires the heads-up display, picks your default interview language, and chooses where your vault lives.

## How you use it

selfgraph activates when you talk to Claude Code about your experience. There are no commands to memorize.

When you want to capture experience:

- "start organizing my experience"
- "log today's meeting with the design team"
- "absorb this resume.pdf"
- "add what I learned this week from the LLM agents paper"

When you want to produce something from what is already captured:

- "make me a resume targeted at us-tech-senior"
- "write me a Korean cover letter for company X, question 1"
- "summarize last quarter's decisions"
- "show me my graph"

selfgraph asks one question at a time when it needs more from you, and it stops when it has enough.

## Why it exists

Most career tools regenerate every artifact from scratch. The artifact is the point, the source is forgotten. selfgraph treats the source as the point. Your structured experience lives at `~/.selfgraph/` as plain markdown that you own. Resumes, cover letters, and graph visualizations are queries against that memory, not the memory itself.

## How it works

The vault is plain markdown with frontmatter. Every entity becomes one file. There are fifteen entity types covering people, companies, roles, projects, achievements, skills, education, certificates, publications, volunteer work, languages, documents, meetings, decisions, and topics. Relationships between entities are stored as links inside frontmatter, and the schema enforces which type can connect to which.

When you ask for a render, selfgraph queries the vault, drafts the output in one Claude turn, and then reviews the draft against a calibrated rubric in a separate Claude turn. The two-turn split is intentional. Self evaluation in the same context inflates scores by about one point.

selfgraph runs on your existing Claude Code subscription. It does not require an Anthropic API key, and it does not phone home.

## Skills

| Skill | Role |
|---|---|
| `selfgraph` | Main skill. Routes natural language requests, runs the Q&A interview that seeds your vault, coordinates ingest and render flows. |
| `selfgraph-render-jaso` | Korean cover letter renderer with a five-dimension rubric (<!-- ko-example -->두괄식, 구조화, 구체성, 표현, 적합성<!-- /ko-example -->). Cross-source confirmed banned phrase list. Two-turn writer and reviewer with a hard guard for fresh rubric loading. |
| `selfgraph-render-resume-en` | English resume renderer. Five dimensions: metric density, action verb quality, structural adherence, banned phrase cleanliness, persona fit. Three personas: us-tech-senior, us-tech-mid, pm-product. |

## Documentation

| File | Purpose |
|---|---|
| [`docs/architecture.md`](./docs/architecture.md) | How the pieces fit together |
| [`docs/ontology-spec.md`](./docs/ontology-spec.md) | The frontmatter contract |
| [`docs/ontology-mapping.md`](./docs/ontology-mapping.md) | Cross-walk to JSON Resume, Schema.org, FOAF |
| [`docs/orchestration.md`](./docs/orchestration.md) | Render and ingest pipelines |
| [`docs/cli.md`](./docs/cli.md) | Optional power-user CLI |
| [`docs/hud.md`](./docs/hud.md) | Status line integration |

## License

MIT. See [LICENSE](./LICENSE).
