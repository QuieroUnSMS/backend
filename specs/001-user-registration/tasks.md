---
description: "Task list for Guest-First Identity and Optional Registration"
---

# Tasks: Guest-First Identity and Optional Registration

**Input**: Design documents from `/specs/001-user-registration/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Included — constitution TDD (non-negotiable) and plan testing strategy. Write tests first; confirm failure before implementation.

**Organization**: Phases follow user stories P1 → P2 → P3. Existing contacts stack stays; this feature adds identity.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: US1, US2, US3 map to spec user stories
- Paths use repository root per plan.md (`src/app/`, `tests/`)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Token helpers used by every story (stdlib only; no new packages)

- [x] T001 [P] Implement `generate_session_token` (CSPRNG, URL-safe) and `hash_session_token` (SHA-256) in `src/app/core/security.py` per research.md (store hash only; raw token returned once)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Persistence, schemas, and repositories — **blocks all user stories**

**⚠️ CRITICAL**: Complete Phase 2 before any US phase work

- [x] T002 Add `InvalidSessionError`, `IdentitySuspendedError`, `DuplicateIdentifierError`, and `AlreadyRegisteredError` in `src/app/core/exceptions.py`
- [x] T003 Implement SQLAlchemy models in `src/app/models/identity.py`: `Identity` (`id` UUID PK, `registration_status` `guest`|`registered` default `guest`, `email` VARCHAR(320) nullable, `phone_e164` VARCHAR(16) nullable, `suspended_at` TIMESTAMPTZ nullable, `created_at`/`updated_at` TIMESTAMPTZ NOT NULL); `SessionCredential` (`token_hash` unique, `identity_id` FK ON DELETE RESTRICT); `IdentityCheckoutState` (`identity_id` PK FK, `state` JSONB NOT NULL); `IdentityPurchaseHistoryEntry` (`summary` VARCHAR(255) NOT NULL, `identity_id` FK)
- [x] T004 Add Alembic migration `alembic/versions/002_create_identity_tables.py` with partial unique indexes: `LOWER(email)` WHERE email IS NOT NULL; `phone_e164` WHERE phone_e164 IS NOT NULL; unique `token_hash` per data-model.md
- [x] T005 [P] Define Pydantic models in `src/app/schemas/identity.py`: `IdentityRead`; `SessionBootstrapResponse`; `RegistrationRequest` and `ContactPatchRequest` with exactly one of `email` or `phone_e164`; `phone_e164` pattern `^\+[1-9]\d{1,14}$`; `CheckoutStateWrite`/`CheckoutStateRead`; `PurchaseHistoryCreate` (`summary` max 255) and `PurchaseHistoryEntry`
- [x] T006 Extend `src/app/repositories/protocols.py` with identity, session-credential, checkout, and purchase-history repository protocols
- [x] T007 [P] Implement `src/app/repositories/identity_repository.py` (SQLAlchemy only): create guest, get by id, get by email (case-insensitive), get by phone, set registered fields, set `suspended_at`
- [x] T008 [P] Implement `src/app/repositories/session_credential_repository.py` and checkout/history persistence methods (or `src/app/repositories/identity_activity_repository.py`) matching data-model.md

**Checkpoint**: Foundation ready — user story phases may begin

---

## Phase 3: User Story 1 — Purchase as a guest (Priority: P1) — MVP

**Goal**: Issue guest session; persist and resume checkout state and purchase history without email or phone (FR-001–FR-004, FR-012, FR-013, FR-014)

**Independent Test**: `POST /session` → 201 with `session_token` and `registration_status=guest`; `PUT`/`GET /me/checkout-state` and purchase-history round-trip with the same bearer; missing/invalid bearer on `/me` → 401; no email or phone required

### Tests for User Story 1 (write first — must fail)

- [x] T009 [P] [US1] Add unit tests for session bootstrap and checkout replace/read in `tests/unit/test_session_service.py` (mocked repositories)
- [x] T010 [P] [US1] Add integration tests for `POST /session`, `GET /me`, checkout, and purchase-history in `tests/integration/test_identity_api.py`

### Implementation for User Story 1

- [x] T011 [US1] Implement `SessionService` (create guest + hashed credential; resolve bearer) in `src/app/services/session_service.py`
- [x] T012 [US1] Implement guest checkout and purchase-history methods in `src/app/services/identity_service.py` (no deletion of guest rows)
- [x] T013 [US1] Add `get_current_identity` bearer dependency (401 invalid/missing; do not require email/phone) in `src/app/api/dependencies.py`
- [x] T014 [US1] Implement `POST /session` (201 new guest; 200 if valid bearer; 401 if bearer present but invalid) in `src/app/api/routes/session.py`
- [x] T015 [US1] Implement `GET /me`, `GET`/`PUT /me/checkout-state`, `GET`/`POST /me/purchase-history` in `src/app/api/routes/me.py`
- [x] T016 [US1] Mount session and me routers and map new domain errors in `src/app/main.py`
- [x] T017 [US1] Merge US1 paths from `specs/001-user-registration/contracts/openapi.yaml` into repository-root `openapi.yaml`

**Checkpoint**: User Story 1 independently testable (guest continuity)

---

## Phase 4: User Story 2 — Voluntary registration (Priority: P2)

**Goal**: Upgrade the same identity with email **or** E.164 phone; reject duplicates without merge (FR-005–FR-009)

**Independent Test**: Guest with history `POST /me/registration` with unused email or `phone_e164` → 200 `registered` and same `id` with history intact; taken identifier → 409 and guest unchanged; invalid format → 422; already registered → 422

### Tests for User Story 2 (write first — must fail)

- [x] T018 [P] [US2] Add unit tests for upgrade success, duplicate email/phone, and invalid E.164 in `tests/unit/test_identity_service.py`
- [x] T019 [P] [US2] Add integration tests for `POST /me/registration` (200, 409, 422) in `tests/integration/test_identity_api.py`

### Implementation for User Story 2

- [x] T020 [US2] Implement `register` in `src/app/services/identity_service.py`: guest only; exactly one identifier; store email lowercased; phone must match `^\+[1-9]\d{1,14}$` with no normalization; on conflict raise `DuplicateIdentifierError` without merging or changing the other identity; keep the same `id` and owned activity
- [x] T021 [US2] Implement `POST /me/registration` in `src/app/api/routes/me.py` (200 / 409 / 422)
- [x] T022 [US2] Add `/me/registration` to repository-root `openapi.yaml`

**Checkpoint**: User Stories 1 and 2 both work; upgrade does not fork history

---

## Phase 5: User Story 3 — Complementary contact and suspension (Priority: P3)

**Goal**: Add the second identifier; deny suspended identities (FR-010–FR-012, constitution V)

**Independent Test**: Registered with only email can `PATCH /me/contact` with unused phone (and the reverse); duplicate add → 409 and row unchanged; suspended identity `GET /me` → 403 and no checkout/history body

### Tests for User Story 3 (write first — must fail)

- [x] T023 [P] [US3] Add unit tests for complementary contact and suspension denial in `tests/unit/test_identity_service.py`
- [x] T024 [P] [US3] Add integration tests for `PATCH /me/contact` and suspended `GET /me` → 403 in `tests/integration/test_identity_api.py`

### Implementation for User Story 3

- [x] T025 [US3] Implement `add_complementary_contact` in `src/app/services/identity_service.py` (registered only; field currently null; same uniqueness and E.164 rules as registration; conflict leaves account unchanged)
- [x] T026 [US3] Reject suspended identities in `get_current_identity` with `IdentitySuspendedError` → HTTP 403 and a clear detail, without returning checkout or history, in `src/app/api/dependencies.py` and `src/app/main.py`
- [x] T027 [US3] Implement `PATCH /me/contact` in `src/app/api/routes/me.py`
- [x] T028 [US3] Expose repository `suspend` for tests (no public admin API) and use it from `tests/integration/test_identity_api.py`
- [x] T029 [US3] Add `/me/contact` and 403 responses to repository-root `openapi.yaml`

**Checkpoint**: All three stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Contract parity and quickstart proof

- [x] T030 Confirm repository-root `openapi.yaml` matches `specs/001-user-registration/contracts/openapi.yaml` for identity paths (Constitution VI)
- [x] T031 Run the manual acceptance table in `specs/001-user-registration/quickstart.md` against a local server and fix any spec mismatches
- [x] T032 [P] Use clear Spanish `detail` strings for identity 401/403/409 responses where user-facing, per constitution language constraint, in `src/app/main.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on T001 — **blocks all user stories**
- **US1 (Phase 3)**: Depends on Phase 2
- **US2 (Phase 4)**: Depends on US1 routes and `IdentityService` existing
- **US3 (Phase 5)**: Depends on US2 registration (complementary contact assumes `registered`)
- **Polish (Phase 6)**: Depends on US1–US3

### User Story Dependencies

- **US1 (P1)**: After foundation only — MVP
- **US2 (P2)**: Needs guest session from US1
- **US3 (P3)**: Needs a registered identity from US2 for the happy path; suspension can be tested on a guest once US1 auth exists, but the story checkpoint includes both

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Services before routes
- OpenAPI update in the same story as the routes

### Parallel Opportunities

- T005 can run in parallel with T003–T004 (different files) after T002 is not required for schemas
- T007 and T008 in parallel after T006
- T009 and T010 in parallel; T018 and T019 in parallel; T023 and T024 in parallel

---

## Parallel Example: User Story 1

```bash
# Tests first (different files):
# T009 tests/unit/test_session_service.py
# T010 tests/integration/test_identity_api.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (guest session + checkout/history)
3. Stop and run US1 rows in quickstart.md

### Incremental Delivery

1. US1 guest continuity
2. US2 optional registration without losing history
3. US3 second identifier + suspension
4. Phase 6 OpenAPI parity and full quickstart

---

## Notes

- Do not add OTP, passwords, or real payment gateways
- Do not merge guest data into an existing account on identifier collision
- Do not delete guest identities in this feature (FR-013)
- Phone input is rejected unless it already matches `^\+[1-9]\d{1,14}$`
