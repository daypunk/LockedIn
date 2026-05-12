---
fixture_kind: pass
persona: ml-engineer-mid
expected_score: 4.4
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Placeholders only (SAMPLE_USER, GLOBAL_TECH, ACME_CORP).
  Demonstrates strong persona_fit for ml-engineer-mid: XGBoost classifier with
  AUC delta, LightGBM ranker with NDCG metric, drift monitoring with PSI
  threshold, and A/B test with business KPI result. Tool mentions: MLflow,
  Evidently, Feast, BentoML. No GenAI/LLM claims — classical ML focus.
  Verbs: Trained, Deployed, Reduced, Built, Monitored, Implemented.
---

## SAMPLE_USER

sample@placeholder.invalid | github.com/placeholder | San Francisco, CA

---

### GLOBAL_TECH — ML Engineer (Fraud & Risk)
*2021 – Present*

Owned the production fraud scoring pipeline for a 1.4M daily-transaction platform; primary on-call for model serving SLA.

- Trained an XGBoost fraud classifier on 2.1M rows and 160 engineered features, raising precision at 5% recall from 0.58 to 0.79; reduced false-positive fraud holds by ~21% and recovered an estimated $280k/month in previously declined-transaction revenue.
- Deployed the fraud model as a FastAPI inference service on Kubernetes with ONNX export, meeting a p95 latency SLA of 35ms under 500 RPS load-test conditions; BentoML packaging reduced container build time from 18 minutes to 4 minutes.
- Implemented PSI-based drift monitoring for 8 production models using Evidently, configured to alert PagerDuty when PSI exceeded 0.2 on any top-20 feature; caught 2 distribution-shift events before model AUC degraded below the production SLA.
- Reduced offline-to-online feature skew by auditing 14 features in the Feast feature store against the training pipeline's computation logic; eliminated 3 point-in-time leakage bugs that had inflated offline AUC by ~0.04.

### ACME_CORP — Data Scientist (Recommendations)
*2019 – 2021*

- Migrated the homepage ranking model from a heuristic scorer to a LightGBM ranker trained on 90-day implicit click-through feedback; offline NDCG@10 improved from 0.43 to 0.59 and a 4-week A/B test showed +7.1% 7-day user retention.
- Built reproducible training pipelines with MLflow experiment tracking, pinned Conda environments, and versioned dataset snapshots; onboarded 2 new data scientists with zero environment-parity issues over 6 months.

---

### Skills

Python · XGBoost · LightGBM · scikit-learn · MLflow · Feast · Evidently · FastAPI · ONNX · BentoML · Kubernetes · SQL
