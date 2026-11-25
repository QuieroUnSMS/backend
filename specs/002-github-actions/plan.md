# Implementation Plan: Automated Test Execution in Continuous Integration

**Branch**: `002-github-actions` | **Date**: 2026-11-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-github-actions/spec.md`

## Summary

Add a GitHub Actions workflow that runs the existing **unit** and **integration** pytest suites on
every pull request to `main` and every push to `main`. Use `uv` with Python **3.15.2**, a
**postgres:18.7** service container, create `quierounsms_test`, set `TEST_DATABASE_URL`, and fail the
check on any setup or test failure. Document parity commands in README. No API, OpenAPI, or Postman
changes.

## Technical Context

**Language/Version**: Python 3.15.2 (`.python-version`)

**Primary Dependencies**: `uv`, Pytest, SQLAlchemy, FastAPI (existing app deps via `uv.lock`)

**Storage**: Ephemeral PostgreSQL 18.7 per CI job (`quierounsms_test`); no persistent CI state

**Testing**: `uv run pytest tests/unit -q`; `uv run pytest tests/integration -q` with `TEST_DATABASE_URL`

**Target Platform**: GitHub-hosted `ubuntu-latest` runners

**Project Type**: Web service backend — infrastructure feature (workflow YAML + docs)

**Performance Goals**: Full pipeline completes within spec SC-001 window (10 minutes) under normal load

**Constraints**: No production secrets; integration schema via existing `tests/conftest.py` session
fixtures (not separate Alembic step in CI — see [research.md](./research.md))

**Scale/Scope**: One workflow file, README section, no application code changes required for core goal

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Constraint | Plan compliance |
|------------------------|-----------------|
| I. TDD | CI runs existing unit + integration pytest; supports PR gate for untested behavior |
| II. Layered architecture | No application layer changes in v1 |
| III. MVP-first | Scoped to test automation only |
| IV–V Privacy / acceptable use | No PII or prod provider access in workflow |
| VI. OpenAPI parity | No HTTP API change |
| VII. Postman parity | No collection change |
| Technical stack | Python 3.15.2, Pytest, PostgreSQL 18.7, `uv` — aligned |
| Development Workflow | Mirrors README test commands; version-controlled workflow |

**Pre-Phase 0 gate**: PASS

**Post-Phase 1 gate**: PASS — [research.md](./research.md), [data-model.md](./data-model.md),
[contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml), and [quickstart.md](./quickstart.md) add
no API scope and no unjustified stack deviations.

## Project Structure

### Documentation (this feature)

```text
specs/002-github-actions/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1 — logical CI entities
├── quickstart.md        # Phase 1 — validation guide
├── contracts/
│   └── ci-pipeline.yaml # Phase 1 — workflow contract
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
.github/
└── workflows/
    └── tests.yml        # Implement per contracts/ci-pipeline.yaml

tests/
├── unit/
└── integration/

README.md                # Add Continuous integration section (FR-010)
```

**Structure Decision**: Deliverable is workflow config under `.github/workflows/` plus README; no
changes under `src/app/` unless tests require CI-specific fixes discovered during implement.

## Complexity Tracking

*(empty — no constitution violations requiring justification)*

## Phase 0 & Phase 1 Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Research | [research.md](./research.md) | Complete |
| Data model | [data-model.md](./data-model.md) | Complete |
| Contract | [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml) | Complete |
| Quickstart | [quickstart.md](./quickstart.md) | Complete |

## Implementation Notes (for `/speckit-tasks`)

1. Create `.github/workflows/tests.yml` matching [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml).
2. Ensure Postgres health check passes before `CREATE DATABASE` and integration pytest.
3. Prefer `uv sync --frozen` when lockfile is committed.
4. Update [README.md](../../README.md) with CI trigger summary and local parity commands.
5. Validate on a PR: green on clean branch, red on intentional test failure (per quickstart).