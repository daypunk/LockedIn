# prompt-writer.md — render-jaso writer turn

This is the writer-turn instruction for `render-jaso`. The reviewer
turn lives in `prompt-reviewer.md` and runs in a SEPARATE Claude turn
with `RUBRIC.md` re-loaded fresh. Do not collapse the two turns —
same-context self-evaluation inflates scores by ~1 point.

## Inputs

- **company** (required): target company name (free text).
- **question** (required): the 자소서 prompt as written by the company,
  or a canonical slot identifier (`지원동기`, `성장과정`, `성격의 장단점`,
  `입사 후 포부`, or numeric `1–4` defaulting to that order).
- **role** (optional): target 직무 / role description.
- **word_limit** (optional): per-question 자 count. Default 1000 자
  unless the user specifies.

## Vault query

Before drafting, query the user's vault for nodes that connect to the
target. Specifically:

1. If the target company already exists as a `company` entity in the
   vault, surface its outgoing edges (roles, projects, achievements
   linked to it).
2. Surface the user's top-3 most relevant nodes for the prompt slot:
   - 지원동기 → projects + skills relevant to the role + any prior
     contact with the company.
   - 성장과정 → formative role / project / education nodes.
   - 성격의 장단점 → roles where strengths were demonstrated, plus any
     achievement that exposed a weakness honestly.
   - 입사 후 포부 → projects / skills the user wants to extend at this
     company; reference the company's known direction if any.
3. If the vault is empty or returns nothing relevant, ask the user one
   question to fill the gap before drafting. Do not invent ontology
   data.

## Drafting rules

- **두괄식**. The first sentence states the conclusion / 핵심 / 차별점.
  The rest of the answer scaffolds the lead.
- **STAR or PAR per paragraph**. Each body paragraph has Situation /
  Task / Action / Result (or Problem / Action / Result). Implicit S/T
  is fine if context is clear.
- **Quote ontology slugs.** Reference concrete entities by slug in
  square brackets, e.g. `[[role/lead-pm-fintech-2024]]`. The reviewer
  rewards this.
- **Active voice. Concrete metrics.** Numbers (`30%`, `8주`, `매출
  N억`), named projects, named technologies.
- **No banned phrases.** Before returning the draft, scan it against
  `banned_phrases.json`. If any match, replace with a more concrete
  substitute that quotes an ontology node.
- **Word limit.** Stay within ±10% of `word_limit` (default 1000 자).
- **Company / role fit.** At least one sentence references a specific
  fact about the target company / role / industry. If the user has not
  given enough context for that, ask one question before drafting.
- **Korean output only.** No mixed English unless quoting a proper
  noun (project name, technology, brand).

## Output

A single Korean 자소서 answer in markdown, no headers. Cite ontology
slugs in `[[type/slug]]` form so the reviewer turn can verify them.

After producing the draft, run the banned-phrase check yourself:

```bash
python3 -c "
import json, re, sys
banned = json.load(open('lockedin/skill/render-jaso/banned_phrases.json'))['phrases']
draft = open('/tmp/draft.txt', encoding='utf-8').read()
hits = [p for p in banned if re.search(re.escape(p), draft)]
sys.exit(0 if not hits else 1)
"
```

If any banned phrase is present, regenerate that sentence before
emitting the draft. Then hand off to the reviewer turn.

## What you do NOT do here

- Score yourself. That's the reviewer turn's job.
- Suggest revisions. The reviewer's JSON output drives the revision
  cycle, not your own self-critique.
- Add headers, footers, or surrounding chat ("Here is your 자소서...").
  Output the answer text alone.
