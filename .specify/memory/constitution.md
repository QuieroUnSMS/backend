<!--
Sync Impact Report
- Version change: (unratified template) → 1.0.0
- Modified principles: N/A (initial adoption)
- Added sections: Core Principles (2), Technical Constraints, Development Workflow, Governance
- Removed sections: Template placeholder principles IV–V (not adopted)
- Follow-up TODOs: None
-->

# QuieroUnSMS Backend Constitution

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

## Technical Constraints

The following stack and versions are mandatory for this project unless amended by this
constitution:

| Constraint | Requirement |
|------------|-------------|
| Language | Python 3.15.2 |
| HTTP API | FastAPI |
| Testing | Pytest |
| Validation & settings | Pydantic |
| Database | PostgreSQL 18.7 |
| ORM / SQL toolkit | SQLAlchemy |

New dependencies or version changes that affect these constraints MUST be documented in the
feature plan and MUST NOT contradict this section without a constitution amendment.

## Development Workflow

- Feature work MUST follow Spec Kit artifacts (spec, plan, tasks) and MUST demonstrate
  compliance with Core Principles before implementation is considered complete.
- Implementation MUST respect layer boundaries: no business logic in route handlers; no
  bypassing repositories for database access in services.
- Every behavioral change MUST include Pytest coverage at the appropriate layer (unit tests
  for services with mocked repositories; integration tests when persistence or API contracts
  change).
- Pydantic models MUST be used for request/response schemas and application settings;
  configuration MUST NOT rely on untyped dict access for externally visible contracts.
- Database schema changes MUST be compatible with PostgreSQL 18.7 and accessed through
  SQLAlchemy per the repository pattern.

## Governance

This constitution is the authoritative source of engineering governance for the QuieroUnSMS
backend. When plans, specs, tasks, or code conflict with it, this document prevails until
amended.

- **Amendments**: Proposed via `/speckit-constitution` with explicit rationale. Version MUST
  be bumped per semantic versioning: MAJOR for incompatible principle changes, MINOR for new
  principles or material expansions, PATCH for clarifications only.
- **Compliance**: Authors and reviewers MUST verify features against Core Principles,
  Technical Constraints, and Development Workflow. Complexity that violates layering or
  skips TDD MUST be rejected or justified in writing and approved via amendment.
- **Runtime guidance**: Feature-level detail lives in `.specify/templates/plan-template.md`,
  `spec-template.md`, and `tasks-template.md`; those artifacts MUST NOT weaken this
  constitution.

**Version**: 1.0.0 | **Ratified**: 2025-11-16 | **Last Amended**: 2025-11-16