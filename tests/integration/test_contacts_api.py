import uuid

from fastapi.testclient import TestClient


def test_create_and_get(client: TestClient) -> None:
    create = client.post(
        "/contacts",
        json={"name": "Ada", "phone_e164": "+15551000001"},
    )
    assert create.status_code == 201
    body = create.json()
    contact_id = body["id"]
    assert body["name"] == "Ada"
    assert body["phone_e164"] == "+15551000001"

    get_resp = client.get(f"/contacts/{contact_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Ada"


def test_create_validation_errors(client: TestClient) -> None:
    bad_phone = client.post(
        "/contacts",
        json={"name": "Ada", "phone_e164": "555"},
    )
    assert bad_phone.status_code == 422

    bad_name = client.post(
        "/contacts",
        json={"name": "   ", "phone_e164": "+15551000002"},
    )
    assert bad_name.status_code == 422


def test_create_duplicate_phone(client: TestClient) -> None:
    client.post(
        "/contacts",
        json={"name": "Ada", "phone_e164": "+15551000003"},
    )
    dup = client.post(
        "/contacts",
        json={"name": "Bob", "phone_e164": "+15551000003"},
    )
    assert dup.status_code == 409


def test_list_empty_and_multiple(client: TestClient) -> None:
    empty = client.get("/contacts")
    assert empty.status_code == 200
    assert empty.json() == []

    client.post(
        "/contacts",
        json={"name": "One", "phone_e164": "+15551000010"},
    )
    client.post(
        "/contacts",
        json={"name": "Two", "phone_e164": "+15551000011"},
    )
    listed = client.get("/contacts")
    assert listed.status_code == 200
    assert len(listed.json()) == 2


def test_get_not_found(client: TestClient) -> None:
    missing = uuid.UUID("00000000-0000-0000-0000-000000000099")
    resp = client.get(f"/contacts/{missing}")
    assert resp.status_code == 404


def test_patch_and_delete(client: TestClient) -> None:
    created = client.post(
        "/contacts",
        json={"name": "Ada", "phone_e164": "+15551000020"},
    ).json()
    contact_id = created["id"]

    patched = client.patch(
        f"/contacts/{contact_id}",
        json={"name": "Ada L."},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Ada L."

    deleted = client.delete(f"/contacts/{contact_id}")
    assert deleted.status_code == 204

    assert client.get(f"/contacts/{contact_id}").status_code == 404


def test_delete_not_found(client: TestClient) -> None:
    missing = uuid.UUID("00000000-0000-0000-0000-000000000088")
    assert client.delete(f"/contacts/{missing}").status_code == 404


def test_patch_invalid_leaves_contact_unchanged(client: TestClient) -> None:
    created = client.post(
        "/contacts",
        json={"name": "Ada", "phone_e164": "+15551000040"},
    ).json()
    contact_id = created["id"]

    invalid = client.patch(
        f"/contacts/{contact_id}",
        json={"phone_e164": "not-e164"},
    )
    assert invalid.status_code == 422

    get_resp = client.get(f"/contacts/{contact_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["name"] == "Ada"
    assert body["phone_e164"] == "+15551000040"


def test_patch_not_found(client: TestClient) -> None:
    missing = uuid.UUID("00000000-0000-0000-0000-000000000077")
    resp = client.patch(
        f"/contacts/{missing}",
        json={"name": "Nobody"},
    )
    assert resp.status_code == 404


def test_patch_duplicate_phone(client: TestClient) -> None:
    a = client.post(
        "/contacts",
        json={"name": "A", "phone_e164": "+15551000030"},
    ).json()
    client.post(
        "/contacts",
        json={"name": "B", "phone_e164": "+15551000031"},
    )
    conflict = client.patch(
        f"/contacts/{a['id']}",
        json={"phone_e164": "+15551000031"},
    )
    assert conflict.status_code == 409