---
name: selfgraph-render-portfolio
description: |
  Render a static-site portfolio (single-file HTML) from the selfgraph
  ontology. Picks top achievements / projects / skills and lays them out
  in a personal-site-style template. Single-turn (lighter than the
  jaso/resume two-turn).

  Use when the user says: "render portfolio", "make a portfolio site",
  "build my portfolio page". Output: `outputs/portfolio/index.html` plus
  assets, fully static and offline-openable.
---

# render-portfolio

Status: **placeholder**.

## Use this when

- User asks for a static personal portfolio site.
- User wants a shareable HTML page derived from their vault.

## Do NOT use when

- User wants a Korean cover letter → `render-jaso`.
- User wants an ATS-aimed resume → `render-resume-en`.
- User wants the **graph viz** itself, not a portfolio page → run
  `selfgraph render graph` (deterministic CLI, no LLM needed).

## Required design constraints

- Output: `outputs/portfolio/index.html` + assets, fully static (no CDN,
  opens offline like the graph viz).
- Pulls top achievements / projects / skills from the ontology and
  renders them in a personal-site-style layout.
- Deep-link friendly — each project becomes a section anchor.

## Final checklist

- HTML opens with zero console errors.
- All linked assets are local (no CDN dependencies).
- Each project section has a stable anchor (`#project-<slug>`).

## Files in this directory

```
SKILL.md
research-notes.md   citations with URL + ISO date + 2-sentence gloss
prompt.md           (TODO) single-turn rendering prompt
template.html       (TODO) static layout shell
```
