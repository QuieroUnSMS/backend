# Idea Intake: User registration and guest SMS purchase

- **Slug**: user-registration
- **Created**: 2026-11-23
- **Source**: pasted text
- **Type**: new-capability

## Idea (as captured)

> users can register using their emailil address and phone numbers. but take into account that no account is required to buy a SMS, for this frontend will store a unique identifier for the session to save the purchase history and the current state of the user (if he's in the middle of a purchase for example)

## Restated

The product should support optional account registration via email and phone while still allowing SMS purchases without signing in. For guests, the frontend maintains a session-scoped unique identifier to persist purchase history and resume an in-progress checkout.

## Origin & Context

- **Raised by**: Oscar Cedano <oscar.cedano@outlook.com>
- **Trigger**: Product requirement

## First-Glance Unknowns

- **Resolved (product)**: For registration at least an email or a phone number is **required**, later the user can add a phone/email to their account
- **Resolved (product)**: No verification will be needed to create an acccount for now.
- **Resolved (product)**: Guest sessions states and purchase histories will be stored by the backend.
- **Resolved (product)**: Guest sessions can link an email address or phone number to become a regular user account.
- **Resolved (product)**: No backend APIs are already built for accounts and anonymous sessions.
- **Resolved (product)**: See `docs/welcome.md` for more information about privacy and compliance expectations.