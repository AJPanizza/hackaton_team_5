# Review Pipeline or Bundle

Perform a comprehensive review of a pipeline, job, or bundle configuration before promotion to a higher environment.

## Steps

1. Ask the user:
   - Which file(s) or resource(s) should be reviewed? (provide paths or describe the scope)
   - What is the promotion target? (dev → test, or test → prod)
   - Are there any specific concerns to focus on?

2. Read all relevant files:
   - `databricks.yml` — bundle structure and targets
   - `variables.yml` — variable definitions
   - `resources/*.yml` — all job, pipeline, schema, and app definitions
   - Source code files in `src/` that are referenced by the resources
   - Test files in `tests/` to assess coverage

3. Run static analysis using the project's virtual environment (`.venv/`):

   ```bash
   .venv/bin/ruff check src/
   .venv/bin/mypy src/
   ```

   - Capture the output of both commands.
   - If either command fails (non-zero exit code), surface the errors in the review report under **FAIL** items.
   - If the `.venv/` directory does not exist, note it as a **WARN** and skip this step.

4. Invoke the **solution-architect** agent to conduct the review. The architect must evaluate:

   **SunnyData Standards Compliance:**
   - [ ] Naming follows SunnyData conventions (`@.claude/skills/org-custom/org-naming-conventions/SKILL.md`)
   - [ ] All required tags present on job compute (`Business_Unit`, `Team`, `Product`, `Project`, `Budget_Code`)
   - [ ] No hardcoded values — all parameters in `variables.yml`
   - [ ] Medallion architecture correctly implemented (bronze/silver/gold layers)

   **Security and Governance:**
   - [ ] Service principal permissions set on test/prod targets
   - [ ] No credentials or secrets in code or YAML
   - [ ] PII handling follows data governance standards (`@.claude/skills/org-custom/org-data-governance/SKILL.md`)
   - [ ] Data quality checks implemented (DLT expectations or explicit validation)

   **Operational Readiness:**
   - [ ] Email notifications wired to `${var.emails_to_notify}`
   - [ ] Webhook notifications wired to `${var.webhook_id}`
   - [ ] Job timeouts set appropriately
   - [ ] `max_concurrent_runs: 1` for ETL jobs
   - [ ] Schedules paused in dev, active in test/prod
   - [ ] Compute uses `SPOT_WITH_FALLBACK` and `SINGLE_USER` security mode

   **Test Coverage:**
   - [ ] `pytest --cov=src --cov-fail-under=80` configuration present in `pyproject.toml`
   - [ ] Unit tests exist for all `src/` modules
   - [ ] Test fixtures available in `tests/fixtures/`

   **Bundle Configuration:**
   - [ ] `databricks bundle validate` passes for the target environment
   - [ ] `dev_resources/` excluded from prod sync (if applicable)
   - [ ] `root_path` explicitly set for test/prod targets

5. Produce a structured review report:
   - **PASS** items (compliant)
   - **FAIL** items (must fix before promotion)
   - **WARN** items (recommended improvements)
   - **Recommended next steps** with specific file references

6. If there are FAIL items, do not proceed with deployment. List exactly what needs to be fixed and which agent should handle each fix.
