# Research: Starting Point CRUD Example

**Feature**: `001-starting-point` | **Date**: 2025-11-16

## 1. Application layout and dependency injection

- **Decision**: Package layout `src/app/` with FastAPI `APIRouter` for contacts; dependencies
  provide `AsyncSession` (or sync `Session`) and `ContactService` per request.
- **Rationale**: Matches constitution layering; enables pytest overrides of repository/service in
  unit tests without spinning up HTTP.
- **Alternatives considered**: Monolithic `main.py` with inline DB calls — rejected (violates
  repository pattern and testability).

## 2. Database access and migrations

- **Decision**: SQLAlchemy 2.0 declarative models; Alembic for schema versioning; UUID primary
  key column `id` (PostgreSQL `uuid`, server default `gen_random_uuid()`).
- **Rationale**: Stable identifiers per FR-002; standard PostgreSQL 18 practice; migrations keep
  onboarding reproducible.
- **Alternatives considered**: Integer serial IDs — simpler but less representative for public
  API identifiers; auto-increment exposure in URLs is weaker for a reference API.

## 3. Phone number validation

- **Decision**: Store `phone_e164` as `VARCHAR(16)` with UNIQUE constraint; validate at Pydantic
  schema layer using E.164 pattern (`^\+[1-9]\d{1,14}$`) plus optional `phonenumbers` parse for
  clearer error messages in service tests.
- **Rationale**: Spec assumes E.164-style rules; DB uniqueness enforces FR-004 even if application
  layer regresses.
- **Alternatives considered**: National-format storage only — rejected (SMS domain needs
  international normalization).

## 4. HTTP semantics and error model

- **Decision**:
  - `POST /contacts` → 201 + body; 409 on duplicate phone; 422 on validation
  - `GET /contacts`, `GET /contacts/{id}` → 200; empty list allowed; 404 for unknown id
  - `PATCH /contacts/{id}` → 200; 404; 409 on phone conflict; 422 on validation
  - `DELETE /contacts/{id}` → 204 on success; 404 if missing (not idempotent 204 per spec edge case)
- **Rationale**: Aligns with spec acceptance scenarios and OpenAPI contract.
- **Alternatives considered**: RFC 7807 Problem Details — good future enhancement; for reference
  CRUD, FastAPI `detail` arrays suffice for FR-010.

## 5. Testing strategy (TDD)

- **Decision**:
  - **Unit**: `ContactService` with mocked `ContactRepositoryProtocol` (create duplicate, not
    found, happy paths).
  - **Integration**: API tests against real PostgreSQL (docker-compose or test container) covering
    all acceptance scenarios; run pytest before implementation completes each story.
- **Rationale**: Constitution requires both layers; service tests keep Red–Green cycles fast.
- **Alternatives considered**: In-memory SQLite — faster but diverges from PostgreSQL 18.7
  constraint; use only for optional local hack, not CI target.

## 6. Configuration

- **Decision**: `pydantic-settings` `Settings` with `DATABASE_URL` from environment; `.env.example`
  for local dev (documented in quickstart, not committed secrets).
- **Rationale**: Constitution mandates Pydantic for settings.
- **Alternatives considered**: Raw `os.environ` — rejected.

## 7. Async vs sync SQLAlchemy

- **Decision**: Sync SQLAlchemy session + sync route functions for the reference feature (simpler
  onboarding); FastAPI runs sync endpoints in threadpool.
- **Rationale**: CRUD reference clarity over async complexity; can migrate to `AsyncSession` in a
  later feature without changing service contracts.
- **Alternatives considered**: Full async stack — better at scale but higher learning curve for
  starting point.

## Resolved clarifications

All Technical Context fields in [plan.md](./plan.md) are decided; no outstanding NEEDS CLARIFICATION.