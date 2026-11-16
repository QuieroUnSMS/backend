---
description: "Task list for Starting Point CRUD Example"
---

# Tasks: Starting Point CRUD Example

**Input**: Design documents from `/specs/001-starting-point/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Included — constitution TDD (non-negotiable) and plan testing strategy. Write tests first; confirm failure before implementation.

**Organization**: Phases follow user stories P1 → P2 → P3 for incremental delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: US1, US2, US3 map to spec user stories
- Paths use repository root per plan.md (`src/app/`, `tests/`)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize greenfield backend layout and tooling

- [x] T001 Create directory tree `src/app/{api/routes,core,db,models,repositories,schemas,services}`, `tests/{unit,integration}`, and `alembic/` per plan.md
- [x] T002 Create `pyproject.toml` with Python 3.15.2, FastAPI, Pydantic v2, pydantic-settings, SQLAlchemy 2.x, Alembic, psycopg, Uvicorn, pytest, httpx
- [x] T003 [P] Add `.env.example` at repository root with `DATABASE_URL` placeholder
- [x] T004 [P] Configure pytest (`testpaths`, `pythonpath` for `src`) in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared layers and persistence — **blocks all user stories**

**⚠️ CRITICAL**: Complete Phase 2 before any US phase work

- [x] T005 Implement `Settings` with `DATABASE_URL` via pydantic-settings in `src/app/core/config.py`
- [x] T006 Implement SQLAlchemy `Base` and session factory in `src/app/db/base.py` and `src/app/db/session.py`
- [x] T007 Define `ContactNotFoundError` and `DuplicatePhoneError` in `src/app/core/exceptions.py`
- [x] T008 Implement SQLAlchemy `Contact` ORM in `src/app/models/contact.py` (`id` UUID PK, `name` VARCHAR(120) NOT NULL, `phone_e164` VARCHAR(16) NOT NULL UNIQUE, `created_at`/`updated_at` TIMESTAMPTZ)
- [x] T009 Initialize Alembic and add initial migration `alembic/versions/` creating `contacts` table matching data-model.md (unique index on `phone_e164`)
- [x] T010 Define `ContactRepositoryProtocol` (`create`, `list`, `get_by_id`, `get_by_phone`, `update`, `delete`) in `src/app/repositories/protocols.py`
- [x] T011 Implement repository CRUD in `src/app/repositories/contact_repository.py` (SQLAlchemy only here)
- [x] T012 Wire `get_db` session and `get_contact_service` in `src/app/api/dependencies.py`
- [x] T013 Create `FastAPI` app and mount contacts router in `src/app/main.py`
- [x] T014 [P] Define `ContactCreate`, `ContactUpdate` (min 1 field), `ContactRead` in `src/app/schemas/contact.py` with `name` length 1–120 and `phone_e164` pattern `^\+[1-9]\d{1,14}$` (no normalization)

**Checkpoint**: Foundation ready — user story phases may begin

---

## Phase 3: User Story 1 — Create a sample contact (Priority: P1) — MVP

**Goal**: Create contact with E.164 phone; retrieve by id (FR-001–004, FR-005 partial)

**Independent Test**: `POST /contacts` with valid body → 201; `GET /contacts/{id}` → 200 with same name and `phone_e164`; duplicate phone → 409; invalid name/phone → 422

### Tests for User Story 1 (write first — must fail)

- [x] T015 [P] [US1] Add unit tests for `ContactService.create` (success, empty name, invalid E.164 without `+`, duplicate phone) in `tests/unit/test_contact_service.py`
- [x] T016 [P] [US1] Add integration tests for `POST /contacts` and `GET /contacts/{contact_id}` happy path and 422 cases in `tests/integration/test_contacts_api.py`

### Implementation for User Story 1

- [x] T017 [US1] Implement `ContactService.create` (trim name, duplicate check via `get_by_phone`) in `src/app/services/contact_service.py`
- [x] T018 [US1] Implement `POST /contacts` (201) and `GET /contacts/{contact_id}` (200/404) thin handlers in `src/app/api/routes/contacts.py`

**Checkpoint**: User Story 1 independently testable (create + get-by-id)

---

## Phase 4: User Story 2 — Browse and inspect contacts (Priority: P2)

**Goal**: List all contacts and fetch single contact; empty list and not-found (FR-005, FR-006, FR-009)

**Independent Test**: `GET /contacts` returns all fields; empty DB → `[]`; unknown id → 404

### Tests for User Story 2 (write first — must fail)

- [x] T019 [P] [US2] Add integration tests for `GET /contacts` (multiple, empty) and `GET /contacts/{contact_id}` 404 in `tests/integration/test_contacts_api.py`

### Implementation for User Story 2

- [x] T020 [US2] Implement `ContactService.list` and `ContactService.get` in `src/app/services/contact_service.py`
- [x] T021 [US2] Implement `GET /contacts` route in `src/app/api/routes/contacts.py`

**Checkpoint**: User Stories 1 and 2 both pass integration tests

---

## Phase 5: User Story 3 — Maintain and remove contacts (Priority: P3)

**Goal**: PATCH and DELETE with validation, conflict, not-found (FR-007–010, edge cases)

**Independent Test**: PATCH updates fields; invalid PATCH leaves row unchanged; DELETE → 204 then GET 404; DELETE unknown → 404

### Tests for User Story 3 (write first — must fail)

- [x] T022 [P] [US3] Add unit tests for `ContactService.update` and `delete` (not found, duplicate phone, invalid payload) in `tests/unit/test_contact_service.py`
- [x] T023 [P] [US3] Add integration tests for `PATCH /contacts/{contact_id}` and `DELETE /contacts/{contact_id}` in `tests/integration/test_contacts_api.py`

### Implementation for User Story 3

- [x] T024 [US3] Implement `ContactService.update` and `ContactService.delete` in `src/app/services/contact_service.py`
- [x] T025 [US3] Implement `PATCH /contacts/{contact_id}` (200/404/409/422) and `DELETE /contacts/{contact_id}` (204/404) in `src/app/api/routes/contacts.py`

**Checkpoint**: Full CRUD per spec acceptance scenarios

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: HTTP error mapping, contract alignment, quickstart validation

- [x] T026 Register exception handlers mapping `ContactNotFoundError` → 404 and `DuplicatePhoneError` → 409 in `src/app/main.py`
- [x] T027 Run end-to-end steps in `specs/001-starting-point/quickstart.md` (pytest + manual table)
- [x] T028 [P] Verify `/docs` OpenAPI matches paths and status codes in `specs/001-starting-point/contracts/openapi.yaml`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** → **Phase 2** → **Phases 3–5** (sequential by priority recommended) → **Phase 6**
- Phase 2 **blocks** all user story work

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no dependency on US2/US3
- **US2 (P2)**: After Phase 2 — uses create from US1 for realistic data but list/get testable with seeded DB
- **US3 (P3)**: After Phase 2 — logically after US1 for update/delete fixtures; tests may create own data

### Within Each User Story

1. Tests (T015–T016, etc.) written and **failing**
2. Service layer
3. API routes
4. `pytest` green before next story

### Parallel Opportunities

- **Phase 1**: T003, T004 parallel after T002
- **Phase 2**: T014 parallel with T005–T013 once T008 schema types known (after T008 or parallel if schemas only need data-model)
- **US1**: T015 ∥ T016; then T017 → T018
- **US2**: T019 then T020 → T021
- **US3**: T022 ∥ T023; then T024 → T025
- **Phase 6**: T028 parallel with T027 after T026

---

## Parallel Example: User Story 1

```bash
# Tests first (parallel):
# T015 tests/unit/test_contact_service.py
# T016 tests/integration/test_contacts_api.py

# Then sequentially:
# T017 src/app/services/contact_service.py
# T018 src/app/api/routes/contacts.py
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (US1)
3. Stop and run `pytest tests/unit tests/integration -q` for US1 scope
4. Demo create + get-by-id

### Incremental Delivery

1. Setup + Foundational → infrastructure ready
2. US1 → MVP (create + get)
3. US2 → list + read completeness
4. US3 → update + delete
5. Polish → quickstart + OpenAPI parity

### Suggested MVP Scope

**Phase 1 + Phase 2 + Phase 3 (through T018)** delivers spec User Story 1 and partial FR-005.

---

## Notes

- All handlers stay thin; business rules only in `src/app/services/contact_service.py`
- No auth, no pagination (full list per FR-006)
- Hard delete per data-model.md
- Phone: consumer-supplied E.164 with leading `+` only (spec clarification 2026-11-16)

---

## Phase 7: Convergence

**Purpose**: Close gaps found by `/speckit-converge` (spec/plan/constitution vs current code)

- [x] T029 Pin Python runtime to 3.15.2 in `pyproject.toml` (`requires-python >=3.15.2,<3.16`) and add `.python-version` with `3.15.2` per Constitution technical constraints (`contradicts`)
- [x] T030 Add integration test in `tests/integration/test_contacts_api.py` that invalid `PATCH` returns 422 and prior contact fields remain unchanged per US3/AC2 (`partial`)
- [x] T031 Add integration test in `tests/integration/test_contacts_api.py` for `PATCH /contacts/{id}` 404 when id is missing per FR-009 (`partial`)
- [x] T032 Add `docker-compose.yml` for PostgreSQL 18.7 dev/test and document `docker compose up` plus `TEST_DATABASE_URL` in `README.md` and `specs/001-starting-point/quickstart.md` so acceptance tests run reliably per SC-002 (`partial`)