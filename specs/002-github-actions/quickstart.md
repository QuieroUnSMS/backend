# Quickstart: Validate GitHub Actions Test Workflow

**Feature**: `002-github-actions` | **Date**: 2026-11-25

Validates [spec.md](./spec.md) success criteria using local parity runs and (after implementation)
GitHub Checks.

**Contract**: [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml)

## Prerequisites

- Python 3.15.2 (`uv python install 3.15.2` if needed)
- PostgreSQL 18.7 for local parity (`docker compose up -d db` per [README](../../README.md))
- GitHub repository with Actions enabled (for remote validation)

## Local parity (SC-003)

Commands MUST match what the workflow runs:

```bash
uv sync
uv run pytest tests/unit -q
export TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_test
uv run pytest tests/integration -q
```

Expected: both commands exit `0` on `main` at implementation time.

## After implementation — workflow file

Confirm repository contains:

```text
.github/workflows/tests.yml
```

Aligned with [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml) (triggers, Postgres 18.7,
`uv sync`, unit then integration pytest).

## GitHub validation (SC-001, SC-002, SC-004)

| Step | Story | Action | Expected |
|------|-------|--------|----------|
| 1 | US1 | Push branch; open PR to `main` | “Tests” (or workflow job) check appears on PR |
| 2 | US1 | Wait for run | Check completes within 10 minutes; green if tests pass |
| 3 | US2 | Merge to `main` | Push event runs same workflow; check on commit |
| 4 | SC-002 | Introduce failing test on branch; push | PR check **red** |
| 5 | SC-004 | Open successful run logs | Unit and integration pytest steps both executed |

## Negative checks

| Case | Expected |
|------|----------|
| Postgres service fails to start (simulate broken config in fork branch) | Job **failure**, not success with integration skipped |
| `uv sync` fails (broken lockfile) | Job **failure** before tests |
| Unit test failure | Job fails without running integration (if ordered unit-first) or fails at unit step |

## README update (FR-010)

After implementation, [README.md](../../README.md) MUST include a **Continuous integration** bullet
or section stating:

- PRs and pushes to `main` run unit + integration tests on GitHub Actions
- Local commands above reproduce CI behavior

## Success criteria mapping

| ID | Validation |
|----|------------|
| SC-001 | Quickstart step 1–2 on a real PR |
| SC-002 | Quickstart step 4 |
| SC-003 | Local parity commands |
| SC-004 | Quickstart step 5 (log inspection) |
| SC-005 | Maintainer reads PR checks only (step 2 green/red) |

## Compliance / constitution (planning)

- **I. TDD**: CI enforces existing pytest suites; no bypass for untested merges via automation gap.
- **VI–VII OpenAPI / Postman**: No HTTP surface change; root `openapi.yaml` and
  `postman_collection.json` unchanged by this feature.
- **Layering / MVP**: Not applicable (infrastructure-only).