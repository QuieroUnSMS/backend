# Implementation Plan: Guest-First Identity and Optional Registration

**Branch**: `001-user-registration` | **Date**: 2026-11-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-user-registration/spec.md`

## Summary

Implement **guest-first identity** for QuieroUnSMS: issue opaque bearer sessions, persist
checkout/history placeholders server-side, optional upgrade to registered accounts via email or E.164
phone (no verification), complementary contact add, uniqueness enforcement, and suspension.
Follow **TDD** and **API → service → repository → PostgreSQL** layering; extend root `openapi.yaml`
with [contracts/openapi.yaml](./contracts/openapi.yaml) at implementation time.

## Technical Context

**Language/Version**: Python 3.15.2

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, `pydantic-settings`, Uvicorn

**Storage**: PostgreSQL 18.7 — tables `identities`, `session_credentials`,
`identity_checkout_states`, `identity_purchase_history_entries` (see [data-model.md](./data-model.md))

**Testing**: Pytest; unit tests with mocked repositories; integration tests with `TEST_DATABASE_URL`

**Target Platform**: Linux / WSL2 local API server

**Project Type**: Web service (HTTP API)

**Performance Goals**: Session auth and profile reads p95 &lt; 200 ms on local DB; not latency-critical for MVP

**Constraints**: Thin routers; hashed tokens only at rest; no JWT PII; sync SQLAlchemy (consistent with 001)

**Scale/Scope**: ~4 tables, 8 HTTP operations, 3 user stories; foundation for purchase/SMS features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Constraint | Plan compliance |
|------------------------|-----------------|
| I. TDD | Unit + integration tests per story; [quickstart.md](./quickstart.md) |
| II. Layered service–repository | `IdentityService`, `SessionService`; repositories for each aggregate |
| III. MVP-first | Phased US1→US3; no OTP/passwords; placeholders for purchase domain |
| IV. Privacy / minimal PII | Guest default; email/phone only on voluntary registration |
| V. Acceptable use | Suspension flag + 403 on protected routes |
| VI. OpenAPI parity | Feature contract in `contracts/`; merge to root `openapi.yaml` on implement |
| Technical stack table | Python 3.15.2, FastAPI, Pytest, Pydantic, PostgreSQL 18.7, SQLAlchemy |
| Accounts compliance checklist | Documented in [quickstart.md](./quickstart.md) compliance section |

**Pre-Phase 0 gate**: PASS

**Post-Phase 1 gate**: PASS — [research.md](./research.md), [data-model.md](./data-model.md), and contracts preserve layering; no unjustified violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-user-registration/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── openapi.yaml     # Merge into root on implement
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

HTTP contract: merge into `openapi.yaml` at repository root.

```text
src/app/
├── main.py                          # Include identity router
├── core/
│   ├── config.py
│   └── exceptions.py                # IdentityNotFound, DuplicateIdentifier, SuspendedIdentity
├── api/
│   ├── dependencies.py              # get_db, get_current_identity (bearer)
│   └── routes/
│       ├── contacts.py              # existing
│       ├── session.py               # POST /session
│       └── me.py                      # /me/* routes
├── schemas/
│   ├── contact.py
│   └── identity.py                    # Identity, session, checkout, history DTOs
├── services/
│   ├── contact_service.py
│   ├── identity_service.py
│   └── session_service.py
├── repositories/
│   ├── protocols.py
│   ├── identity_repository.py
│   └── session_credential_repository.py
├── models/
│   ├── contact.py
│   └── identity.py                    # ORM models (+ checkout/history)
└── db/
    ├── base.py
    └── session.py

tests/
├── unit/
│   ├── test_contact_service.py
│   ├── test_identity_service.py
│   └── test_session_service.py
└── integration/
    ├── test_contacts_api.py
    └── test_identity_api.py

alembic/versions/                      # New migration for identity tables
```

**Structure Decision**: Extend existing `src/app/` package; identity routes parallel to contacts.

## Complexity Tracking

*(empty — no constitution violations requiring justification)*