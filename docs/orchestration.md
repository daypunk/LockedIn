# Orchestration design

selfgraph today is a single Claude Code skill that does most flows in
one or two turns. This document plans where multi-agent orchestration
genuinely earns its keep, and what the rollout looks like.

## Where orchestration is overkill

A flow that fits inside one Claude turn does **not** need orchestration:

- A single Q&A interview question.
- Ingesting one short document.
- Querying the vault for one fact.
- Rendering a single short cover letter (where the writer/reviewer
  split is the only orchestration we need).

For these, the cost of spinning up additional agents (token overhead,
serialization through files, latency) outweighs the marginal quality
gain.

## Where orchestration earns its keep

Three concrete cases:

### 1. Render pipeline (medium-priority)

Today: writer turn → reviewer turn (already a 2-step pipeline).
Target:

```
1. vault-query agent  (haiku)
   → reads ontology, surfaces top-N relevant nodes for the prompt slot
2. writer agent       (sonnet)
   → drafts the artifact, quoting the surfaced slugs
3. banned-phrase check (deterministic, no LLM)
   → regex pass; reports hits
4. reviewer agent     (sonnet, fresh context)
   → re-loads RUBRIC.md, scores the draft, emits JSON
5. revision agent     (sonnet, optional, max 1 round)
   → given review notes + draft, produces v2
```

Why it helps: each agent runs with a focused system prompt and
minimal context, so quality is higher than asking one agent to do all
five steps.

### 2. Bulk ingest (high-priority once docs > ~10)

Today: serial ingestion via the `ingest` skill flow.
Target (when path is a folder with N supported files):

```
1. dispatcher        — walks the folder, tags each file by type
2. parallel parsers  (haiku per file, up to 5 concurrent)
   → text extraction + heuristic entity sniff
3. diff classifier   (haiku, sequential after parsers complete)
   → addition / modification / ambiguity per item
4. ambiguity Q&A     (sonnet, interactive with user)
   → resolve flagged items one at a time
5. merger            (deterministic, no LLM)
   → write notes to vault, update inverse links
```

Why it helps: parsing 50 PDFs serially is several minutes; in
parallel under 30 seconds. The user never has to say "wait, is it
still going?"

### 3. Graph curator (low-priority, quarterly use)

Today: not implemented.
Target:

```
1. scanner           (haiku)
   → walks the vault, lists candidate duplicate clusters
       (e.g., "Naver Corp." vs "naver" vs "NAVER")
2. clustering agent  (sonnet, batched)
   → for each cluster, emits a merge proposal with confidence score
3. user confirmation (interactive)
   → user accepts/rejects each proposal
4. merger            (deterministic)
   → rewrite the canonical slug, update all inverse links, archive
     duplicates
```

Why it helps: drift is the single biggest cause of stale graphs.
A periodic curator keeps the graph clean without manual review of
every node.

## Non-goals

- A full agent framework like autopilot or a generic team
  orchestrator. selfgraph orchestration is **task-specific** —
  each pipeline is a small DAG hardcoded for one flow, not a generic
  orchestration engine.
- Always-parallel execution. Many flows still run as one Claude turn;
  we only orchestrate where parallelism or specialization is the
  bottleneck.
- Persistent agent state across user requests. Each flow is a fresh
  pipeline; vault is the only state.

## Tools

Claude Code's `Task` tool spawns sub-agents with their own system
prompts. selfgraph's pipelines call `Task(subagent_type="explore" |
"executor" | …)` for each step that needs an LLM, in parallel where
possible.

For the model tier dispatch (haiku vs sonnet vs opus), pipelines
respect the cheat sheet in `selfgraph/skill/selfgraph/TOOLS.md`. The
dispatch is *suggested* by SKILL.md instructions, not enforced by the
skill — Claude Code chooses based on its own routing.

## Sequencing

| Version | Flow | Orchestration depth |
| --- | --- | --- |
| v1.0 (now) | render | writer and reviewer two turns, already shipped |
| v1.2 | render | full 5-step pipeline above |
| v1.2 | bulk ingest | dispatcher and parallel parsers |
| v1.3 | graph curator | first quarterly run |

Each step is shipped as a behavior change in the skill files (more
explicit pipeline instructions in SKILL.md / AGENTS.md). The CLI does
not change — orchestration is internal to the skill.

## What this means for users

Users see no new commands. They see:

- Faster bulk ingest.
- Higher-quality renders (rubric scores climb).
- Fewer duplicate entities accumulating over time.

Same surface, more careful internals.
