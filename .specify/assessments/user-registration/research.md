# Idea Research: User registration and guest SMS purchase

- **Slug**: user-registration
- **Created**: 2026-11-23
- **Evidence confidence (overall)**: medium

## Users & Demand

- Buyers want temporary numbers for OTP verification without exposing a personal number; product charter cites Mexico telecom rules requiring PII with carriers as a driver for privacy-oriented purchase flows — [source: `docs/welcome.md`] (confidence: high, cited)
- Optional registration aligns with the stated key user flow: registration/login is optional, and the product defaults to not requiring PII for purchase — [source: `docs/welcome.md` §4] (confidence: high, cited)
- Registered accounts are still listed as an MVP checkbox (`User registration and login`), indicating planned demand for repeat purchasers who want history — [source: `docs/welcome.md` §3] (confidence: high, cited)
- No production usage metrics, support tickets, or interview transcripts exist in this repository to quantify how many users would register vs. stay guest — [source: repository search] (confidence: high, cited)
- Industry UX research (not independently fetched here) reports that forcing account creation at checkout is a top abandonment reason and that guest-first flows often improve conversion — [source: Baymard Institute summaries via web search; host `baymard.com` not on intake allowlist — ASSUMPTION for numeric claims] (confidence: low, assumption)

## Prior Art

### Internal (QuieroUnSMS)

- Constitution **III. MVP-First Product Scope** explicitly requires honoring optional registration and low-friction anonymous sessions while delivering purchase and SMS visibility first — [source: `.specify/memory/constitution.md`] (confidence: high, cited)
- Constitution **IV. Privacy and Minimal PII** requires collecting only necessary account/payment/number data and defaulting away from PII beyond purchase needs — [source: `.specify/memory/constitution.md`] (confidence: high, cited)
- Backend today exposes only a Contacts CRUD example; `specs/001-starting-point` states auth is out of scope; tasks note **no auth** — [source: `src/app/main.py`, `specs/001-starting-point/spec.md`, `specs/001-starting-point/tasks.md`] (confidence: high, cited)
- Intake records product decisions: email **or** phone required to register (other can be added later); **no verification** at signup for now; guest session state and purchase history on **backend**; guest can link email/phone to become a full account; **greenfield** APIs — [source: `.specify/assessments/user-registration/intake.md`] (confidence: high, cited)
- **Tension:** `docs/welcome.md` still describes frontend `sessionStorage` and cookies for session persistence, while intake resolves storage to the backend — [source: `docs/welcome.md` §4 vs. intake.md] (confidence: high, cited)

### External

- Web platforms commonly support **anonymous sessions** before authentication for cart/state, then **separate authenticated sessions** after login — [source: OWASP Session Management Cheat Sheet — host `cheatsheetseries.owasp.org` not allowlisted; content via secondary fetch/search] (confidence: medium, cited with policy caveat)
- **Linking guest data to a registered account** is a known hard problem: when the target credential already exists, systems must merge data, resolve conflicts, and avoid stranded anonymous records — [source: https://stackoverflow.com/questions/49624742/android-firebase-authentication-how-to-link-existing-user-account-to-anonymous (host: stackoverflow.com, policy: allowlisted)] (confidence: medium, cited)
- Recreating anonymous sessions on every visit after a user already registered can produce duplicate identities unless sign-in replaces anonymous flow — [source: https://stackoverflow.com/questions/78253016/firebase-link-existing-user-to-anonymous-account (host: stackoverflow.com, policy: allowlisted)] (confidence: medium, cited)

## Market & Context

- Competitors in the temporary-SMS-number space typically offer purchase with minimal signup; exact competitor flows were not benchmarked in-repo — [source: ASSUMPTION] (confidence: low, assumption)
- **Cost of doing nothing (product):** MVP checklist still flags registration/login as unfinished; without guest session + optional accounts, either forced signup harms privacy positioning or pure guest flows lose repeat-purchase history — [source: `docs/welcome.md`, intake restatement] (confidence: medium, cited)
- Post-MVP roadmap already anticipates number/SMS history for logged-in users, which depends on account or durable identity — [source: `docs/welcome.md` §3] (confidence: high, cited)

## Data & Constraints

- **Legal/privacy (product text):** Collect account details, payment information, and temporary numbers; SMS stored temporarily then deleted; users must not submit sensitive data through temp numbers; suspension for abuse — [source: `docs/welcome.md` §7] (confidence: high, cited)
- **Payments:** SPEI and Stripe planned — payment rails may impose their own identity, fraud, and retention requirements independent of “no verification at signup” — [source: `docs/welcome.md` §5] (confidence: medium, cited; provider rules ASSUMPTION)
- **Session security:** Server-issued guest identifiers should have high entropy, not accept client-chosen IDs, and rotate/ invalidate on privilege change (e.g., guest → registered) to mitigate fixation/hijacking — [source: OWASP session guidance — secondary; ASSUMPTION for implementation mapping] (confidence: medium, assumption)
- **E.164 phone validation** already established for contacts API may extend to user phone fields — [source: `specs/001-starting-point/spec.md` clarifications] (confidence: medium, cited)
- **Engineering constraint:** Constitution mandates TDD and layered service–repository design for new auth/session domains — [source: `.specify/memory/constitution.md`] (confidence: high, cited)
- **Retention periods** for guest purchase history and in-progress checkout are not defined in product docs — [source: `docs/welcome.md`, intake] (confidence: high, cited gap)

## Evidence Against the Idea

- **No verification at registration** increases risk of account preemption (claiming another person’s email/phone), weak recovery, and harder enforcement of acceptable-use suspensions tied to real identity — [source: intake product decision; general auth practice — ASSUMPTION for severity] (confidence: medium, assumption)
- **Guest-to-account linking** introduces merge conflicts (duplicate email/phone, partial checkout, orphaned guest rows) and multi-device edge cases documented in prior Firebase-style implementations — [source: stackoverflow.com threads above] (confidence: medium, cited)
- **Scope creep vs. MVP:** Full accounts + backend anonymous sessions + linking is substantial greenfield work while MVP priority is purchase + provider + real-time SMS — [source: constitution III, intake “no APIs built”, welcome MVP priorities] (confidence: high, cited)
- **Policy/enforcement gap:** Terms reference account suspension, but anonymous purchasers may be harder to correlate with abuse without stronger identity or payment fingerprints — [source: `docs/welcome.md` §7, intake] (confidence: medium, cited)
- **Frontend vs. backend session split** in documentation risks building the wrong persistence layer first if not reconciled — [source: welcome.md vs. intake] (confidence: high, cited)

## Gaps & Open Questions

- **Resolved (product)**: Guest sessions will live as long as the user provides an email or phone number to complete the account; up until that moment, the user will be authenticated using the session key generated from the frontend. [NEEDS CLARIFICATION: Retention TTL for guest sessions, purchase history, and abandoned checkouts]
- **Resolved (product)**: Client will hold a session token in cookies/localStorage/sessionStorage, and the backend will authenticate that token and retrieve the account's information (history, purchases, so on...) [NEEDS CLARIFICATION: Whether the client still holds a session token in cookies/localStorage while the backend is source of truth]
- **Resolved (product)**: No account will be created if the email or phone number already belong to another account. [NEEDS CLARIFICATION: Duplicate registration policy when email or phone already belongs to another account]
- **Resolved (product)**: For now, there will be no payment gateway. [CLARIFICATION: What minimal PII Stripe/SPEI flows require at MVP for Mexico]
- **Resolved (product)**: Permanent policy. There will be users that won't provide email or phone number to create a regular account. [NEEDS CLARIFICATION: Whether “no verification” is a permanent policy or a launch shortcut with a planned OTP phase]
- **Resolved (product)**: No Real-user validation. [NEEDS CLARIFICATION: Real-user validation (waitlist, interviews) beyond internal product requirements]

## Sources

- `docs/welcome.md` (repo path, policy: n/a)
- `.specify/memory/constitution.md` (repo path, policy: n/a)
- `.specify/assessments/user-registration/intake.md` (repo path, policy: n/a)
- `specs/001-starting-point/spec.md`, `tasks.md` (repo path, policy: n/a)
- `src/app/main.py` (repo path, policy: n/a)
- https://stackoverflow.com/questions/49624742/android-firebase-authentication-how-to-link-existing-user-account-to-anonymous (host: stackoverflow.com, policy: allowlisted)
- https://stackoverflow.com/questions/78253016/firebase-link-existing-user-to-anonymous-account (host: stackoverflow.com, policy: allowlisted)
- https://baymard.com/research-articles/delayed-account-creation (host: baymard.com, policy: [UNVERIFIED — fetch skipped: host not on safe list])
- https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html (host: cheatsheetseries.owasp.org, policy: [UNVERIFIED — fetch skipped: host not on safe list])