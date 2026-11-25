# Quickstart: Validate Guest-First Identity

**Feature**: `002-user-registration` | **Date**: 2026-11-24

End-to-end validation against [spec.md](./spec.md), [data-model.md](./data-model.md), and
[contracts/openapi.yaml](./contracts/openapi.yaml) (merged into root `openapi.yaml` when implemented).

## Prerequisites

- Python 3.15.2, PostgreSQL 18.7 (`docker compose up -d db`)
- `DATABASE_URL` / `TEST_DATABASE_URL` per [README](../../README.md)

## Setup (after implementation)

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --app-dir src
```

## TDD workflow

Per user story P1 → P3 in [spec.md](./spec.md):

1. Add failing pytest (unit: services with mocked repositories; integration: HTTP + DB).
2. Implement through `api` → `services` → `repositories` layers.
3. Merge identity paths into repository-root [openapi.yaml](../../openapi.yaml).

## Run tests

```bash
uv run pytest tests/unit -q
export TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_test
uv run pytest tests/integration -q
```

## Manual acceptance (curl)

Set `TOKEN` from step 1 response `session_token`. Use header: `Authorization: Bearer $TOKEN`.

| Step | Story | Action | Expected |
|------|-------|--------|----------|
| 1 | US1 | `POST /session` (no auth) | `201`, `session_token`, `identity.registration_status` = `guest` |
| 2 | US1 | `PUT /me/checkout-state` `{"state":{"step":"payment"}}` | `200`, state persisted |
| 3 | US1 | `POST /me/purchase-history` `{"summary":"Test purchase"}` | `201` |
| 4 | US1 | New curl with same `TOKEN`: `GET /me/checkout-state` | `200`, same state |
| 5 | US1 | `GET /me/purchase-history` | `200`, array includes entry |
| 6 | US2 | `POST /me/registration` `{"email":"buyer@example.com"}` | `200`, `registered` |
| 7 | US2 | `GET /me` | `200`, email set; history unchanged count |
| 8 | US2 | Second guest + `POST /me/registration` same email | `409`, guest unchanged |
| 9 | US3 | `PATCH /me/contact` `{"phone_e164":"+525512345678"}` | `200`, both identifiers |
| 10 | US3 | Suspended identity (test fixture / admin hook): `GET /me` | `403` |

Negative checks:

| Case | Expected |
|------|----------|
| `GET /me` without bearer | `401` |
| Invalid phone on registration | `422` |
| Register when already `registered` | `422` |
| `PATCH /me/contact` duplicate phone | `409` |

## Success criteria mapping

| ID | Validation |
|----|------------|
| SC-001 | Steps 1–5 without email/phone until step 6 optional |
| SC-002 | Step 7 still lists step 3 history |
| SC-003 | Step 8 |
| SC-004 | Step 10 |

## Compliance checklist (planning)

- Data minimization: identity stores only email, phone, session binding, suspension.
- No verification at signup (documented product risk).
- Acceptable use: suspension blocks protected routes (FR-011).
- Retention: no automated guest purge in v1 (FR-013).