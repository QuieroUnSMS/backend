# Data Model: Continuous Integration Artifacts

**Feature**: `002-github-actions` | **Date**: 2026-11-25

This feature does not add application database tables. The entities below are **logical** objects
represented by GitHub Actions runs, logs, and ephemeral CI infrastructure (per spec **Key Entities**).

## Entity: CI run

One automated execution bound to a single commit.

| Field (logical) | Source | Rules |
|-----------------|--------|--------|
| Commit SHA | `github.sha` | Immutable for the run |
| Ref / event | `github.ref`, `github.event_name` | `pull_request` or `push` |
| Workflow name | Workflow metadata | e.g. “Tests” |
| Job status | GitHub Checks API | `success`, `failure`, `cancelled`, `skipped` |
| Started / completed | Run timestamps | Used for SC-001 (within 10 minutes) |
| Log URL | Actions run page | Diagnosable output for FR-007 |

**Invariants**

- One failing step ⇒ overall check **failure** (FR-007).
- Run MUST NOT use production external credentials (FR-009).

## Entity: Test suite outcome

Aggregated pytest result for a suite category within one CI run.

| Field | Values | Rules |
|-------|--------|--------|
| Suite | `unit`, `integration` | Both required in full pass (SC-004) |
| Command | Documented pytest invocation | Matches README / quickstart |
| Exit code | `0` or non-zero | Non-zero fails CI run |
| Skipped (unintended) | Integration with DB down | MUST NOT occur in healthy CI |

**Relationships**

- Many suite outcomes (2) belong to one **CI run**.
- **Integration** suite outcome depends on **Ephemeral test database** availability.

## Entity: Ephemeral test database

PostgreSQL instance scoped to one job.

| Field | CI value | Rules |
|-------|----------|--------|
| Engine | PostgreSQL 18.7 (service container) | Constitution stack |
| Host | `localhost` from job perspective | Service port mapping |
| Database name | `quierounsms_test` | Align with local Docker init |
| Credentials | `postgres` / `postgres` | Non-production only |
| Lifetime | Job start → job end | Destroyed with job (isolation per FR concurrent PRs) |
| Connection URL | `TEST_DATABASE_URL` env | Consumed by pytest/conftest |

**State**

```text
[provisioning] → [healthy] → [tests running] → [destroyed]
```

Failure to reach `healthy` before integration pytest ⇒ CI run **failure** (spec edge case).

## Entity: Workflow definition (versioned config)

Stored in `.github/workflows/tests.yml` (implementation artifact).

| Aspect | Contract |
|--------|----------|
| Triggers | `pull_request`, `push` → `main` |
| Required env | `TEST_DATABASE_URL` for integration step |
| Service | `postgres:18.7` with health check |
| Check visibility | Job conclusion surfaces on PR / branch |

See [contracts/ci-pipeline.yaml](./contracts/ci-pipeline.yaml).