# Feature Specification: Starting Point CRUD Example

**Feature Branch**: `001-starting-point`

**Created**: 2025-11-16

**Status**: Draft

**Input**: User description: "Create a basic CRUD example following the constitution principles and technical constraints" slug=starting-point

## Clarifications

### Session 2026-11-16

- Q: On create and update, must the consumer send the phone number already in international E.164 form (including a leading `+`), or may they send other formats and rely on the system to normalize before save? → A: Consumer must send E.164 with leading `+`; non-E.164 input is rejected (no auto-normalization).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a sample contact (Priority: P1)

As an API consumer, I want to register a new contact with a display name and phone number so that
the contact can be used in later messaging workflows.

**Why this priority**: Creation is the minimum viable slice; without it, no other CRUD operation has
meaningful data to work with.

**Independent Test**: Submit a valid new contact and confirm it is stored and retrievable with the
same identifying information and a stable identifier.

**Acceptance Scenarios**:

1. **Given** no existing contact with the same phone number, **When** the consumer submits a valid
   name and phone number, **Then** the system confirms success and returns the new contact
   including a unique identifier.
2. **Given** a submitted name or phone number that fails validation rules, **When** the consumer
   attempts to create a contact, **Then** the system rejects the request with a clear explanation
   and does not create a partial record.
3. **Given** a contact was created successfully, **When** the consumer requests that contact by
   identifier, **Then** the system returns the stored name and phone number.

---

### User Story 2 - Browse and inspect contacts (Priority: P2)

As an API consumer, I want to list contacts and fetch a single contact by identifier so that I can
review and select recipients before sending messages.

**Why this priority**: Read operations are required for verification and daily use after creation
is available.

**Independent Test**: With at least one contact in the system, list and single-fetch operations
return accurate data; requesting an unknown identifier yields a not-found outcome.

**Acceptance Scenarios**:

1. **Given** multiple contacts exist, **When** the consumer requests the contact list, **Then** the
   system returns all contacts with identifier, name, and phone number.
2. **Given** no contacts exist, **When** the consumer requests the contact list, **Then** the
   system returns an empty collection without error.
3. **Given** a valid contact identifier, **When** the consumer requests that contact, **Then** the
   system returns the matching contact.
4. **Given** an identifier that does not exist, **When** the consumer requests that contact,
   **Then** the system reports that the contact was not found.

---

### User Story 3 - Maintain and remove contacts (Priority: P3)

As an API consumer, I want to update or delete a contact so that recipient information stays
accurate and obsolete entries can be removed.

**Why this priority**: Update and delete complete the reference lifecycle but depend on create and
read being in place first.

**Independent Test**: Change a contact’s name or phone, verify persistence; delete a contact and
confirm it no longer appears in list or single-fetch.

**Acceptance Scenarios**:

1. **Given** an existing contact, **When** the consumer submits valid updated name or phone
   values, **Then** the system saves the changes and subsequent reads reflect the new values.
2. **Given** update payload with invalid data, **When** the consumer attempts an update, **Then**
   the system rejects the change and leaves the stored contact unchanged.
3. **Given** an existing contact, **When** the consumer requests deletion, **Then** the system
   removes the contact and it is no longer returned by list or single-fetch.
4. **Given** a delete request for an unknown identifier, **When** the consumer attempts deletion,
   **Then** the system reports that the contact was not found.

---

### Edge Cases

- Duplicate phone number on create or update: system rejects the operation and explains the
  conflict without altering the existing record.
- Extremely long or empty name: validation fails with a clear message; no record is created or
  changed.
- Phone number not in E.164 with leading `+` (including national or local formats): validation
  fails before persistence; the system does not infer country or normalize input.
- Concurrent updates to the same contact: last successful write wins; consumers can rely on
  read-after-write consistency for a single client flow.
- Delete idempotency: deleting an already removed contact returns not-found rather than success.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow consumers to create a contact with a display name and phone number.
- **FR-002**: System MUST assign a unique, stable identifier to each contact at creation time.
- **FR-003**: System MUST validate name and phone number before persisting; invalid input MUST NOT
  create or corrupt stored data. On create and update, phone number MUST be supplied in E.164 form
  with a leading `+`; the system MUST NOT auto-normalize national or local formats.
- **FR-004**: System MUST enforce unique phone numbers across all contacts.
- **FR-005**: System MUST allow consumers to retrieve a single contact by identifier.
- **FR-006**: System MUST allow consumers to retrieve a list of all contacts.
- **FR-007**: System MUST allow consumers to update an existing contact’s name and/or phone number.
- **FR-008**: System MUST allow consumers to delete an existing contact by identifier.
- **FR-009**: System MUST return explicit not-found outcomes for single-fetch, update, and delete
  when the identifier does not exist.
- **FR-010**: System MUST return human-readable error details for validation failures and conflicts
  without exposing internal implementation details.
- **FR-011**: The feature MUST serve as the project’s reference implementation for full
  create-read-update-delete behavior on a single business resource, suitable for onboarding and
  pattern replication.

### Key Entities *(include if feature involves data)*

- **Contact**: A person or party reachable by SMS; attributes include unique identifier, display
  name, and phone number in E.164 form (leading `+`). Phone number is unique across all contacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new team member can complete create, list, read, update, and delete for one
  contact using only published consumer documentation in under 15 minutes on first attempt.
- **SC-002**: 100% of acceptance scenarios in this specification pass in structured acceptance
  testing before the feature is marked done.
- **SC-003**: Invalid inputs (empty name, phone not in E.164 with `+`, duplicate phone) are
  rejected in 100% of tested cases with messages that identify the failing field or rule.
- **SC-004**: After delete, repeated fetch attempts for the same identifier report not-found in 100%
  of tested cases.

## Assumptions

- The example resource is **Contact** (name + phone); no messaging send/receive is in scope for
  this feature.
- Authentication and authorization are out of scope; the example is for local and learning
  environments unless a later feature adds access control.
- One logical tenant; multi-tenancy and organization scoping are out of scope.
- Consumers supply phone numbers already in E.164 with a leading `+`; validation rejects other
  formats without normalization.
- Persistence is durable across process restarts for the deployed example environment.
- Constitution-mandated engineering practices (test-first delivery and layered structure) are
  satisfied during planning and implementation phases, not duplicated as consumer-facing
  requirements in this document.