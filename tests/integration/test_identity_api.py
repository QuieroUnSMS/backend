import uuid
from datetime import datetime, timezone

from app.repositories.identity_repository import SqlAlchemyIdentityRepository


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_guest_session_checkout_and_history(client) -> None:
    created = client.post("/session")
    assert created.status_code == 201
    body = created.json()
    token = body["session_token"]
    assert body["identity"]["registration_status"] == "guest"
    assert body["identity"]["email"] is None

    saved = client.put(
        "/me/checkout-state",
        headers=_auth(token),
        json={"state": {"step": "payment"}},
    )
    assert saved.status_code == 200
    assert saved.json()["state"]["step"] == "payment"

    purchase = client.post(
        "/me/purchase-history",
        headers=_auth(token),
        json={"summary": "Test purchase"},
    )
    assert purchase.status_code == 201

    again = client.get("/me/checkout-state", headers=_auth(token))
    assert again.status_code == 200
    assert again.json()["state"]["step"] == "payment"

    history = client.get("/me/purchase-history", headers=_auth(token))
    assert history.status_code == 200
    assert history.json()[0]["summary"] == "Test purchase"

    missing = client.get("/me")
    assert missing.status_code == 401


def test_invalid_bearer_on_session(client) -> None:
    response = client.post("/session", headers=_auth("not-a-real-token"))
    assert response.status_code == 401


def test_register_keeps_history_and_rejects_duplicate(client) -> None:
    first = client.post("/session")
    token = first.json()["session_token"]
    identity_id = first.json()["identity"]["id"]
    client.post(
        "/me/purchase-history",
        headers=_auth(token),
        json={"summary": "Before register"},
    )

    registered = client.post(
        "/me/registration",
        headers=_auth(token),
        json={"email": "buyer@example.com"},
    )
    assert registered.status_code == 200
    assert registered.json()["id"] == identity_id
    assert registered.json()["registration_status"] == "registered"
    assert registered.json()["email"] == "buyer@example.com"

    history = client.get("/me/purchase-history", headers=_auth(token))
    assert history.json()[0]["summary"] == "Before register"

    second = client.post("/session")
    other = second.json()["session_token"]
    conflict = client.post(
        "/me/registration",
        headers=_auth(other),
        json={"email": "Buyer@Example.com"},
    )
    assert conflict.status_code == 409
    still_guest = client.get("/me", headers=_auth(other))
    assert still_guest.json()["registration_status"] == "guest"

    invalid = client.post(
        "/me/registration",
        headers=_auth(other),
        json={"phone_e164": "555"},
    )
    assert invalid.status_code == 422

    again = client.post(
        "/me/registration",
        headers=_auth(token),
        json={"phone_e164": "+525512345678"},
    )
    assert again.status_code == 422


def test_complementary_contact_and_suspension(client, db_session) -> None:
    created = client.post("/session")
    token = created.json()["session_token"]
    identity_id = uuid.UUID(created.json()["identity"]["id"])
    client.post(
        "/me/registration",
        headers=_auth(token),
        json={"email": "complete@example.com"},
    )
    patched = client.patch(
        "/me/contact",
        headers=_auth(token),
        json={"phone_e164": "+525598765432"},
    )
    assert patched.status_code == 200
    assert patched.json()["phone_e164"] == "+525598765432"
    assert patched.json()["email"] == "complete@example.com"

    other = client.post("/session").json()["session_token"]
    client.post(
        "/me/registration",
        headers=_auth(other),
        json={"phone_e164": "+525500000099"},
    )
    clash = client.patch(
        "/me/contact",
        headers=_auth(other),
        json={"email": "complete@example.com"},
    )
    assert clash.status_code == 409
    unchanged = client.get("/me", headers=_auth(other))
    assert unchanged.json()["email"] is None
    assert unchanged.json()["phone_e164"] == "+525500000099"

    repo = SqlAlchemyIdentityRepository(db_session)
    identity = repo.get_by_id(identity_id)
    assert identity is not None
    repo.suspend(identity, datetime.now(timezone.utc))
    blocked = client.get("/me", headers=_auth(token))
    assert blocked.status_code == 403
    assert "suspendida" in blocked.json()["detail"]
    hidden = client.get("/me/purchase-history", headers=_auth(token))
    assert hidden.status_code == 403
