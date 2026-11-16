# Data Model: Contact

**Feature**: `001-starting-point` | **Date**: 2025-11-16

## Entity: Contact

Represents a party reachable by SMS (spec **Key Entities**).

| Field (logical) | Storage column | Type | Rules |
|-----------------|----------------|------|--------|
| Identifier | `id` | UUID, PK, NOT NULL | Assigned at insert (`gen_random_uuid()` or app-generated uuid4) |
| Display name | `name` | `VARCHAR(120)`, NOT NULL | Trim whitespace; length 1–120 after trim |
| Phone (E.164) | `phone_e164` | `VARCHAR(16)`, NOT NULL, UNIQUE | Must match E.164; unique across all rows |
| Created at | `created_at` | `TIMESTAMPTZ`, NOT NULL | Set once at insert, server default `now()` |
| Updated at | `updated_at` | `TIMESTAMPTZ`, NOT NULL | Updated on successful PATCH |

## Validation rules (application + DB)

1. **Name**: Reject empty or whitespace-only; max 120 characters (FR-003).
2. **Phone**: Reject invalid E.164 before insert/update (FR-003); duplicate phone returns conflict
   without mutating existing row (FR-004, edge cases).
3. **Identifier**: Immutable after create (FR-002).

## Relationships

None in v1 (single-tenant, no auth, no messaging links).

## State transitions

```text
[non-existent] --CREATE--> [active]
[active] --PATCH (valid)--> [active]
[active] --DELETE--> [removed / non-existent]
```

- **Read list**: Returns all `[active]` contacts; empty set if none.
- **Read by id**: `[active]` only; `[removed]` → not found (FR-009).
- **Update**: Only `[active]`; invalid payload leaves row unchanged (acceptance P3).
- **Delete**: Removes row physically (hard delete) for simplicity in reference implementation;
  subsequent reads return not found (SC-004).

## Indexes

- Primary key on `id`.
- Unique index on `phone_e164` (enforces FR-004 at persistence layer).

## Mapping to layers

| Layer | Artifact |
|-------|----------|
| API | Pydantic `ContactCreate`, `ContactUpdate`, `ContactRead` |
| Service | Domain rules: duplicate phone check before write, not-found handling |
| Repository | CRUD methods: `create`, `list`, `get_by_id`, `update`, `delete`, `get_by_phone` |
| ORM | SQLAlchemy `Contact` model ↔ `contacts` table |