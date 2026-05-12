---
fixture_kind: fail
persona: us-tech-mid
expected_revisions_required: false
banned_phrases_hit: ["assisted with", "worked on", "helped with", "was involved in", "participated in"]
dimensions_failed: ["action_verb_quality"]
notes: |
  Synthesized composite. Placeholders only. No real persons or companies.
  Action verb quality failure. Bullets dominated by weak/passive phrases:
  assisted with, worked on, helped with, was involved in, participated in.
  These are all in banned_phrases.json. Action verb quality dimension
  should score ≤2. Metrics are minimal but present to isolate verb issue.
---

## SAMPLE_USER

sample@placeholder.invalid | Seattle, WA

---

### SOME_COMPANY — Software Engineer
*2021 – Present*

- Assisted with the migration of legacy authentication services to a new identity provider over a 6-month project.
- Worked on the backend API team to improve response times; latency dropped from 800ms to 400ms after the team's changes.
- Helped with code review and pull request feedback for the 3-person feature squad.
- Was involved in the on-call rotation for the payments service, handling roughly 4 incidents per quarter.
- Participated in sprint planning and retrospective ceremonies each two-week cycle.

### BLUE_LABS — Junior Engineer
*2019 – 2021*

- Assisted with building the internal dashboard used by the customer support team.
- Worked on bug fixes and minor feature improvements for the web application.

---

### Skills

Python · Django · PostgreSQL · AWS · Git
