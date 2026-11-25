# Feature Specification: Guest-First Identity and Optional Registration

**Feature Branch**: `001-user-registration`

**Created**: 2026-11-24

**Status**: Draft

**Input**: User description: "Assessment handoff from `.specify/assessments/user-registration/decision.md` — guest-first unified identity (phased), optional email/phone registration, no verification at signup." slug=user-registration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Purchase as a guest without signing up (Priority: P1)

As a privacy-minded buyer, I want to use the service and complete purchases without providing email
or phone or creating an account, so that I can get a temporary number without sharing identifying
credentials up front.

**Why this priority**: Guest-first checkout is the core product promise and unblocks purchase flows
that depend on a stable owner for checkout and history.

**Independent Test**: A new visitor receives a durable session identity, attaches activity to it,
leaves and returns with the same client-held session, and sees the same in-progress checkout and
purchase history without ever supplying email or phone.

**Acceptance Scenarios**:

1. **Given** a first-time visitor with no session, **When** they begin using the service,
   **Then** the system issues a unique guest identity and a session credential the client can store.
2. **Given** a valid guest session, **When** the visitor records purchase-related activity (e.g.,
   in-progress checkout or completed purchase placeholders owned by this feature’s domain),
   **Then** that activity is associated with the guest identity and retrievable only through that
   session.
3. **Given** a guest who left mid-checkout, **When** they return later presenting the same session
   credential on the same client, **Then** they can resume from the saved checkout state and see
   prior purchases tied to that guest identity.
4. **Given** a visitor, **When** they attempt core flows that require an identity owner,
   **Then** the system MUST NOT require email, phone, or account creation before proceeding as a
   guest.

---

### User Story 2 - Upgrade voluntarily to a registered account (Priority: P2)

As a guest who wants continuity or recognition, I want to attach an email **or** phone number to my
existing guest identity, so that I become a registered account holder without losing what I already
did as a guest.

**Why this priority**: Optional registration is an MVP goal; upgrade must not fork history or force
a new anonymous identity.

**Independent Test**: From an active guest session with stored activity, supply one valid identifier
(email or E.164 phone); the same logical identity becomes registered and all prior guest-owned
activity remains visible under that identity.

**Acceptance Scenarios**:

1. **Given** a guest with stored activity, **When** they submit a valid email that is not already
   taken, **Then** the identity becomes registered with that email and retains all prior activity.
2. **Given** a guest with stored activity, **When** they submit a valid phone number (E.164 with
   leading `+`) that is not already taken, **Then** the identity becomes registered with that phone
   and retains all prior activity.
3. **Given** a guest attempting upgrade, **When** the submitted email or phone already belongs to
   another account, **Then** the system rejects the upgrade with a clear conflict message, remains a
   guest, and does not merge or overwrite the other account.
4. **Given** a guest attempting upgrade, **When** they submit invalid email or phone format,
   **Then** the system rejects the input without partial registration.

---

### User Story 3 - Complete profile and enforce acceptable use (Priority: P3)

As a registered user, I want to add the complementary contact method (phone if I registered with
email, or email if I registered with phone) when I choose, and as the platform I need to suspend
identities that violate acceptable use.

**Why this priority**: Second identifier and enforcement complete the identity lifecycle but depend
on guest and upgrade flows.

**Independent Test**: Add the missing identifier on a registered account; attempt duplicate add;
suspend an identity and confirm subsequent requests are refused with a clear outcome.

**Acceptance Scenarios**:

1. **Given** a registered user with only email on file, **When** they add a valid unused phone
   number, **Then** the account stores both identifiers.
2. **Given** a registered user with only phone on file, **When** they add a valid unused email,
   **Then** the account stores both identifiers.
3. **Given** an identifier already in use elsewhere, **When** a registered user tries to add it,
   **Then** the system rejects the change and leaves the account unchanged.
4. **Given** an identity (guest or registered) flagged for prohibited use, **When** they present a
   session credential, **Then** the system refuses service with a clear suspension outcome and does
   not expose purchase or checkout data.

---

### Edge Cases

- Missing, unknown, or malformed session credential: reject protected operations; allow only issuance
  of a new guest identity where appropriate.
- Guest presents a credential issued by the server but never stored client-side: treat as new visitor
  (no cross-client recovery for guests).
- Registered user on a new browser/device without password or OTP sign-in: no access to prior account
  until a future sign-in feature (out of scope here).
- Concurrent upgrade attempts from the same guest with two different identifiers: first successful
  upgrade wins; later attempts follow registered-user rules.
- Email case normalization: treat addresses as case-insensitive for uniqueness (industry default).
- Identity remains guest indefinitely if the user never upgrades; guest records are not deleted by
  routine retention sweeps.
- International phone numbers must be E.164 with leading `+`; other formats are rejected without
  auto-normalization (consistent with project contact rules).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST issue a unique guest identity and session credential to each new visitor
  who does not present a valid existing credential.
- **FR-002**: System MUST authenticate requests using the client-presented session credential and
  resolve it to exactly one identity (guest or registered).
- **FR-003**: System MUST NOT require email, phone, or account creation for guest identities to
  perform flows that this feature’s dependent product areas label as guest-allowed (including
  owning checkout and purchase history placeholders).
- **FR-004**: System MUST persist guest-owned checkout state and purchase history server-side, keyed
  to the guest identity, until upgraded or until product policy changes outside this spec.
- **FR-005**: System MUST allow a guest to upgrade to a registered account by supplying at least one
  of: valid email or valid E.164 phone (with leading `+`).
- **FR-006**: System MUST NOT require identity verification (OTP, magic link, email confirmation) at
  account creation or upgrade in this release.
- **FR-007**: System MUST enforce global uniqueness of email and phone across registered accounts;
  upgrade MUST fail if the chosen identifier is already taken.
- **FR-008**: System MUST NOT automatically merge a guest’s data into an existing account when
  identifiers collide; the user MUST be prompted to supply a different identifier (reject and
  reprompt).
- **FR-009**: System MUST preserve all activity associated with a guest identity when that identity
  successfully upgrades to registered status.
- **FR-010**: System MUST allow a registered user to add the complementary identifier (email or
  phone) later, subject to the same uniqueness and format validation rules.
- **FR-011**: System MUST support marking an identity as suspended for acceptable-use violations and
  MUST deny operational access for suspended identities with a clear, user-safe explanation.
- **FR-012**: System MUST reject session credentials that are invalid, unknown, or belong to a
  suspended identity when accessing protected capabilities.
- **FR-013**: System MUST NOT delete guest identities or their stored activity as part of standard
  automated retention in this release (per product policy).
- **FR-014**: System MUST collect and expose only the minimum identity fields needed for this
  feature: session binding, optional email, optional phone, registration status (guest vs.
  registered), and suspension status.

### Key Entities *(include if feature involves data)*

- **Identity**: The platform’s representation of a visitor or account holder; holds registration
  status (guest or registered), optional email, optional phone (E.164 when present), suspension
  state, and creation/update timestamps. One identity owns all linked activity.
- **Session credential**: An opaque, server-issued token presented by the client on subsequent
  requests; maps to exactly one identity. Must not embed PII.
- **Owned activity (checkout and purchase history)**: Server-stored records representing in-progress
  checkout and completed purchase summaries tied to an identity; detailed purchase/SMS behavior
  belongs to sibling features but MUST reference the identity defined here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, 100% of guest-only journeys complete without email or phone
  entry while still retrieving saved checkout state after a simulated return visit on the same
  client.
- **SC-002**: In acceptance testing, 100% of successful upgrade scenarios retain pre-upgrade
  activity visible on the same identity.
- **SC-003**: In acceptance testing, 100% of attempts to register with an already-taken email or
  phone are rejected without creating duplicate accounts or altering the conflicting account.
- **SC-004**: In acceptance testing, 100% of suspended identities are blocked from protected
  capabilities with an explanatory outcome.
- **SC-005**: Qualitative product goal: the default happy path allows a first purchase without
  prior registration, aligned with privacy positioning in the product charter.

## Assumptions

- Purchase, payment (simulated), and SMS features will consume identity ownership via this feature;
  they are not specified here beyond requiring a stable identity key.
- Real payment gateways (SPEI, Stripe) and password-based login are out of scope; a fake/simulated
  payment path may proceed without stronger identity proof.
- Cross-device or cross-browser access for **registered** users without a future sign-in mechanism
  is out of scope; continuity on the same client after upgrade is in scope.
- No verification at signup is an accepted product risk for this release.
- Guest session credentials are stored by the client (cookies, session storage, or local storage);
  the server is the source of truth for identity and owned activity.
- Phone numbers on accounts follow the same E.164-with-`+` validation policy as the contacts
  reference feature.
- Acceptable-use suspension rules align with constitution and `docs/welcome.md`; detailed legal copy
  lives in policy documents, not this spec.
- Indefinite guest retention is intentional; operational and privacy impacts are acknowledged and may
  require policy updates outside this feature.

## Dependencies and Out of Scope

**In scope for this feature**: Guest issuance, session authentication, persistence of identity-linked
checkout/history placeholders, voluntary upgrade, second-identifier add, uniqueness, suspension.

**Out of scope**: OTP or magic-link verification; passwords and explicit login flows; real SPEI/Stripe;
merging guest data into an existing account on collision; cross-device guest merge; SMS provider,
catalog, and live SMS UI; defining full purchase catalog behavior.