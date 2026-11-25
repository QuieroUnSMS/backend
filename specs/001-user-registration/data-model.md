# Data Model: Identity and Session

**Feature**: `001-user-registration` | **Date**: 2026-11-24

## Entity: Identity

Platform visitor or account holder (spec **Key Entities**).

| Field (logical) | Storage column | Type | Rules |
|-----------------|----------------|------|--------|
| Identifier | `id` | UUID, PK | `gen_random_uuid()` at insert |
| Registration status | `registration_status` | `VARCHAR` / PG enum | `guest` or `registered`; default `guest` |
| Email | `email` | `CITEXT` or `VARCHAR(320)` | Nullable; unique when not null; case-insensitive |
| Phone (E.164) | `phone_e164` | `VARCHAR(16)` | Nullable; unique when not null; pattern `^\+[1-9]\d{1,14}$` |
| Suspended | `suspended_at` | `TIMESTAMPTZ` | Null = active; non-null = suspended (FR-011) |
| Created at | `created_at` | `TIMESTAMPTZ`, NOT NULL | Server default `now()` |
| Updated at | `updated_at` | `TIMESTAMPTZ`, NOT NULL | On mutation |

**Invariants**

- `registered` ⇒ at least one of `email`, `phone_e164` is non-null (FR-005).
- `guest` ⇒ both may be null (FR-003).
- No automated purge of guest rows (FR-013).

## Entity: SessionCredential

Opaque bearer binding to one identity.

| Field | Column | Type | Rules |
|-------|--------|------|--------|
| Identifier | `id` | UUID, PK | |
| Identity FK | `identity_id` | UUID, FK → `identities.id`, NOT NULL | ON DELETE RESTRICT |
| Token hash | `token_hash` | `BYTEA` or `CHAR(64)` | SHA-256 of issued token; unique |
| Created at | `created_at` | `TIMESTAMPTZ` | |
| Last used at | `last_used_at` | `TIMESTAMPTZ` | Optional, update on auth |

v1: at most one active credential per identity (simplify); rotate on demand in future.

## Entity: IdentityCheckoutState (placeholder)

| Field | Column | Type | Rules |
|-------|--------|------|--------|
| Identity FK | `identity_id` | UUID, PK, FK | One row per identity |
| Payload | `state` | `JSONB`, NOT NULL | Opaque checkout document |
| Updated at | `updated_at` | `TIMESTAMPTZ` | |

## Entity: IdentityPurchaseHistoryEntry (placeholder)

| Field | Column | Type | Rules |
|-------|--------|------|--------|
| Identifier | `id` | UUID, PK | |
| Identity FK | `identity_id` | UUID, FK | |
| Summary label | `summary` | `VARCHAR(255)` | Human-readable placeholder |
| Created at | `created_at` | `TIMESTAMPTZ` | Append-only (no delete in v1 policy) |

## State transitions (Identity)

```text
[none] --POST /session--> [guest, active]
[guest, active] --POST /me/registration (valid)--> [registered, active]
[registered, active] --PATCH /me/contact--> [registered, active]  (add 2nd identifier)
[*, active] --suspend--> [*, suspended]
[suspended] --auth attempt--> denied (403)
```

Upgrade does **not** create a new identity id (FR-009).

## Indexes

- PK on all tables.
- Unique partial: `LOWER(email)` WHERE email IS NOT NULL.
- Unique partial: `phone_e164` WHERE phone_e164 IS NOT NULL.
- Unique on `session_credentials.token_hash`.
- Index on `session_credentials.identity_id`.
- Index on `identity_purchase_history_entries.identity_id` for list by owner.

## Relationships

```text
Identity 1 --- * SessionCredential
Identity 1 --- 0..1 IdentityCheckoutState
Identity 1 --- * IdentityPurchaseHistoryEntry
```

Future purchase/SMS features reference `identities.id`.

## Mapping to layers

| Layer | Artifact |
|-------|----------|
| API | Pydantic session/identity/me schemas; bearer dependency |
| Service | `IdentityService`, `SessionService` — upgrade, uniqueness, suspension checks |
| Repository | `IdentityRepository`, `SessionCredentialRepository`, activity repositories |
| ORM | SQLAlchemy models ↔ tables above |