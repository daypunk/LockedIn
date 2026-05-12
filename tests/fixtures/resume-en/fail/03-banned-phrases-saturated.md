---
fixture_kind: fail
persona: us-tech-senior
expected_revisions_required: false
banned_phrases_hit: ["team player", "results-driven", "proven track record", "passionate about", "synergy", "thought leader", "detail-oriented"]
dimensions_failed: ["banned_phrase_cleanliness"]
notes: |
  Synthesized composite. Placeholders only. No real persons or companies.
  Banned phrase cleanliness failure. Multiple high-severity buzzwords from
  banned_phrases.json: team player, results-driven, proven track record,
  passionate about, synergy, thought leader, detail-oriented.
  Banned phrase cleanliness dimension should score ≤1 (7+ hits).
---

## SAMPLE_USER

sample@placeholder.invalid | Chicago, IL

---

### SOME_COMPANY — Senior Software Engineer
*2019 – Present*

Results-driven and detail-oriented engineer with a proven track record of delivering large-scale distributed systems. Passionate about building reliable infrastructure that enables business synergy across product teams.

- Served as the thought leader for the platform team's migration roadmap, aligning 4 engineering squads.
- A natural team player who facilitated cross-functional synergy between backend and frontend engineering during the monolith decomposition effort.
- Built the API gateway layer for the core services platform, improving routing reliability.
- Collaborated with the SRE team to define on-call runbooks and incident severity tiers.

### REGIONAL_BANK Digital — Software Engineer
*2016 – 2019*

Detail-oriented engineer passionate about fintech infrastructure. Proven track record of delivering compliance-ready systems on schedule.

- Implemented PCI-compliant data masking for customer account records.
- Supported the team's quarterly PEN test remediation cycles.

---

### Skills

Go · Kubernetes · AWS · PostgreSQL · Terraform
