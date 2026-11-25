# Problem Definition: Identity for purchase without forced signup

- **Slug**: user-registration
- **Created**: 2026-11-24
- **Inputs used**: intake.md | research.md

## Problem Statement

People who want temporary numbers for OTP verification—especially in Mexico where carrier rules push more personal data onto subscribers—need to buy and receive SMS without being required to register or hand over email or phone up front. At the same time, many will abandon or repeat purchases across visits, so they lose in-progress checkouts and purchase history when nothing durable ties one visit to the next. The product also cannot meet its own MVP expectation for optional accounts and future logged-in history while the platform has no way to distinguish anonymous purchasers from people who later choose to identify themselves.

## Affected Users & Stakeholders

- **Users**: Privacy-minded first-time buyers — must complete a purchase without creating an account or supplying email/phone solely to check out; friction or forced signup conflicts with why they use the service.
- **Users**: Returning or multi-step purchasers — need continuity across sessions (e.g., resume checkout, see past numbers/SMS) whether they stay anonymous or opt into an account later.
- **Users**: Optional registrants — want to add email or phone when it benefits them without repeating work already done as a guest.
- **Stakeholders**: Product owner (Oscar Cedano) — needs MVP scope aligned with charter (optional registration, minimal PII, Mexico market).
- **Stakeholders**: Compliance and trust — acceptable-use and privacy commitments assume some link between activity and identity for suspension and data handling, which is harder when purchasers are anonymous or unverified.

## Goals

- Allow a person to buy a temporary number and use the service without mandatory registration or upfront email/phone for that path.
- Preserve enough continuity across visits that purchasers are not reset mid-checkout or denied access to their own recent activity when they use the same client session identity.
- Let someone who started anonymously later attach email or phone to become a recognized account holder without losing prior activity tied to that session.
- Keep voluntary identification bounded to product privacy principles (minimal PII, legitimate use).

## Non-Goals

- Requiring identity verification (OTP, magic link, etc.) at account creation—product policy treats this as out of scope for now.
- Integrating payment gateways or defining payment-time PII requirements in the current MVP slice (payments deferred per product input).
- Delivering number purchase, provider integration, or real-time SMS reception themselves—these are separate MVP pillars.
- Proving market demand with user research, waitlists, or production analytics (none available in-repo).
- Benchmarking competitor registration flows in detail.

## Success Metrics

- Share of completed purchases that finish without prior registration (baseline: unknown; qualitative: “majority of first purchases” per privacy positioning).
- Share of checkout starts that reach completion without dropping at an account wall (baseline: unknown).
- Share of guest sessions that later attach email or phone (baseline: unknown).
- Incidents where a purchaser cannot resume an in-progress checkout on return within the intended retention window (baseline: unknown; target: rare).
- Support or internal reports of mistaken account creation on another person’s email/phone without verification (baseline: unknown; target: monitored, no target set).

## Cost of Inaction

- Forced or de facto mandatory signup undermines the privacy-led value proposition and may increase checkout abandonment relative to guest-first alternatives suggested in research.
- Purchasers lose checkout state and history across browser or device changes unless they register early, reducing repeat use and delaying post-MVP “history for logged-in users.”
- MVP checklist items for registration/login remain unmet with no backend notion of guests or accounts, blocking a coherent identity story for the rest of the product.
- Abuse response and account suspension described in legal copy are harder to apply consistently when activity is anonymous or weakly attributable.

## Open Questions

- **Resolved (product)**: Never delete guest sessions. [NEEDS CLARIFICATION: Retention TTL for guest sessions, purchase history, and abandoned checkouts when the user never registers]
- **Resolved (product)**: Ask the user to provide other credentials to create the account. [NEEDS CLARIFICATION: Behavior when a guest links credentials that already belong to an existing account—merge, reject, or sign-in-only policy beyond “do not create duplicate account”]
- **Resolved (product)**: This will be handled by next specs. For now, create a fake payment gateway. [NEEDS CLARIFICATION: Minimum identity and retention payment providers will require when SPEI/Stripe are introduced in Mexico]
- **Resolved (product)**: The same as `V. Legal Compliance and Acceptable Use` in `constitution.md`. [NEEDS CLARIFICATION: How acceptable-use enforcement should treat abusive behavior tied only to guest sessions]