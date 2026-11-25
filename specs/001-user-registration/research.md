# Research: Guest-First Identity and Optional Registration

**Feature**: `001-user-registration` | **Date**: 2026-11-24

## 1. Session credential transport and format

- **Decision**: Opaque bearer token in `Authorization: Bearer <token>` on protected routes; token is
  32+ bytes from a CSPRNG, URL-safe base64-encoded for client storage (cookies/localStorage).
- **Rationale**: Meets FR-002 without embedding PII; familiar HTTP pattern; aligns with OWASP
  guidance on high-entropy server-issued session IDs.
- **Alternatives considered**: JWT with embedded claims — rejected (risks PII leakage and bypasses
  server-side revocation for suspension); client-generated UUID — rejected (FR-001/FR-012).

## 2. Persisting credentials at rest

- **Decision**: Store only `SHA-256(token)` (hex or bytea) in `session_credentials` table; raw token
  returned once at issuance/rotation. Constant-time compare on lookup.
- **Rationale**: DB leak does not grant session hijack; supports multiple active credentials per
  identity if needed later (single credential per identity for v1 simplicity).
- **Alternatives considered**: Plaintext token column — rejected for security posture.

## 3. Identity model (guest vs registered)

- **Decision**: Single `identities` row per visitor; `registration_status` enum `guest` |
  `registered`; optional `email` and `phone_e164` with partial unique indexes (unique when not
  null); email compared case-insensitively via `LOWER(email)` unique index.
- **Rationale**: FR-009 upgrade in place without row split; FR-007/FR-008 uniqueness on registered
  fields; matches spec entity “Identity”.
- **Alternatives considered**: Separate `guests` and `users` tables — rejected (merge/link
  complexity per assessment research).

## 4. Owned activity placeholders

- **Decision**: `identity_checkout_state` (one JSON document per identity, replaces on write) and
  `identity_purchase_history` (append-only list of summary records: id, label, created_at) until
  purchase feature owns a richer schema.
- **Rationale**: Satisfies US1 acceptance for resume/history without designing full commerce
  domain; foreign key `identity_id` for sibling features.
- **Alternatives considered**: Embed in session row only — rejected (FR-004 server persistence).

## 5. Upgrade and profile mutations

- **Decision**:
  - `POST /me/registration` body: exactly one of `email` or `phone_e164` for guest→registered.
  - `PATCH /me/contact` body: add complementary field when `registered` and other field null.
  - On unique violation → HTTP 409 with stable error code/message (no merge).
- **Rationale**: FR-005, FR-008, FR-010; Spanish/English messages delegated to API i18n layer later.
- **Alternatives considered**: Auto sign-in to existing account on collision — rejected by spec.

## 6. Suspension

- **Decision**: `identities.suspended_at` nullable timestamp; `is_suspended` derived or boolean;
  suspended identities fail auth dependency with **403** and clear `detail` (FR-011/FR-012).
- **Rationale**: Constitution V acceptable use; operator suspension via future admin tooling — v1
  exposes repository method + integration test fixture to suspend by identity id (no public admin
  API in this feature unless needed for quickstart).
- **Alternatives considered**: Delete guest on abuse — rejected (indefinite retention policy).

## 7. Session bootstrap

- **Decision**:
  - `POST /session` with no body (or empty) when no bearer token → create guest + return token +
    identity summary.
  - Optional: same endpoint accepts valid bearer → **200** with existing identity (session refresh
    read).
- **Rationale**: FR-001 clear entry; invalid token on protected routes → **401**; missing token on
  `/session` bootstrap only.

## 8. Testing strategy (TDD)

- **Decision**: Unit tests on `IdentityService` / `SessionService` with mocked repositories; integration
  tests for full US1–US3 flows against PostgreSQL test DB per constitution.
- **Rationale**: Same pattern as `001-starting-point`.
- **Alternatives considered**: Auth-only mocks without DB — insufficient for unique constraints.

## 9. OpenAPI and contract location

- **Decision**: Feature contract drafted in
  `specs/001-user-registration/contracts/openapi.yaml`; implementation phase merges paths/schemas
  into repository-root `openapi.yaml` in the same change set (Constitution VI).
- **Rationale**: Spec Kit parity during plan; single canonical file at root for clients.

## Resolved clarifications

All Technical Context fields in [plan.md](./plan.md) are decided; no outstanding NEEDS CLARIFICATION.