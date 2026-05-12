---
expected_score: 2.0
expected_dimensions:
  clarity: 3
  evidence_density: 2
  persona_fit: 3
  conciseness: 3
  tone: 1
expected_revisions_required: true
question: "Tell me about a time you led a project under a tight deadline."
role: software-engineer
notes: |
  Failure mode: weak_ownership — answer is saturated with passive and
  diluted-contribution phrases ("was responsible for", "was involved in",
  "helped with", "worked with the team to", "was part of the team").
  Tone dimension should score ≤ 2 due to multiple high-severity banned
  phrase hits. Evidence density is low because actions are team-attributed
  with no personal specifics.
---
In my previous role at SOME_COMPANY I was responsible for a database migration project that had a very tight deadline. I was involved in the planning phase and helped with the technical design.

I worked with the team to identify the key risks and was part of the team that built the migration scripts. I also helped with the testing phase and contributed to writing the runbook. The whole team was really working hard and I supported the team wherever I could during the final push.

We completed the migration on time and the project was successful. I learned a lot from being involved in this project and it helped me grow as an engineer.
