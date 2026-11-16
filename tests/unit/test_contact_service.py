import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ContactNotFoundError, DuplicatePhoneError
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from app.services.contact_service import ContactService


def _contact(
    *,
    phone: str = "+15551000001",
    name: str = "Ada",
    contact_id: uuid.UUID | None = None,
) -> Contact:
    return Contact(
        id=contact_id or uuid.uuid4(),
        name=name,
        phone_e164=phone,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture()
def repo() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def service(repo: MagicMock) -> ContactService:
    return ContactService(repo)


class TestCreate:
    def test_create_success(self, service: ContactService, repo: MagicMock) -> None:
        repo.get_by_phone.return_value = None
        expected = _contact()
        repo.create.return_value = expected

        result = service.create(
            ContactCreate(name="Ada", phone_e164="+15551000001")
        )

        assert result is expected
        repo.create.assert_called_once_with("Ada", "+15551000001")

    def test_create_duplicate_phone(
        self, service: ContactService, repo: MagicMock
    ) -> None:
        repo.get_by_phone.return_value = _contact()

        with pytest.raises(DuplicatePhoneError):
            service.create(
                ContactCreate(name="Bob", phone_e164="+15551000001")
            )

        repo.create.assert_not_called()


class TestGetAndList:
    def test_get_not_found(self, service: ContactService, repo: MagicMock) -> None:
        repo.get_by_id.return_value = None
        with pytest.raises(ContactNotFoundError):
            service.get(uuid.uuid4())

    def test_list_delegates(self, service: ContactService, repo: MagicMock) -> None:
        rows = [_contact(), _contact(phone="+15551000002", name="Bob")]
        repo.list.return_value = rows
        assert service.list() == rows


class TestUpdate:
    def test_update_not_found(self, service: ContactService, repo: MagicMock) -> None:
        repo.get_by_id.return_value = None
        with pytest.raises(ContactNotFoundError):
            service.update(uuid.uuid4(), ContactUpdate(name="New"))

    def test_update_duplicate_phone(
        self, service: ContactService, repo: MagicMock
    ) -> None:
        current = _contact(phone="+15551000001")
        other = _contact(phone="+15551000099", name="Other")
        repo.get_by_id.return_value = current
        repo.get_by_phone.return_value = other

        with pytest.raises(DuplicatePhoneError):
            service.update(
                current.id,
                ContactUpdate(phone_e164="+15551000099"),
            )

    def test_update_success(self, service: ContactService, repo: MagicMock) -> None:
        current = _contact()
        updated = _contact(name="Ada L.")
        repo.get_by_id.return_value = current
        repo.update.return_value = updated

        result = service.update(current.id, ContactUpdate(name="Ada L."))

        assert result is updated
        repo.update.assert_called_once()


class TestDelete:
    def test_delete_not_found(self, service: ContactService, repo: MagicMock) -> None:
        repo.get_by_id.return_value = None
        with pytest.raises(ContactNotFoundError):
            service.delete(uuid.uuid4())

    def test_delete_success(self, service: ContactService, repo: MagicMock) -> None:
        current = _contact()
        repo.get_by_id.return_value = current
        service.delete(current.id)
        repo.delete.assert_called_once_with(current)