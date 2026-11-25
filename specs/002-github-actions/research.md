# Research: Automated Test Execution in Continuous Integration

**Feature**: `002-github-actions` | **Date**: 2026-11-25

## 1. CI platform and workflow placement

- **Decision**: Add `.github/workflows/tests.yml` using GitHub Actions on `ubuntu-latest` hosted
  runners.
- **Rationale**: Matches feature assumptions and repository hosting; version-controlled next to
  application code (FR-008).
- **Alternatives considered**: CircleCI or GitLab CI — rejected (user requested GitHub Actions;
  repo on GitHub).

## 2. Triggers and branch scope

- **Decision**: Run on `pull_request` and `push` to `main` (confirmed default branch via
  `origin/main`).
- **Rationale**: Satisfies FR-001 and user stories US1–US2; covers PR feedback and post-merge
  verification.
- **Alternatives considered**: PR-only (no push) — rejected (spec US2 requires integration branch
  runs); path filters — deferred to post-v1 per spec edge cases.

## 3. Python runtime and dependencies

- **Decision**: Use `astral-sh/setup-uv` with `python-version-file: .python-version` (3.15.2) and
  `uv sync --frozen` when `uv.lock` is present (fallback `uv sync` if lock policy changes).
- **Rationale**: Mirrors README local workflow (FR-004); frozen lock improves reproducibility on
  CI and locally.
- **Alternatives considered**: `actions/setup-python` + pip — rejected (project standard is `uv`).

## 4. PostgreSQL for integration tests

- **Decision**: Declare a job `services.postgres` container `postgres:18.7` with health checks;
  credentials `postgres`/`postgres`; create database `quierounsms_test` via a setup step
  (`psql -c 'CREATE DATABASE quierounsms_test;'`) before integration pytest.
- **Rationale**: Constitution requires PostgreSQL 18.7; local Docker uses the same image and
  [init-databases.sql](../../docker/postgres/init-databases.sql); integration tests expect
  `quierounsms_test` in default URL.
- **Alternatives considered**: Reuse service default DB `postgres` only — rejected (diverges from
  local `TEST_DATABASE_URL`); Docker Compose in CI — rejected (heavier, slower than GHA service
  container).

## 5. Schema setup vs Alembic in CI

- **Decision**: Do **not** run `alembic upgrade head` as a separate CI prerequisite; rely on
  existing integration test session fixtures in [tests/conftest.py](../../tests/conftest.py) that
  call `Base.metadata.create_all` / `drop_all` per session.
- **Rationale**: Local integration runs documented in README only export `TEST_DATABASE_URL` and
  invoke pytest; conftest already provisions schema (FR-005 “equivalent setup”). Keeps CI aligned
  with contributor commands.
- **Alternatives considered**: Mandatory Alembic before integration tests — rejected for v1
  (duplicates ORM sync path tests already use; add later if migration drift tests are introduced).

## 6. Test execution order and job structure

- **Decision**: Single job **Tests** with steps: checkout → setup uv → unit pytest → wait for DB
  healthy → create test DB → export `TEST_DATABASE_URL` → integration pytest.
- **Rationale**: One check status maps cleanly to PR UI (FR-006); unit tests fail fast without
  waiting for Postgres; integration runs only after DB is reachable.
- **Alternatives considered**: Parallel jobs (unit + integration) — acceptable later; rejected for
  v1 simplicity and single required check.

## 7. Secrets and fork pull requests

- **Decision**: Workflow uses only public runner env and service credentials; no repository secrets.
- **Rationale**: FR-009 and spec fork guidance; unit/integration suites use mocks and local DB only.
- **Alternatives considered**: Pull `GITHUB_TOKEN` for packages — not needed (`uv` resolves from
  PyPI in lockfile).

## 8. Timeouts and failure behavior

- **Decision**: Job `timeout-minutes: 15`; fail job on any non-zero pytest exit; do not
  `continue-on-error` for integration suite.
- **Rationale**: FR-007; SC-004 (no silent skip). Integration conftest skips when DB unavailable —
  CI must ensure DB is up so skips do not mask success.
- **Alternatives considered**: Retry flaky tests — out of scope until flakiness is observed.

## 9. Documentation touchpoints

- **Decision**: Extend root [README.md](../../README.md) with a short “Continuous integration”
  section linking workflow and local parity commands; feature [quickstart.md](./quickstart.md) for
  acceptance validation (FR-010).
- **Rationale**: Spec requires discoverability without reading YAML.
- **Alternatives considered**: CI-only docs in specs — rejected (README is canonical for
  contributors).