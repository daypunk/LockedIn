---
expected_score: 4.5
expected_dimensions:
  clarity: 4
  evidence_density: 5
  persona_fit: 4
  conciseness: 5
  tone: 5
expected_revisions_required: false
question: "Tell me about a time you failed and what you learned from it."
role: software-engineer
notes: |
  Synthetic composite — STAR structure with honest failure framing.
  Placeholder identifiers only. No real persons or companies. Pass fixture:
  evidence density is high (named system, named metric, specific failure
  mode). Tone is active and non-deflecting throughout — candidate owns the
  failure directly without blame-shifting. Clarity is 4 not 5 because the
  takeaway sentence arrives in sentence two rather than sentence one, which
  is acceptable for a failure story where brief context anchors the lesson.
---
In 2023, a migration I owned for [[project/db-migration-2023]] at GLOBAL_TECH caused 40 minutes of read degradation because I underestimated index rebuild time on the production replica — a gap in my pre-migration checklist.

The migration was a foreign-key backfill across 18 million rows. I had tested the process on a staging replica that was six weeks stale. Production traffic patterns had changed the row distribution since the last staging refresh, so the index rebuild ran 3x longer than my estimate and locked the read path for 40 minutes during peak traffic. I caught the slowdown at minute 12 via monitoring, escalated to the on-call lead, and triggered the rollback plan I had documented. We were fully recovered at minute 40. The root cause was a stale staging environment — not the migration logic itself.

I rewrote the migration runbook to include a staging-freshness check (maximum 72-hour lag from production) and a live row-count delta comparison before any production execution. That check has been applied to eight subsequent migrations at GLOBAL_TECH with zero recurrence of the staging-drift failure mode.
