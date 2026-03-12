# Population Health Intelligence Platform

## Project Overview

**Challenge**: Build a pre-built Lakehouse pipeline unifying EHR, claims, lab, and device data into a longitudinal patient record — with care gap detection and a Claude-powered agentic intervention system.

**Domain**: Patient Engagement / Population Health
**Platform**: Databricks Lakehouse
**Scope**: Unify 8 HLS data sources into a medallion pipeline, detect care gaps per patient, and let an AI agent generate and log personalized outreach interventions backed by Lakebase PostgreSQL.

---

## Architecture

```
Bronze (team_five_bronze — populated from hackathon.hls)
  patients | diagnoses | encounters | lab_results
  medications | claims | adherence | device_telemetry
        │
        ▼  (Spark batch jobs — NO Declarative Pipelines)
Silver (team_five_silver)
  patient_longitudinal_silver   ← patients + labs + meds + diagnoses
  care_events_silver            ← encounters + diagnoses unified timeline
        │
        ▼
Gold (team_five_gold)
  care_gaps_gold                ← per-patient gap flags + priority_score
  population_health_summary_gold← aggregate KPIs for dashboard
        │
        ├──► Genie Space (natural language BI over gold tables)
        │
        ▼
Care Gap Agent (Databricks Job)
  reads top-N patients by priority_score
  calls Claude API → personalized outreach message
  writes to Lakebase PostgreSQL (intervention_log)
        │
        ▼
Streamlit Dashboard (Databricks App)
  Page 1: Population Overview (KPI cards, gap distribution)
  Page 2: Care Gap Registry (filterable patient table)
  Page 3: Agent Actions (trigger agent, view intervention_log)
```

---

## Evaluation Criteria Alignment

| Criteria | How We Address It |
|----------|------------------|
| **Business Value** | Care gap detection is a $3.7B problem for payers/health systems. HbA1c gaps, low adherence, readmission risk — all real clinical pain points. |
| **Databricks Usage** | Genie space over gold tables for NL BI; Lakebase PostgreSQL for transactional agent state |
| **Agentic Factor** | Agent reads gold, calls Claude, **writes** to Lakebase — transactional action, not just display |
| **Presentation** | 5-step demo: dashboard → Genie → registry → agent trigger → intervention log |

---

## Medallion Schema Design

### Bronze — `team_five_bronze` (pre-populated)
8 tables copied from `hackathon.hls`: patients, diagnoses, encounters, lab_results, medications, claims, adherence, device_telemetry. No transformations — raw as received.

### Silver — `team_five_silver`

**`patient_longitudinal_silver`**
- Base: patients table (demographics, risk_tier, insurance_type, has_cgm)
- Enriched with: latest HbA1c value + date (from lab_results WHERE test_name='HbA1c')
- Enriched with: medication summary (avg_pdc_score, active_med_count, total_med_adherence_gaps from adherence)
- Enriched with: latest primary diagnosis (icd10_code, diagnosis_desc, diagnosis_date)
- Adds: `_silver_ts` (ingestion watermark)

**`care_events_silver`**
- Union of encounters + diagnoses into a single chronological event timeline per patient
- Normalised columns: event_id, patient_id, event_date, event_type, event_subtype, icd10_code, readmission_30d, length_of_stay, discharge_disposition
- Adds: `_silver_ts`

### Gold — `team_five_gold`

**`care_gaps_gold`**
Per-patient care gap flags computed from silver + bronze device_telemetry:

| Flag | Logic |
|------|-------|
| `hba1c_gap` | primary_condition is diabetes AND (no HbA1c OR last HbA1c > 365 days ago) |
| `low_medication_adherence` | avg_pdc_score < 0.80 |
| `high_readmission_risk` | any readmission_30d=1 encounter in last 90 days |
| `uncontrolled_glucose` | mean glucose > 180 OR hypo_event_count >= 2 (last 30 days, device_telemetry) |
| `gap_count` | sum of all boolean gap flags cast to int |
| `priority_score` | weighted sum × risk_tier_weight (Very High=2.0, High=1.5, Medium=1.0, Low=0.5) — weights: readmission 2.5, glucose 2.0, adherence 1.5, hba1c 1.0 |

Also carries: full_name, age, primary_condition, insurance_type, risk_tier, mean_glucose, hypo_event_count, avg_pdc_score, latest_hba1c_date, as_of_date.

**`population_health_summary_gold`**
Single-row aggregate KPIs: total_patients, patients_with_gaps, pct_with_gaps, avg_gap_count, high_risk_count, per-gap-type counts, total_cost_at_risk (from claims for patients with gap_count > 0), snapshot_date.

---

## Care Gap Agent

**File**: `src/population_health/agent/care_gap_agent.py`

```
run_care_gap_agent(spark, catalog, gold_schema, lakebase_host, lakebase_db, anthropic_api_key, top_n=10)
  1. Read care_gaps_gold ORDER BY priority_score DESC LIMIT top_n
  2. For each patient:
     a. Identify highest-priority gap_type
     b. build_care_gap_prompt(patient, gap_type)  → prompt_builder.py
     c. Call claude-sonnet-4-6 → outreach_message
     d. write_intervention(conn, record)          → lakebase.py
  3. Return count of interventions written
```

**Lakebase `intervention_log` table** (PostgreSQL, auto-created on first run):
```sql
CREATE TABLE IF NOT EXISTS intervention_log (
    intervention_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id        VARCHAR(20)  NOT NULL,
    intervention_ts   TIMESTAMPTZ  DEFAULT now(),
    care_gap_type     VARCHAR(50),
    outreach_message  TEXT,
    channel           VARCHAR(20),
    status            VARCHAR(20)  DEFAULT 'pending',
    agent_run_id      VARCHAR(50)
)
```

Connection: `user='token'`, `password=DATABRICKS_TOKEN`, `sslmode='require'`

---

## Genie Space

Configured over `team_five_gold.care_gaps_gold` and `team_five_gold.population_health_summary_gold`.

Sample questions pre-loaded:
- "Which patients have the most care gaps?"
- "What percentage of diabetic patients have an HbA1c gap?"
- "Show high-risk patients with low medication adherence"
- "What is the total cost at risk by insurance type?"
- "Which patients had a 30-day readmission in the last 90 days?"

---

## Streamlit Dashboard (3 Pages)

**Page 1 — Population Overview**
KPI cards (total patients, % with gaps, high-risk count, cost at risk) + bar chart of gap types + pie by risk tier. Source: `population_health_summary_gold`.

**Page 2 — Care Gap Registry**
Filters: risk_tier, primary_condition, insurance_type. Sortable dataframe with color-coded priority_score. Source: `care_gaps_gold`.

**Page 3 — Agent Actions**
"Run Care Gap Agent (Top 10)" button → triggers Databricks Job via SDK → polls run status → shows `intervention_log` from Lakebase (latest 50 rows: patient_id, gap_type, outreach_message preview, channel, status, timestamp).

---

## File Structure

```
src/population_health/
  __init__.py
  silver/
    __init__.py
    patient_longitudinal.py   # build_patient_longitudinal(spark, catalog, bronze, silver)
    care_events.py            # build_care_events(spark, catalog, bronze, silver)
  gold/
    __init__.py
    care_gaps.py              # build_care_gaps(spark, catalog, silver, bronze, gold)
    population_summary.py     # build_population_summary(spark, catalog, gold)
  agent/
    __init__.py
    care_gap_agent.py         # run_care_gap_agent(...)
    lakebase.py               # get_connection, ensure_table, write_intervention
    prompt_builder.py         # build_care_gap_prompt(patient, gap_type) → str

src/population_health/
  pipeline_entrypoint.py      # notebook bootstrap → calls silver + gold build functions
  agent_entrypoint.py         # notebook bootstrap → calls run_care_gap_agent

resources/
  pipeline.job.yml            # Databricks Job: runs pipeline_entrypoint (silver + gold)
  agent_job.job.yml           # Databricks Job: runs agent_entrypoint (on-demand + scheduled)
  genie.yml                   # Genie space over gold tables

general_resources/src/app/app.py   # 3-page Streamlit dashboard (replace placeholder)

tests/population_health/
  __init__.py
  test_care_gaps.py
  test_prompt_builder.py
  test_lakebase.py            # mock psycopg2
  test_population_summary.py
```

---

## Variables (`variables.yml` additions)

```yaml
variables:
  lakebase_host:
    default: ""
    description: "Hostname of the Lakebase PostgreSQL instance (fill after deploy)"
  lakebase_db_name:
    default: "hackathon_db"
  warehouse_id:
    default: ""
    description: "SQL warehouse ID for Genie space"
```

---

## Agents Available

| Agent | Role | When to Use |
|-------|------|-------------|
| `solution-architect` | Architecture decisions, governance review | Design choices, pre-deployment review |
| `python-data-engineer` | Spark batch jobs, ETL, tests | Writing pipelines, notebooks, jobs |
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
- **Catalog**: `team_5_hackaton`
- **Bronze schema**: `team_five_bronze` (pre-populated from `hackathon.hls`)
- **Silver schema**: `team_five_silver`
- **Gold schema**: `team_five_gold`
- **Two-bundle strategy**: `hackathon-five` (pipeline + agent + Genie) | `hackathon-five-general-resources` (Lakebase DB + Databricks App)

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
- **No Declarative Pipelines (DLT)**: Use plain Spark batch jobs only

---

## PII & Governance

HLS data is PHI (Protected Health Information). All patient-identifiable fields must:
- Be tagged with `pii: true` in Unity Catalog column properties
- Use row/column-level security where appropriate
- Never appear in logs or error messages
- Follow de-identification before cross-environment promotion (test/prod use synthetic data in dev)

---

## Test Fixtures

Mock datasets live in `fixtures/` and must be used for all local unit tests. They follow the production data dictionary exactly.

### `fixtures/patients.csv` — 12 patients
| Field | Notes |
|-------|-------|
| `patient_id` | Format `PAT` + 6-digit int |
| `has_cgm` | 8 patients = `1` (CGM enrolled), 4 = `0` |
| `risk_tier` | Mix: Low (2), Medium (3), High (3), Very High (2) (for non-cgm patients) |
| `primary_condition` | Mostly Type 2 Diabetes; also Hypertension, COPD, Heart Failure, Obesity |
| `insurance_type` | Commercial, Medicare, Medicaid (no Uninsured in this fixture) |
| PHI fields | `full_name`, `email`, `phone`, `address` — synthetic only, never real data |

**CGM-enrolled patients** (valid FK targets for `device_telemetry`):
`PAT000001`, `PAT000002`, `PAT000004`, `PAT000005`, `PAT000007`, `PAT000008`, `PAT000010`, `PAT000011`

### `fixtures/device_telemetry.csv` — 60 readings
| Field | Notes |
|-------|-------|
| `reading_id` | Format `CGM` + 8-digit int |
| `patient_id` | Only CGM-enrolled patients (`has_cgm=1`) |
| `device_type` | `CGM` (primary) and `Insulin Pump` (co-readings on alert events) |
| `device_model` | Dexcom G7, Libre 3, Medtronic 780G, Omnipod 5 |
| `reading_ts` | 5-minute intervals; all timestamps before 2026-03-11 (no future data) |
| `glucose_mg_dl` | Full range covered: hypo (<70), normal (70–180), hyper (>180) |
| `insulin_units` | `0.0` for CGM rows; `1.0–7.0` for Insulin Pump rows |
| `is_hypoglycemic` | `1` when glucose < 70 (PAT000002, PAT000010 have hypo sequences) |
| `is_hyperglycemic` | `1` when glucose > 180 (PAT000001, PAT000005, PAT000007, PAT000008) |
| `alert_triggered` | `1` when glucose outside 70–180 |
| `variability_cv` | Range 0.155–0.461; PAT000002, PAT000005, PAT000008 exceed CV > 0.36 threshold |

---

## Demo Script (5 minutes)

1. **[0:00–0:30]** Hook: "Payers lose $3.7B/year to preventable gaps in care. We built a platform that finds them and acts on them — automatically."
2. **[0:30–1:30]** Population Overview dashboard: KPI cards, gap distribution chart.
3. **[1:30–2:30]** Genie: "Which uninsured diabetic patients have an HbA1c gap?" → instant NL answer.
4. **[2:30–3:30]** Care Gap Registry → filter to "Very High" risk → inspect patient gaps.
5. **[3:30–4:30]** Click "Run Care Gap Agent" → job triggers → intervention_log fills with Claude-generated personalized messages. **This is the agentic moment.**
6. **[4:30–5:00]** Close: "One bundle deploy, three data layers, an AI agent that acts — not just alerts."

---

## Hackathon Deliverable

A single unified Databricks Asset Bundle deployable with `databricks bundle deploy`, demonstrating:
1. **Bronze → Silver → Gold** batch Spark pipeline (patient longitudinal record + care gap detection)
2. **Genie Space** for natural language BI over gold tables
3. **Care Gap Agent** (Claude API + Lakebase write) for agentic intervention
4. **Streamlit Dashboard** (Databricks App) with population health view + agent trigger
