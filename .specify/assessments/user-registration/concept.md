# Concept: Guest-first identity with optional accounts

- **Slug**: user-registration
- **Created**: 2026-11-24
- **Recommended option**: Option B — Guest-first unified identity (phased)

## Options

### Option A — Smallest: browser-only continuity (defer accounts)

- **Sketch**: The storefront issues and stores a durable client key only (cookies / local storage). Purchase and checkout state live on that device until the user clears storage or switches devices. Registration is postponed entirely until post-MVP; the backend treats every caller as an opaque session id with no separate “account” concept yet.
- **Appetite**: small
- **Trade-offs**: Wins fastest path to “no signup required” and avoids greenfield account logic while purchase/SMS features are built. Sacrifices cross-device history, server-authoritative enforcement, and the MVP checkbox for registration/login; conflicts with product intake that already chose backend-owned guest state and optional upgrade.
- **Rabbit holes**: Frontend and backend both invent session rules; later migration to server truth becomes a breaking change; accidental reliance on client-generated ids for security-sensitive operations.

### Option B — Guest-first unified identity (phased)

- **Sketch**: Every visitor gets a server-recognized guest identity (via a client-held token the backend issued). They can complete purchases without email or phone. Purchase history and in-progress checkout attach to that guest identity on the server. When they choose, they supply email **or** phone to graduate the same identity into a registered account (add the other identifier later), with no verification step for now. If the identifier already belongs to someone else, they are prompted for different credentials rather than creating a duplicate or silently merging. Guest records persist indefinitely unless product policy changes later.
- **Appetite**: medium
- **Trade-offs**: Wins alignment with privacy positioning, cross-visit continuity on the same browser, optional accounts, and a single thread of activity from guest → registered. Sacrifices engineering time before core purchase/SMS paths exist; unverified identifiers carry squatting and recovery risk; linking edge cases need explicit product rules. Fits constitution MVP-first if phased (guest session + attach first, polish login/returning-user flows second).
- **Rabbit holes**: Full account merge when credentials collide; multi-device “two guests one person”; session fixation/hijacking if tokens are weak or client-supplied; building password/login flows that were not in intake; retroactive abuse bans on guests; unbounded guest row growth with “never delete” policy.

### Option C — Do nothing now | Buy managed identity

- **Do nothing**: Ship purchase and SMS with no identity layer; every request is stateless or keyed only by order id in URLs. Registration stays on the backlog until after MVP revenue path works. Lowest build cost now; highest rework and UX debt (no resume checkout, no optional accounts, charter gap).
- **Buy (e.g. hosted auth with anonymous users)**: Use a third-party product for anonymous sessions and account linking. Wins speed on token hygiene and upgrade flows if the vendor matches. Sacrifices control, Mexico/data-residency fit, coupling cost, and may still require custom glue for “email OR phone, no verification, no duplicate create” rules. Appetite: medium for integration, large if compliance review and data mapping are heavy.
- **Rabbit holes**: Vendor anonymous-user lifecycle vs. “never delete guests”; vendor merge behavior vs. “ask for other credentials”; pricing at scale; Constitution stack constraints (FastAPI-first backend may still own purchase linkage).

## Recommendation

**Option B — Guest-first unified identity (phased)** is the best fit for the stated goals and product decisions already captured in intake and problem definition.

Phased delivery keeps MVP-first discipline: first slice delivers guest token issuance, server-side persistence of checkout/history, and purchase without registration; second slice delivers voluntary upgrade to a registered account (email or phone) and returning recognition for registered users. That directly supports optional signup, continuity on return, and later logged-in history without forcing account walls at checkout.

Option A is too small—it fights backend-owned sessions and blocks registration MVP goals. Option C (defer entirely) leaves the identity gap that problem.md calls costly; buying auth is reasonable to reassess if Option B’s session/linking work exceeds appetite after a thin spike.

## Out of Scope (for the recommended option)

- Identity verification (OTP, magic links, email confirmation) at signup or upgrade
- Real payment gateways; fake/simulated payment only until a later spec
- Password-based login flows unless explicitly added later (intake emphasizes identifier attachment, not passwords)
- Cross-device merge of two guest identities into one
- Automatic merge of guest data into an existing account when identifiers collide (product: ask for different credentials)
- SMS provider, number catalog, and live SMS dashboard (separate MVP pillars)
- Full acceptable-use automation beyond what constitution V already implies for accounts/sessions

## Assumptions to Validate

- A single browser-held server-issued token is sufficient for “same visit continuity” at MVP; cross-device remains a known limitation until registered login exists.
- “Never delete guest sessions” is intentional and acceptable for storage, privacy notice, and support load.
- Purchasers will tolerate unverified email/phone claims with risk accepted by product policy.
- Upgrade flow when email/phone is taken is **reject and reprompt**, not merge or auto sign-in to existing account.
- Purchase and checkout features can accept a guest identity key as the owning principal before payments go live.
- Fake payment gateway does not require stronger identity than guest/optional account provides.
- Enforcement for abuse on guest-only activity can mirror constitution acceptable-use intent without new legal design.