# Implementation Plan: Starting Point CRUD Example

**Branch**: `001-starting-point` | **Date**: 2025-11-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-starting-point/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Deliver a reference **Contact** CRUD HTTP API as the project’s onboarding baseline: create, list,
read, update, and delete contacts (display name + E.164 phone) with validation, unique phone
enforcement, and clear error responses. Implementation follows constitution **TDD** and **API →
service → repository → PostgreSQL** layering using **Python 3.15.2**, **FastAPI**, **Pydantic**,
**SQLAlchemy**, and **Pytest**.

## Technical Context

**Language/Version**: Python 3.15.2

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.x, Uvicorn (ASGI server), Alembic
(migrations), `phonenumbers` or Pydantic-compatible E.164 validation helper

**Storage**: PostgreSQL 18.7 (`contacts` table)

**Testing**: Pytest, `httpx` (async API client), pytest fixtures for DB (integration);
`unittest.mock` for service unit tests with mocked repositories

**Target Platform**: Linux server / local development (WSL2-compatible)

**Project Type**: Web service (HTTP API)

**Performance Goals**: Not critical for reference feature; p95 &lt; 500 ms for CRUD on local DB
with up to 10k contacts is sufficient

**Constraints**: Constitution stack only; thin routers; no auth in v1; durable persistence across
restarts

**Scale/Scope**: Single resource (`Contact`), five endpoints, ~15–25 source modules plus tests;
foundation for future SMS features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Constraint | Plan compliance |
|------------------------|-----------------|
| TDD (non-negotiable) | Red–Green–Refactor per user story; pytest at unit (services) and integration (API + DB) layers defined in [quickstart.md](./quickstart.md) |
| Layered architecture + service–repository | Routers delegate to `ContactService`; service uses `ContactRepository` protocol; SQLAlchemy only in repository/ORM layer |
| Python 3.15.2, FastAPI, Pytest, Pydantic, PostgreSQL 18.7, SQLAlchemy | Reflected in Technical Context and [research.md](./research.md) |
| Pydantic for API schemas and settings | Request/response models in `schemas/`; `Settings` via `pydantic-settings` |
| No business logic in route handlers | Routes: parse, call service, map exceptions to HTTP |

**Pre-Phase 0 gate**: PASS (no violations)

**Post-Phase 1 gate**: PASS — [data-model.md](./data-model.md) and [contracts/openapi.yaml](./contracts/openapi.yaml) preserve layering and spec behaviors (404, 409, 422); no extra complexity requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-starting-point/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── openapi.yaml     # Phase 1
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks — not yet created)
```

### Source Code (repository root)

```text
src/
└── app/
    ├── main.py                 # FastAPI app factory
    ├── core/
    │   ├── config.py           # Pydantic Settings (DATABASE_URL, etc.)
    │   └── exceptions.py       # Domain errors → HTTP mapping helpers
    ├── api/
    │   ├── dependencies.py     # DB session, service injection
    │   └── routes/
    │       └── contacts.py     # Thin CRUD routes
    ├── schemas/
    │   └── contact.py          # ContactCreate, ContactUpdate, ContactRead
    ├── services/
    │   └── contact_service.py  # Validation orchestration, duplicate rules
    ├── repositories/
    │   ├── protocols.py        # ContactRepositoryProtocol
    │   └── contact_repository.py
    ├── models/
    │   └── contact.py          # SQLAlchemy Contact ORM
    └── db/
        ├── base.py
        └── session.py

tests/
├── unit/
│   └── test_contact_service.py
└── integration/
    └── test_contacts_api.py

alembic/                      # Migrations (initial contacts table)
pyproject.toml                # Dependencies and pytest config
```

**Structure Decision**: Single-package layout under `src/app/` matching constitution layer
direction (inward dependencies). Greenfield repo; this feature establishes the initial tree.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(empty — no violations)*