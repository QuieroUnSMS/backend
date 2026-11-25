---
description: "Task list for Automated Test Execution in Continuous Integration"
---

# Tasks: Automated Test Execution in Continuous Integration

**Input**: Design documents from `/specs/002-github-actions/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml), [quickstart.md](./quickstart.md)

**Tests**: Not requested for this feature (CI runs existing pytest suites; no new application test files unless CI exposes a gap).

**Organization**: Phases follow user stories — US1 and US3 are both P1; US2 is P2. Deliverables are primarily `.github/workflows/tests.yml` and `README.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: US1, US2, US3 map to [spec.md](./spec.md) user stories
- Paths use repository root per [plan.md](./plan.md)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare version-controlled CI location

- [x] T001 Create `.github/workflows/` directory at repository root per [plan.md](./plan.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Workflow skeleton, triggers, and dependency install — **blocks all user stories**

**⚠️ CRITICAL**: Complete Phase 2 before user story phases

- [x] T002 Create `.github/workflows/tests.yml` with workflow `name`, `on.pull_request.branches: [main]`, `on.push.branches: [main]`, job `tests` on `ubuntu-latest`, `timeout-minutes: 15` per [specs/002-github-actions/contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml)
- [x] T003 Add steps `actions/checkout@v4`, `astral-sh/setup-uv@v5` with `python-version-file: .python-version`, and `uv sync --frozen` in `.github/workflows/tests.yml`
- [x] T004 Ensure job has no `continue-on-error: true` on setup or test steps in `.github/workflows/tests.yml` (FR-007)

**Checkpoint**: Workflow file exists and installs deps on PR/push — ready for test steps

---

## Phase 3: User Story 1 — See test results on every change proposal (Priority: P1) — MVP

**Goal**: Pull requests to `main` run automated unit tests and expose pass/fail on the change (FR-001, FR-002, FR-006)

**Independent Test**: Open PR to `main`; after push, GitHub shows a check for job `tests`; unit pytest step runs; green when `tests/unit` passes, red on intentional unit failure

### Implementation for User Story 1

- [x] T005 [US1] Add step `uv run pytest tests/unit -q` in `.github/workflows/tests.yml` after `uv sync` (non-zero exit fails job)
- [x] T006 [US1] Set contributor-visible job name (e.g. job id `tests` / workflow name `Tests`) in `.github/workflows/tests.yml` so PR checks map to [quickstart.md](./quickstart.md) step 1

**Checkpoint**: PRs to `main` run unit tests with visible check status

---

## Phase 4: User Story 3 — Validate database-dependent behavior in automation (Priority: P1)

**Goal**: Ephemeral PostgreSQL 18.7 per job; `quierounsms_test`; integration pytest with `TEST_DATABASE_URL`; overall check fails if either suite fails (FR-003, FR-005, FR-007, FR-009)

**Independent Test**: Successful workflow log shows postgres service healthy, `CREATE DATABASE quierounsms_test`, integration pytest executed; failing integration test fails job; no repository secrets used

### Implementation for User Story 3

- [x] T007 [US3] Add `services.postgres` with `image: postgres:18.7`, `POSTGRES_USER`/`POSTGRES_PASSWORD` `postgres`, and `pg_isready` health check (`interval: 3s`, `timeout: 5s`, `retries: 10`) in `.github/workflows/tests.yml` per [data-model.md](./data-model.md) ephemeral test database lifetime = job scoped
- [x] T008 [US3] Add step to install `postgresql-client` on the runner (e.g. `apt-get install -y postgresql-client`) before `psql` in `.github/workflows/tests.yml`
- [x] T009 [US3] Add database prep step: `PGPASSWORD=postgres psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -c 'CREATE DATABASE quierounsms_test;'` in `.github/workflows/tests.yml` after unit tests, before integration tests
- [x] T010 [US3] Add integration step with `env.TEST_DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_test` and `uv run pytest tests/integration -q` in `.github/workflows/tests.yml` (schema via existing `tests/conftest.py` session fixtures — no separate Alembic step per [research.md](./research.md))
- [x] T011 [US3] Audit `.github/workflows/tests.yml` for excluded credentials (no Stripe, Grizzly SMS, or production secrets) per [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml) `spec.exclusions`

**Checkpoint**: Full PR runs unit + integration; DB unavailable causes failure, not silent skip

---

## Phase 5: User Story 2 — Protect the integration branch (Priority: P2)

**Goal**: Pushes to `main` run the same test job as pull requests (FR-001, US2 acceptance)

**Independent Test**: Push to `main` triggers workflow; logs show unit and integration steps identical to PR runs

### Implementation for User Story 2

- [x] T012 [US2] Verify `.github/workflows/tests.yml` `on.push.branches` is `[main]` and shares the same `tests` job steps as `pull_request` (no divergent job definitions)

**Checkpoint**: Direct pushes and merges to `main` exercise the same CI bar

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Discoverability and acceptance validation (FR-010, SC-001–SC-005)

- [x] T013 [P] Add **Continuous integration** section to `README.md`: triggers (PR + push to `main`), link to `.github/workflows/tests.yml`, local parity commands matching CI per [specs/002-github-actions/quickstart.md](./quickstart.md)
- [x] T014 Run local parity from [quickstart.md](./quickstart.md): `uv run pytest tests/unit -q` and `uv run pytest tests/integration -q` with `TEST_DATABASE_URL` (SC-003)
- [ ] T015 Push branch and confirm GitHub Actions run is green on clean tree; optional negative check: temporary failing assertion → red PR check per [quickstart.md](./quickstart.md) steps 4–5 (SC-001, SC-002, SC-004)
- [x] T016 If CI fails only on runner (e.g. missing system package, integration skip): apply minimal fix in `.github/workflows/tests.yml` or `tests/conftest.py` and re-run workflow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies
- **Phase 2**: Depends on Phase 1 — blocks US1, US3, US2
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US3)**: Depends on Phase 3 (unit step ordering per contract: unit before DB prep)
- **Phase 5 (US2)**: Depends on Phase 2 (often satisfied when T002 complete; T012 is verification)
- **Phase 6**: Depends on Phases 3–5

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependency on US2/US3 for unit-only MVP
- **US3 (P1)**: After US1 steps in same workflow file — adds Postgres + integration
- **US2 (P2)**: Trigger verification after workflow complete

### Parallel Opportunities

- **T013** [P] with **T014** after workflow file is stable (README vs local test run)
- Phases 3→4→5 are sequential on `.github/workflows/tests.yml` (same file)

### Parallel Example: Polish

```bash
# After CI workflow merged locally on branch:
# Developer A: README update (T013)
# Developer B: local parity run (T014)
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phases 1–2
2. Complete Phase 3 (US1) — PR unit checks
3. **STOP and VALIDATE**: Open PR; confirm unit check green
4. Continue Phase 4 (US3) before merge — both US1 and US3 are P1 in spec

### Full feature (recommended single PR)

1. Phases 1–5 in order on one branch
2. Phase 6 validation before merge to `main`
3. No `openapi.yaml` or `postman_collection.json` changes (constitution VI–VII)

---

## Notes

- Canonical workflow contract: [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml)
- Concurrent PR isolation: each job gets its own Postgres service container ([data-model.md](./data-model.md))
- `CREATE DATABASE` runs once per job on fresh Postgres — no shared CI database
- Avoid adding path filters in v1 unless spec is amended

## Phase 7: Convergence

**Purpose**: Remediation from `/speckit-converge` (2026-11-25)

- [x] T017 In `tests/conftest.py`, when the `CI` environment variable is set and PostgreSQL is not reachable at `TEST_DATABASE_URL`, fail the integration session with an explicit error instead of `pytest.skip`, so GitHub Actions cannot report success with an all-skipped integration suite per FR-007 (partial)