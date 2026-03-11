# New Feature Scaffold

Scaffold a new data feature end-to-end from requirements through implementation-ready tasks, following SunnyData standards.

## Steps

1. Ask the user:
   - What is the feature description and business goal?
   - What Databricks resources will be created or modified? (jobs, pipelines, apps, schemas)
   - What is the target environment? (dev / test / prod)
   - Is this a net-new project or an addition to an existing bundle?

2. Invoke the **project-manager** agent to:
   - Produce a technical specification using the SunnyData task template
   - Break the work into well-scoped tasks mapped to the appropriate agent
   - Flag which tasks require solution-architect review
   - Load `@.claude/skills/org-custom/org-pm-workflows/SKILL.md` before producing output

3. Invoke the **solution-architect** agent to:
   - Review the technical specification for architectural soundness
   - Validate against SunnyData approved patterns (`@.claude/skills/org-custom/org-architecture-patterns/SKILL.md`)
   - Check governance compliance (`@.claude/skills/org-custom/org-data-governance/SKILL.md`)
   - Confirm naming follows conventions (`@.claude/skills/org-custom/org-naming-conventions/SKILL.md`)
   - Produce an approval or a list of required changes before implementation begins

4. Based on the approved specification, invoke the **python-data-engineer** agent to scaffold the initial structure:
   - `databricks.yml` and `variables.yml` (if new bundle)
   - `resources/schemas.yml` (bronze/silver/gold)
   - Job and/or pipeline resource YAML files
   - `src/` directory with package structure and bootstrap notebook
   - `tests/conftest.py` and test stubs
   - `pyproject.toml` with UV and pytest configuration

5. If the feature includes a user-facing app, invoke the **uiux-expert** agent to scaffold:
   - `resources/{app_name}.app.yml`
   - `src/app/app.yaml`, `main.py`, and `requirements.txt`

6. Present the complete task breakdown and scaffolded files to the user. List next steps clearly.
