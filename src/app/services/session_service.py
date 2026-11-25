from app.core.exceptions import IdentitySuspendedError, InvalidSessionError
from app.core.security import generate_session_token, hash_session_token
from app.models.identity import Identity
from app.repositories.protocols import (
    IdentityRepositoryProtocol,
    SessionCredentialRepositoryProtocol,
)


class SessionService:
    def __init__(
        self,
        identities: IdentityRepositoryProtocol,
        credentials: SessionCredentialRepositoryProtocol,
    ) -> None:
        self._identities = identities
        self._credentials = credentials

    def bootstrap(self, raw_token: str | None) -> tuple[str, Identity, bool]:
        """Return (token, identity, created). Created is True only for a new guest."""
        if raw_token:
            identity = self.resolve(raw_token)
            return raw_token, identity, False
        identity = self._identities.create_guest()
        token = generate_session_token()
        self._credentials.create(identity.id, hash_session_token(token))
        return token, identity, True

    def resolve(self, raw_token: str) -> Identity:
        credential = self._credentials.get_by_hash(hash_session_token(raw_token))
        if credential is None:
            raise InvalidSessionError()
        identity = self._identities.get_by_id(credential.identity_id)
        if identity is None:
            raise InvalidSessionError()
        if identity.suspended_at is not None:
            raise IdentitySuspendedError()
        return identity
