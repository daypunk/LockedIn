# ml-engineer-mid

## Snapshot

Mid-level machine learning engineer with 3-6 years of experience. Focus is
on productizing classical ML and gradient boosted models: feature engineering,
training pipelines, model deployment as inference services, and monitoring for
data drift and performance degradation. Distinct from an AI engineer (who
focuses on LLM fine-tuning, prompt engineering, and retrieval-augmented
generation) and from a data scientist (who focuses on exploration and
statistical analysis). This persona owns the end-to-end lifecycle of a
production ML model — from feature pipeline through a served endpoint to
alerting when the model goes stale. Targets roles at companies with
established ML platforms or feature stores: fintech, adtech, recommender
systems, fraud detection, demand forecasting.

## Skill cluster

Hard skills (8-12 items):
- Python — scikit-learn, XGBoost / LightGBM / CatBoost, pandas, NumPy
- Feature engineering at scale: feature store design (Feast, Tecton, or
  custom), point-in-time correct joins for training data
- Model training pipelines: MLflow or Weights & Biases for experiment
  tracking, reproducible training runs, hyperparameter sweeps
- Serving infrastructure: Flask / FastAPI inference endpoints, ONNX export,
  TorchServe or BentoML
- Model monitoring: data drift detection (evidently, Alibi Detect), model
  performance dashboards, alert thresholds on key metrics (AUC, precision,
  recall, NDCG)
- SQL for feature extraction from analytical warehouses
- Cloud ML services (SageMaker, Vertex AI, or Azure ML) for managed training
  and deployment
- A/B testing and shadow-mode evaluation for model version comparison
- Docker / Kubernetes for packaging and deploying inference services
- Offline evaluation rigor: time-series train/val/test splits, leakage
  detection, calibration

Soft / cross-functional skills (4-6 items):
- Stakeholder metric translation: turning a business goal (fraud loss rate)
  into an ML objective (binary classification threshold, precision/recall
  trade-off)
- Cross-functional collaboration with data engineers to define feature
  pipeline contracts and SLAs
- Model explainability communication to non-technical stakeholders (SHAP
  plots, partial dependence)
- Incident response for model degradation: diagnosing distribution shift,
  feature pipeline failures, or serving latency regressions

## Responsibility patterns

- Designs and maintains feature pipelines that generate point-in-time correct
  training datasets, verifying for leakage before each training run.
- Trains, evaluates, and versions models using tracked experiments (MLflow /
  W&B), maintaining reproducibility via pinned dependency environments and
  data snapshots.
- Deploys models as low-latency inference services, meeting p95 latency SLAs
  (commonly under 50ms for real-time fraud or ranking) with load-tested
  confidence.
- Implements drift detection that pages on-call when feature distributions or
  model output distributions diverge from baseline by a statistically
  significant margin.
- Runs A/B or shadow-mode experiments to validate new model versions before
  full promotion, reporting lift against business KPIs (revenue, fraud loss,
  CTR).
- Reduces offline-to-online feature skew by auditing feature computation
  logic in the training pipeline against the serving path and enforcing
  parity through integration tests.
- Documents model cards (training data lineage, evaluation methodology,
  intended use, known failure modes) as a prerequisite for model promotion.

## Tone guidance

Vocabulary register: rigorous, metric-anchored, ML-vocabulary specific.
Bullets should name the model family (XGBoost, LightGBM, logistic regression,
neural ranking model), the evaluation metric (AUC, precision@k, NDCG, F1),
and the business outcome it serves (fraud loss rate, CTR lift, churn
reduction). Avoid AI hype language (GenAI, LLM fine-tuning claims) unless the
role genuinely involved them — this persona is classical ML, not LLM
engineering.

Lean on: Trained, Deployed, Reduced, Monitored, Profiled, Built, Designed,
Evaluated, Shipped, Automated, Improved, Migrated, Instrumented.

Avoid: "AI/ML solutions" (too vague), "cutting-edge models" (claim without
evidence), "deep learning" unless a neural architecture was actually used and
justified, "big data" (specify volume), "GenAI" unless accurate.

## Action verb cluster

Trained, Deployed, Reduced, Built, Monitored, Designed, Evaluated, Shipped,
Automated, Profiled, Instrumented, Improved, Migrated, Validated, Implemented,
Benchmarked, Established, Replaced

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "AI/ML solution" — generic; name the model family and the business problem
- "cutting-edge" — claim without evidence; describe the specific technique
  and its measured improvement
- "data-driven insights" — tautological in ML context; replace with the
  specific metric and the decision it drove
- "leveraged machine learning" — soft verb; state what model type was trained
  and the target metric
- "model performance improvements" — vague; specify AUC delta, precision
  change, or latency gain
- "end-to-end ML pipeline" without specifics — name each stage and the
  tooling used

## Persona fit scoring guidance

- `ml-engineer-mid` persona_fit >= 4 requires at least 1 model-specific noun
  (XGBoost, LightGBM, sklearn, ONNX, MLflow, feature store) AND at least 1
  ML evaluation metric (AUC, precision, recall, NDCG, F1, log loss) with a
  before/after or absolute value.
- A resume that reads as data science exploration (notebooks, statistical
  analysis, dashboards) without deployment or serving evidence cannot score
  above 2.5 on persona_fit.
- Model monitoring and drift detection evidence is a strong differentiator
  for mid-level ML engineering; its presence elevates persona_fit toward 4.5.
- Leakage prevention or offline/online feature parity work is a distinct
  quality signal that recruiters for this persona recognize.

## Quality bar examples

Before: "Built and deployed machine learning models for fraud detection."
After: "Trained an XGBoost fraud classifier (1.8M rows, 140 features) that
raised precision@5% recall from 0.62 to 0.81, reducing false-positive fraud
holds by ~23% and recovering an estimated $340k/month in declined-transaction
revenue."

Before: "Worked on model monitoring and alerting."
After: "Implemented population stability index monitoring for 8 production
models using Evidently; paged on-call when PSI exceeded 0.2, catching 3
distribution-shift events before they degraded model AUC below the SLA
threshold."

Before: "Improved the recommendation model."
After: "Migrated the homepage ranking model from a rule-based scorer to a
LightGBM ranker trained on 90-day implicit feedback; offline NDCG@10 rose
from 0.41 to 0.57 and A/B test showed +6.8% 7-day retention over 4 weeks."
