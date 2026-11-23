# Quickstart: Validate Starting Point CRUD

**Feature**: `001-starting-point` | **Date**: 2025-11-16

This guide validates end-to-end behavior against [spec.md](./spec.md) and
[openapi.yaml](../../openapi.yaml) at the repository root. Implementation details live in tasks and
source; commands below assume the standard layout from [plan.md](./plan.md).

## Prerequisites

- Python 3.15.2 (`.python-version` at repo root; `uv python install 3.15.2`)
- PostgreSQL 18.7 reachable via `DATABASE_URL`
- Feature branch or workspace at repo root

## Database with Docker Compose

From repository root:

```bash
docker compose up -d db
```

This starts PostgreSQL **18.7** with databases `quierounsms_dev` and `quierounsms_test`.

## Setup (after implementation)

1. Install dependencies: `uv sync` (uses Python 3.15.2).
2. Copy `.env.example` to `.env` and set `DATABASE_URL` to
   `postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_dev`.
3. Run migrations: `uv run alembic upgrade head`.
4. Start API: `uv run uvicorn app.main:app --reload --app-dir src`.

Interactive docs: `http://localhost:8000/docs` (should match OpenAPI contract paths).

## TDD workflow (constitution)

Per user story priority:

1. Write failing pytest for the story (unit and/or integration as in [research.md](./research.md)).
2. Run pytest — confirm failure.
3. Implement minimal code through service/repository layers.
4. Run pytest — confirm green; refactor.

## Run tests

```bash
# From repository root — start DB first: docker compose up -d db
uv run pytest tests/unit -q

export TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_test
uv run pytest tests/integration -q
```

Integration tests require PostgreSQL; with Compose running they should not be skipped.

## Manual acceptance script

Use `curl` or the Swagger UI. Sample flow (E.164 phone):

| Step | Action | Expected |
|------|--------|----------|
| 1 | `POST /contacts` `{"name":"Ada","phone_e164":"+15551000001"}` | `201`, body includes `id` |
| 2 | `GET /contacts/{id}` | `200`, same name and phone |
| 3 | `GET /contacts` | `200`, array length ≥ 1 |
| 4 | `PATCH /contacts/{id}` `{"name":"Ada L."}` | `200`, updated name |
| 5 | `DELETE /contacts/{id}` | `204` |
| 6 | `GET /contacts/{id}` | `404` |

Negative checks:

| Case | Action | Expected |
|------|--------|----------|
| Duplicate phone | Second `POST` with same `phone_e164` | `409` |
| Invalid phone | `POST` with `phone_e164": "555"` | `422` |
| Empty name | `POST` with `name: ""` | `422` |
| Unknown id | `GET /contacts/00000000-0000-0000-0000-000000000099` | `404` |
| Delete unknown | `DELETE` same uuid | `404` |

## Success criteria mapping

- **SC-001**: Complete manual table above using `/docs` within 15 minutes.
- **SC-002**: All pytest integration tests pass (acceptance scenarios).
- **SC-003**: Negative rows return field-identifying validation or conflict messages.
- **SC-004**: Step 6 returns `404` after delete.

## References

- Data rules: [data-model.md](./data-model.md)
- HTTP contract: [openapi.yaml](../../openapi.yaml)