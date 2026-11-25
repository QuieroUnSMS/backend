# Decision: Guest-first identity with optional accounts

- **Slug**: user-registration
- **Decided**: 2026-11-24
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md | concept.md

## Scorecard

| Criterion | Rating | Justification |
|-----------|--------|---------------|
| Problem validity | strong | Product charter, constitution, and MVP checklist all require optional signup plus continuity; cost of inaction is documented in `problem.md`. |
| Evidence strength | adequate | Internal product decisions and charter are well cited; no production usage data, but owner-stated requirements are explicit (overall research confidence: medium). |
| Value vs. inaction | strong | Without identity, privacy positioning and guest checkout suffer and registration MVP items stay blocked per `problem.md` and research. |
| Feasibility / appetite | adequate | Option B is scoped as **medium** and **phased**; greenfield backend but bounded non-goals (no verification, no real payments in this slice). |
| Strategic fit | strong | Aligns with constitution III (MVP, optional registration), IV (minimal PII), and `docs/welcome.md` flows. |
| Risk posture | adequate | Unverified identifiers, guest abuse attribution, and scope vs. purchase/SMS are recorded; concept narrows merge policy and phases delivery but does not eliminate security/product risks. |

## Verdict & Rationale

**Go.** The problem is real for QuieroUnSMS’s stated market and MVP; evidence is sufficient from product charter and explicit owner decisions (not assumption-driven wishful thinking). Option B — guest-first unified identity (phased) fits appetite and strategic goals better than deferring identity or client-only sessions. Risks are known and accepted by product policy (no verification, indefinite guests); they should be reflected in specification and monitored, not used to block specify at this stage.

## If needs-clarification

_Not applicable._

## If go — Handoff to `/speckit-specify`

- **Problem**: Buyers must purchase temporary numbers without forced registration while retaining checkout/history continuity and an optional path to attach email or phone later.
- **Chosen approach**: Option B — Guest-first unified identity (phased): server-issued session token, backend-owned guest state, voluntary upgrade with email **or** phone, reject-and-reprompt on duplicate identifiers, no verification at signup.
- **In scope / out of scope**:
  - **In**: Guest session issuance; server persistence of purchase/checkout state; upgrade guest → registered; uniqueness rules for email/phone; client holds token (cookies/storage).
  - **Out**: OTP/magic-link verification; real SPEI/Stripe; passwords/login unless added explicitly; cross-device guest merge; auto-merge into existing accounts; SMS provider/purchase catalog (separate features).
- **Success metrics**: Majority of first purchases without prior registration (qualitative); rare failed checkout resume within retention; monitor identifier-squatting reports; track optional upgrade rate (baselines unknown).
- **Carried-forward open questions**:
  - Returning registered users on a new device/browser without passwords (recognition mechanism deferred in concept).
  - Privacy notice and operational impact of indefinite guest retention.
  - Future payment-provider identity requirements (Mexico) when gateways ship.
  - Concrete acceptable-use actions for guest-only abuse (align with constitution V during specify).