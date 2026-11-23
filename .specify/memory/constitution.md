<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: None renamed (I–II unchanged)
- Added principles: III. MVP-First Product Scope; IV. Privacy and Minimal PII; V. Legal Compliance and Acceptable Use
- Added sections: Product Context (preamble under title)
- Modified sections: Technical Constraints (providers, payments, market, languages); Development Workflow (MVP gates, compliance)
- Removed sections: None
- Follow-up TODOs: None
- Source: docs/welcome.md (last update 2026-11-23)
-->

# QuieroUnSMS Backend Constitution

QuieroUnSMS is a platform for purchasing temporary phone numbers to receive OTP/SMS verification
codes from social networks and applications. The backend supports resale of numbers via
specialized provider APIs, per-user payment, and real-time SMS delivery to clients. This
constitution governs how the API and domain services are built in service of that product.

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)

All production behavior MUST be developed using test-driven development. For each change,
tests MUST be written or updated first, executed to confirm failure where new behavior is
expected, then implementation MUST proceed until tests pass. The Red–Green–Refactor cycle MUST
be followed. Pull requests or merges MUST NOT introduce untested behavior. Rationale: TDD
locks intent, prevents regressions, and keeps the FastAPI surface and domain logic evolvable
under Pytest.

### II. Layered Architecture with Service–Repository Pattern

The backend MUST use a layered architecture combined with the service–repository pattern.
HTTP/route handlers (API layer) MUST remain thin: validation, mapping, and orchestration
only. Business rules and use cases MUST live in service classes. Data access MUST be isolated
in repository abstractions backed by SQLAlchemy; services MUST NOT embed raw SQL or ORM query
details except through repositories. Dependencies MUST point inward (API → services →
repositories → persistence). Rationale: clear boundaries improve testability (services tested
with mocked repositories), maintainability, and alignment with PostgreSQL persistence.

### III. MVP-First Product Scope

**Priority 1** MUST remain a functional MVP: temporary number purchase, service and country
selection, integration with the designated SMS provider, and real-time SMS visibility for the
user. Post-MVP capabilities (e.g., persistent number/SMS history for logged-in users,
multi-language beyond the initial focus) MUST NOT block MVP delivery and MUST be introduced
only through explicit Spec Kit features. User flows MUST support registration and login where
required, while honoring optional registration where the product allows anonymous or
low-friction sessions. Rationale: The project is in definition phase; scope discipline avoids
building ahead of validated user value described in the product charter.

### IV. Privacy and Minimal PII

The backend MUST collect and retain only data necessary to provide the service (account where
used, payment handling, and temporary numbers in use). User-facing flows MUST default to not
requiring personally identifiable information beyond what is needed for purchase, delivery, or
legal obligations. SMS content MUST be stored only for the convenience window defined by product
policy and MUST be deleted afterward; APIs MUST NOT encourage submission of sensitive personal
data through temporary numbers. Design choices MUST reflect the primary market (Mexico), including
privacy motivations tied to telecommunications regulation, without expanding data collection
beyond stated privacy commitments. Rationale: Product positioning depends on privacy and
minimal identification; the API must not undermine that trust.

### V. Legal Compliance and Acceptable Use

Features that provision numbers, relay SMS, or manage accounts MUST enforce acceptable use:
legitimate verification, privacy, testing, or personal use only; end users MUST NOT resell,
share, or transfer numbers obtained through the platform. The system MUST support suspension or
termination when prohibited uses occur (fraud, spam, ban circumvention, harassment, illegal
activity). Jurisdiction and terms-of-service constraints documented for QuieroUnSMS MUST be
reflected in enforceable backend rules (e.g., eligibility, access restriction) where
technically appropriate. Rationale: Temporary-number services carry legal and platform risk;
backend behavior is part of compliance, not only policy text.

## Technical Constraints

The following stack, integrations, and versions are mandatory for this project unless amended
by this constitution:

| Constraint | Requirement |
|------------|-------------|
| Language | Python 3.15.2 |
| HTTP API | FastAPI |
| Testing | Pytest |
| Validation & settings | Pydantic |
| Database | PostgreSQL 18.7 |
| ORM / SQL toolkit | SQLAlchemy |
| SMS numbers provider | Grizzly SMS (or successor approved by amendment) |
| Payments | SPEI and Stripe |
| Primary market | Mexico |
| Languages | Spanish for applicable user-facing API messages; English for repository specs and docs |

Real-time SMS delivery to clients is a core non-functional requirement: designs MUST avoid
unnecessary polling-only paths where push or streaming is specified in the feature plan.

New dependencies or version changes that affect these constraints MUST be documented in the
feature plan and MUST NOT contradict this section without a constitution amendment.

## Development Workflow

- Feature work MUST follow Spec Kit artifacts (spec, plan, tasks) and MUST demonstrate
  compliance with Core Principles before implementation is considered complete.
- MVP and post-MVP work MUST be traceable to `docs/welcome.md` (or its successor product
  charter); scope creep into post-MVP items without a spec is not permitted.
- Implementation MUST respect layer boundaries: no business logic in route handlers; no
  bypassing repositories for database access in services.
- Every behavioral change MUST include Pytest coverage at the appropriate layer (unit tests
  for services with mocked repositories; integration tests when persistence, provider APIs,
  payment webhooks, or API contracts change).
- Provider and payment integrations MUST be abstracted behind services; route handlers MUST NOT
  call external provider or payment APIs directly.
- Pydantic models MUST be used for request/response schemas and application settings;
  configuration MUST NOT rely on untyped dict access for externally visible contracts.
- Database schema changes MUST be compatible with PostgreSQL 18.7 and accessed through
  SQLAlchemy per the repository pattern.
- Features touching accounts, SMS retention, or number lifecycle MUST include a compliance
  checklist (acceptable use, data minimization, retention/deletion) in the feature plan.

## Governance

This constitution is the authoritative source of engineering and product-shaping governance for
the QuieroUnSMS backend. When plans, specs, tasks, product docs, or code conflict with it,
this document prevails until amended.

- **Amendments**: Proposed via `/speckit-constitution` with explicit rationale. Version MUST
  be bumped per semantic versioning: MAJOR for incompatible principle changes, MINOR for new
  principles or material expansions, PATCH for clarifications only.
- **Compliance**: Authors and reviewers MUST verify features against Core Principles,
  Technical Constraints, and Development Workflow. Complexity that violates layering,
  skips TDD, or expands scope beyond MVP without a spec MUST be rejected or justified in
  writing and approved via amendment.
- **Runtime guidance**: Product summary lives in `docs/welcome.md`. Feature-level detail lives
  in `.specify/templates/plan-template.md`, `spec-template.md`, and `tasks-template.md`;
  those artifacts MUST NOT weaken this constitution.

**Version**: 1.1.0 | **Ratified**: 2025-11-16 | **Last Amended**: 2026-11-23