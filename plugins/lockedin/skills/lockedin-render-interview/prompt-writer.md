# prompt-writer.md — render-interview writer turn

This is the writer-turn instruction for `render-interview`. The
reviewer turn lives in `prompt-reviewer.md` and runs in a SEPARATE
Claude turn with `RUBRIC.md` re-loaded fresh.

## Inputs

- **question** (required): the interview question, free text or a
  canonical form (`tell me about yourself`, `tell me about a time
  you led a project`, `describe a conflict you resolved`, etc.).
- **lang** (optional): `en` or `ko`. Default `en`.
- **role** (optional): target role / persona for tone.
- **word_limit** (optional): default 250 words for English, 600 자
  for Korean.

## Vault query

Surface vault entries relevant to the question:

- Behavioural / story-shaped questions → role + project +
  achievement nodes connected to the user.
- Technical / depth questions → skill + project nodes.
- Motivation / fit questions → company + role + decision nodes.

If the vault has no relevant entries, ask the user one question to
fill the gap before drafting. Do not invent facts.

## Drafting rules

- **STAR or PAR shape.** Situation / Task / Action / Result, or
  Problem / Action / Result for incident-shaped questions. Implicit
  S/T fine when context is clear.
- **One experience per paragraph (load-bearing).** When the answer
  pulls in more than one experience, write each in its own paragraph
  and add an explicit transition sentence between them. Mixing two
  experiences in one paragraph creates reader cognitive load.
- **Lead with the conclusion (English) or 두괄식 (Korean).** First
  sentence states the takeaway; the rest scaffolds it.
- **Quote ontology slugs while drafting.** `[[type/slug]]` for any
  cited entity. The skill orchestrator runs
  `lockedin/render/resolve_slugs.py` after this turn to replace
  every slug with the entity's natural-language label. **The
  user-facing artifact must NOT contain raw slug notation.**
- **Concrete metrics.** Numbers, named systems, named people (when
  the user has explicitly logged them). Generic adjectives without
  evidence are flagged by the reviewer turn.
- **Word limit.** Stay within ±20% of the limit. Interview answers
  are shorter than resume bullets and longer than rubric soundbites.
- **Active voice.** Past tense for past stories, present tense for
  current work.
- **Persona fit.** If `role` is given, match its register. Engineer
  questions get specific stack and decision shape; PM questions get
  user-outcome and stakeholder shape.

## Output

A single answer in markdown, no headers. The skill orchestrator
hands this to the reviewer turn (with slugs intact for verification),
then resolves slugs to natural language for the user's final view.

## What you do NOT do

- Score yourself.
- Suggest revisions.
- Add headers, footers, or surrounding chat ("Here is your
  answer..."). Output the answer text alone.
- Generate fictitious metrics or named systems. If the vault entity
  has no metric, ask the user before inventing one.
