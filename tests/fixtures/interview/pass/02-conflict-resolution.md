---
expected_score: 4.5
expected_dimensions:
  clarity: 5
  evidence_density: 4
  persona_fit: 5
  conciseness: 5
  tone: 4
expected_revisions_required: false
question: "Describe a time you resolved a conflict with a colleague."
role: product-manager
notes: |
  Synthetic composite — PAR structure (Problem / Action / Result),
  stakeholder-outcome emphasis appropriate for PM persona. Placeholder
  identifiers only. No real persons or companies. Pass fixture: persona_fit
  is strong (user-outcome and stakeholder framing), active voice throughout,
  no banned phrases. Evidence density is 4 because one connector sentence
  is contextual rather than metric-backed.
---
A disagreement about prioritisation between [[role/pm-payments-2024]] and the tech lead for ACME's checkout team was slowing the Q2 roadmap by three weeks; I surfaced the root disagreement and resolved it in one structured working session.

The conflict came from different data sets. The tech lead's sprint health metrics showed mounting technical debt; my user-research synthesis from [[project/checkout-ux-study-2024]] showed abandonment at the address step was costing 14% of conversion. We were both right but optimising for different failure modes. I proposed a shared cost model: we would quantify the debt risk in lost developer-hours per quarter and express the UX abandonment in lost GMV per quarter, then let the numbers drive priority. I ran that analysis over two days, presented the output in a 30-minute working session, and both items ended up in the Q2 plan — the debt item sequenced first because its cost exceeded the UX item's cost by 1.8x over the quarter.

The roadmap unblocked in one week. The tech lead cited the cost-model approach in the following quarter's planning as the right way to handle competing priorities, and the PM team adopted it as a template for cross-functional trade-off discussions.
