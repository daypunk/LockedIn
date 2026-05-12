---
expected_score: 2.5
expected_dimensions:
  clarity: 3
  evidence_density: 2
  persona_fit: 3
  conciseness: 3
  tone: 3
expected_revisions_required: true
question: "Tell me about a time you had to learn a new technology quickly."
role: software-engineer
notes: |
  Failure mode: missing_result — STAR structure has reasonable Situation
  and Action but the Result section is a vague learning statement with no
  measurable outcome. Evidence density drops because the claimed result
  ("I learned a lot") has no named outcome, no metric, and no named
  stakeholder impact. No banned phrases from the high-severity list, so
  tone is moderate. This isolates the missing-result failure mode.
---
When GLOBAL_TECH decided to migrate our data pipeline from a batch Hadoop job to a streaming architecture using a technology I had never used before, I had two weeks to get productive enough to contribute to the design.

I spent the first three days reading the official documentation and working through the quickstart tutorial. Then I built a small prototype that replicated one of our existing batch jobs as a streaming pipeline. I pair-programmed with a colleague who had prior experience to get feedback on my design choices, and I asked questions in the team Slack channel whenever I was stuck.

I learned a lot from this experience and became much more comfortable with stream processing. The project was a good learning opportunity and I think I grew a lot as an engineer from going through this process.
