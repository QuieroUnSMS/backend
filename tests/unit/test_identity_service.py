import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import (
    AlreadyRegisteredError,
    DuplicateIdentifierError,
    RegistrationRequiredError,
)
from app.models.identity import Identity, IdentityCheckoutState
from app.services.identity_service import IdentityService


def _guest() -> Identity:
    return Identity(
        id=uuid.uuid4(),
        registration_status="guest",
        email=None,
        phone_e164=None,
        suspended_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture()
def repo() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def service(repo: MagicMock) -> IdentityService:
    return IdentityService(repo)


class TestCheckout:
    def test_empty_checkout(self, service: IdentityService, repo: MagicMock) -> None:
        guest = _guest()
        repo.get_checkout.return_value = None
        state, updated_at = service.get_checkout(guest)
        assert state == {}
        assert updated_at == guest.updated_at

    def test_put_checkout(self, service: IdentityService, repo: MagicMock) -> None:
        guest = _guest()
        saved = IdentityCheckoutState(
            identity_id=guest.id,
            state={"step": "payment"},
            updated_at=datetime.now(timezone.utc),
        )
        repo.upsert_checkout.return_value = saved
        result = service.put_checkout(guest, {"step": "payment"})
        assert result is saved
        repo.upsert_checkout.assert_called_once_with(guest.id, {"step": "payment"})


class TestRegister:
    def test_register_email(self, service: IdentityService, repo: MagicMock) -> None:
        guest = _guest()
        repo.get_by_email.return_value = None
        repo.save.side_effect = lambda identity: identity

        result = service.register(guest, email="Buyer@Example.com")

        assert result.registration_status == "registered"
        assert result.email == "buyer@example.com"
        assert result.id == guest.id

    def test_duplicate_email(self, service: IdentityService, repo: MagicMock) -> None:
        guest = _guest()
        other = _guest()
        repo.get_by_email.return_value = other
        with pytest.raises(DuplicateIdentifierError):
            service.register(guest, email="taken@example.com")
        assert guest.registration_status == "guest"

    def test_invalid_phone(self, service: IdentityService) -> None:
        guest = _guest()
        with pytest.raises(ValueError):
            service.register(guest, phone_e164="555")

    def test_already_registered(self, service: IdentityService) -> None:
        guest = _guest()
        guest.registration_status = "registered"
        guest.email = "a@b.co"
        with pytest.raises(AlreadyRegisteredError):
            service.register(guest, phone_e164="+525512345678")


class TestComplementary:
    def test_add_phone(self, service: IdentityService, repo: MagicMock) -> None:
        guest = _guest()
        guest.registration_status = "registered"
        guest.email = "a@b.co"
        repo.get_by_phone.return_value = None
        repo.save.side_effect = lambda identity: identity
        result = service.add_complementary_contact(guest, phone_e164="+525512345678")
        assert result.phone_e164 == "+525512345678"

    def test_guest_cannot_add(self, service: IdentityService) -> None:
        with pytest.raises(RegistrationRequiredError):
            service.add_complementary_contact(_guest(), email="a@b.co")

    def test_duplicate_phone_leaves_unchanged(self, service: IdentityService, repo: MagicMock) -> None:
        guest = _guest()
        guest.registration_status = "registered"
        guest.email = "a@b.co"
        repo.get_by_phone.return_value = _guest()
        with pytest.raises(DuplicateIdentifierError):
            service.add_complementary_contact(guest, phone_e164="+525500000001")
        assert guest.phone_e164 is None
