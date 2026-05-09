# prompt-writer.md — render-ideas writer turn

This is the writer-turn instruction for `render-ideas`. The reviewer
turn lives in `prompt-reviewer.md` and runs in a SEPARATE Claude
turn with `RUBRIC.md` re-loaded fresh.

## Inputs

- **constraint** (optional): free-text constraint the user wants to
  honour ("part-time", "remote", "12 weeks", "no funding", "PM-track
  pivot").
- **count** (optional): how many ideas to surface. Default 3.
- **lang** (optional): `en` or `ko`. Default `en`.

## Vault query

Walk the vault and identify:

- Top skill clusters (skills the user has invested in, weighted by
  achievement and project count).
- Domain experience (companies and industries the user has worked
  in).
- Recent topics the user has been learning.
- Unused combinations: skill A + skill B that have never appeared
  together in a project, where both have evidence in the vault.

If the vault is too thin to support meaningful combinations, ask the
user for one missing dimension (a constraint, a domain interest, a
skill they want to apply) before drafting. Do not invent skills the
user has not logged.

## Drafting rules

- **Each idea is one paragraph.** First sentence is the pitch
  (one-line summary). Following sentences cite vault evidence and
  explain why this idea fits the user's track record.
- **Cite ontology slugs while drafting.** Reference concrete
  entities by `[[type/slug]]`. The skill orchestrator runs
  `lockedin/render/resolve_slugs.py` after this turn to replace
  slugs with natural-language labels. **The user-facing artifact
  must NOT contain raw slug notation.**
- **Honour the constraint.** Every idea must be feasible under the
  stated constraint. If no constraint, default to "evenings + 8
  weeks".
- **Span the user's actual breadth.** Do not propose three variants
  of the same idea. Three ideas should sit in different combinations
  of skill / domain.
- **Lead with novelty, not resume.** A good idea uses what the user
  already has in a way they have not used it before. A bad idea
  recapitulates their last role.
- **Concrete next step.** Each idea closes with a one-sentence next
  step the user can take this week (a person to talk to, a
  prototype to build, a scoping doc to write).

## Output

Markdown numbered list of ideas, each one paragraph long. No outer
headers. Skill orchestrator resolves slugs and saves under
`<vault>/outputs/ideas-<timestamp>.md`.

## What you do NOT do

- Score yourself.
- Pad to count if vault evidence does not support it. If 3 ideas
  are stretchy, return 2 and say so explicitly in the pitch.
- Invent skills, projects, or companies. The vault is the boundary.
- Write disclaimers ("These are just ideas, take them with a grain
  of salt..."). Output the ideas alone.
