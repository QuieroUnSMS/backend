import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import IdentitySuspendedError, InvalidSessionError
from app.models.identity import Identity
from app.services.session_service import SessionService


def _identity(*, suspended: bool = False) -> Identity:
    return Identity(
        id=uuid.uuid4(),
        registration_status="guest",
        email=None,
        phone_e164=None,
        suspended_at=datetime.now(timezone.utc) if suspended else None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture()
def identities() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def credentials() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def service(identities: MagicMock, credentials: MagicMock) -> SessionService:
    return SessionService(identities, credentials)


class TestBootstrap:
    def test_new_guest(self, service: SessionService, identities: MagicMock, credentials: MagicMock) -> None:
        guest = _identity()
        identities.create_guest.return_value = guest

        token, identity, created = service.bootstrap(None)

        assert created is True
        assert identity is guest
        assert token
        credentials.create.assert_called_once()
        assert credentials.create.call_args.args[0] == guest.id

    def test_existing_session(
        self, service: SessionService, identities: MagicMock, credentials: MagicMock
    ) -> None:
        guest = _identity()
        credential = MagicMock(identity_id=guest.id)
        credentials.get_by_hash.return_value = credential
        identities.get_by_id.return_value = guest

        token, identity, created = service.bootstrap("known-token")

        assert created is False
        assert identity is guest
        assert token == "known-token"
        identities.create_guest.assert_not_called()

    def test_unknown_token(self, service: SessionService, credentials: MagicMock) -> None:
        credentials.get_by_hash.return_value = None
        with pytest.raises(InvalidSessionError):
            service.bootstrap("nope")

    def test_suspended(self, service: SessionService, identities: MagicMock, credentials: MagicMock) -> None:
        guest = _identity(suspended=True)
        credentials.get_by_hash.return_value = MagicMock(identity_id=guest.id)
        identities.get_by_id.return_value = guest
        with pytest.raises(IdentitySuspendedError):
            service.resolve("token")
