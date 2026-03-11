# Hackathon: Connected Device Intelligence & Next-Best-Action

## Project Overview

**Challenge**: Build a unified pipeline from raw CGM (Continuous Glucose Monitor) stream → actionable patient recommendation.

**Domain**: Patient Engagement / Digital Health
**Platform**: Databricks Lakehouse
**Scope**: Ingest real-time device telemetry (CGM glucose readings, insulin doses, wearable signals), fuse with EHR and pharmacy data, run a next-best-action model, and deliver personalized nudges/education directly to patients or care teams.

---

## Architecture: End-to-End Pipeline

```
CGM Stream (Kafka/Event Hub)
        │
        ▼
  [Bronze Layer]  ← Raw device telemetry, EHR feeds, pharmacy data
        │           Auto Loader / Spark Structured Streaming
        ▼
  [Silver Layer]  ← Cleaned, joined, patient-resolved records
        │           CGM + EHR + pharmacy fusion, SCD Type 2 patient dim
        ▼
  [Gold Layer]    ← Feature store, risk scores, next-best-action signals
        │           ML feature engineering, clinical thresholds
        ▼
  [NBA Model]     ← Next-Best-Action inference (Databricks Model Serving)
        │
        ▼
  [Notification]  ← Personalized nudge / education content (Databricks App)
```

---

## Key Data Sources

| Source | Type | Description |
|--------|------|-------------|
| CGM Device | Streaming | Glucose readings (mg/dL), timestamps, device ID |
| Insulin Pump | Streaming | Dose events, basal/bolus rates |
| Wearables | Streaming | Heart rate, activity, sleep (optional enrichment) |
| EHR | Batch/CDC | Diagnoses, medications, lab results, care plans |
| Pharmacy | Batch | Prescription fills, adherence history |

---

## Databricks Platform Components

| Layer | Databricks Feature | Purpose |
|-------|--------------------|---------|
| Ingestion | Auto Loader + Structured Streaming | Real-time CGM ingest into Bronze |
| Transformation | Spark Declarative Pipelines (DLT) | Bronze → Silver → Gold medallion |
| Feature Engineering | Feature Store | Patient-level features for NBA model |
| ML Inference | Model Serving (serverless endpoint) | Real-time NBA scoring |
| Notification App | Databricks Apps (Streamlit or FastAPI) | Care team / patient dashboard |
| Orchestration | Databricks Jobs | Pipeline scheduling and triggers |
| Governance | Unity Catalog | Data lineage, PII tagging, access control |

---

## Medallion Schema Design

### Bronze — `cgm_bronze`
Raw CGM events, exactly as received. No transformations. Schema-on-read with Auto Loader schema inference disabled (explicit schema only).

### Silver — `cgm_silver`
- Patient-resolved records (join on device_id → patient_id via EHR)
- Cleaned glucose readings (null handling, unit normalization)
- Fused with latest EHR snapshot (diagnoses, active meds)
- SCD Type 2 patient dimension for historization

### Gold — `patient_features_gold`
- Rolling glucose statistics (mean, std, time-in-range, hypo events)
- Adherence scores (CGM wear time, insulin dosing gaps, pharmacy refill rate)
- Risk stratification features (HbA1c proxy, nocturnal hypoglycemia flag)
- Ready for Feature Store registration and NBA model consumption

---

## Next-Best-Action Model

**Approach**: Rule-based triage + ML ranking
1. **Triage rules**: Hard clinical thresholds (e.g., glucose < 70 → urgent alert)
2. **ML ranking**: Personalized recommendation ranking from historical engagement data
3. **Content generation**: Claude API for dynamic nudge/education text personalization

**Actions available**:
- Urgent clinical alert (care team notification)
- Adherence nudge (patient push notification)
- Educational content (personalized diabetes management tip)
- Pharmacy refill reminder
- Care team escalation trigger

---

## Agents Available

| Agent | Role | When to Use |
|-------|------|-------------|
| `solution-architect` | Architecture decisions, governance review | Design choices, pre-deployment review |
| `python-data-engineer` | Spark/DLT code, ETL, tests | Writing pipelines, notebooks, jobs |
| `uiux-expert` | Databricks Apps, Streamlit, FastAPI | Patient/care team dashboard |
| `project-manager` | Specs, task breakdown, ADRs | Planning, decomposing features |
| `databricks-general` | Workspace ops, UC queries, resource discovery | Ad-hoc Databricks tasks |

---

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/new-feature` | Scaffold a new data feature end-to-end |
| `/review-pipeline` | Pre-promotion review (dev → test → prod) |
| `/deploy-to-dev` | Deploy bundle to dev workspace |
| `/static-code-checks` | Run Ruff + Mypy on `src/` |

---

## Workspace & Environment

- **Dev/Test/Prod workspace**: `https://dbc-56f60291-144c.cloud.databricks.com/`
- **Service principal** (test/prod): `d5741de9-42fd-4183-9002-67714017b4cc`
- **Three-environment strategy**: dev → test → prod (promote via bundle targets)

---

## Code Standards (Non-Negotiable)

- **Package manager**: UV (`uv init`, `uv sync`, `uv build --wheel`)
- **Linting**: Ruff + Mypy (via `nbqa` for notebooks)
- **Testing**: pytest with 80%+ coverage (`--cov src --cov-fail-under=80`)
- **Schema**: Always explicit — never infer in production
- **Variables**: No hardcoded values — everything in `variables.yml`
- **Compute**: `SPOT_WITH_FALLBACK` + `SINGLE_USER` security mode
- **Tags**: All resources must carry `Business_Unit`, `Team`, `Product`, `Project`, `Budget_Code`
- **Functional style**: No mutable global/class state; small, testable functions
- **Notebooks**: Bootstrap-only in production (call one entry-point function from `src/`)

---

## PII & Governance

CGM and EHR data is PHI (Protected Health Information). All patient-identifiable fields must:
- Be tagged with `pii: true` in Unity Catalog column properties
- Use row/column-level security where appropriate
- Never appear in logs or error messages
- Follow de-identification before cross-environment promotion (test/prod use synthetic data in dev)

---

## Hackathon Deliverable

A single unified Databricks pipeline demonstrating:
1. **Raw CGM stream ingestion** (simulated or live) into Bronze Delta table
2. **Streaming transformation** through Silver (patient resolution + EHR fusion)
3. **Gold feature computation** (glucose stats, adherence, risk flags)
4. **NBA model inference** triggered on new Gold records
5. **Patient/care team notification** via a Databricks App UI

All in one Databricks Asset Bundle, deployable with `databricks bundle deploy`.
