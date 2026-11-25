import re
from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import (
    AlreadyRegisteredError,
    DuplicateIdentifierError,
    IdentitySuspendedError,
    RegistrationRequiredError,
)
from app.models.identity import Identity, IdentityCheckoutState, IdentityPurchaseHistoryEntry
from app.repositories.protocols import IdentityRepositoryProtocol
from app.schemas.identity import E164_PATTERN

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class IdentityService:
    def __init__(self, identities: IdentityRepositoryProtocol) -> None:
        self._identities = identities

    def get_checkout(self, identity: Identity) -> tuple[dict[str, Any], datetime]:
        row = self._identities.get_checkout(identity.id)
        if row is None:
            return {}, identity.updated_at
        return dict(row.state), row.updated_at

    def put_checkout(
        self, identity: Identity, state: dict[str, Any]
    ) -> IdentityCheckoutState:
        return self._identities.upsert_checkout(identity.id, state)

    def list_purchases(self, identity: Identity) -> list[IdentityPurchaseHistoryEntry]:
        return self._identities.list_purchases(identity.id)

    def add_purchase(self, identity: Identity, summary: str) -> IdentityPurchaseHistoryEntry:
        return self._identities.add_purchase(identity.id, summary)

    def register(
        self,
        identity: Identity,
        *,
        email: str | None = None,
        phone_e164: str | None = None,
    ) -> Identity:
        self._ensure_active(identity)
        if identity.registration_status == "registered":
            raise AlreadyRegisteredError()
        if email is not None:
            normalized = email.strip().lower()
            if not _EMAIL.fullmatch(normalized):
                raise ValueError("email must be a valid address")
            taken = self._identities.get_by_email(normalized)
            if taken is not None and taken.id != identity.id:
                raise DuplicateIdentifierError(normalized)
            identity.email = normalized
        elif phone_e164 is not None:
            if not E164_PATTERN.fullmatch(phone_e164):
                raise ValueError("phone_e164 must be valid E.164 with leading +")
            taken = self._identities.get_by_phone(phone_e164)
            if taken is not None and taken.id != identity.id:
                raise DuplicateIdentifierError(phone_e164)
            identity.phone_e164 = phone_e164
        else:
            raise ValueError("exactly one of email or phone_e164 is required")
        identity.registration_status = "registered"
        return self._identities.save(identity)

    def add_complementary_contact(
        self,
        identity: Identity,
        *,
        email: str | None = None,
        phone_e164: str | None = None,
    ) -> Identity:
        self._ensure_active(identity)
        if identity.registration_status != "registered":
            raise RegistrationRequiredError()
        if email is not None:
            if identity.email is not None:
                raise ValueError("email is already set")
            normalized = email.strip().lower()
            if not _EMAIL.fullmatch(normalized):
                raise ValueError("email must be a valid address")
            taken = self._identities.get_by_email(normalized)
            if taken is not None and taken.id != identity.id:
                raise DuplicateIdentifierError(normalized)
            identity.email = normalized
        elif phone_e164 is not None:
            if identity.phone_e164 is not None:
                raise ValueError("phone_e164 is already set")
            if not E164_PATTERN.fullmatch(phone_e164):
                raise ValueError("phone_e164 must be valid E.164 with leading +")
            taken = self._identities.get_by_phone(phone_e164)
            if taken is not None and taken.id != identity.id:
                raise DuplicateIdentifierError(phone_e164)
            identity.phone_e164 = phone_e164
        else:
            raise ValueError("exactly one of email or phone_e164 is required")
        return self._identities.save(identity)

    def suspend(self, identity: Identity, when: datetime | None = None) -> Identity:
        return self._identities.suspend(identity, when or datetime.now(timezone.utc))

    @staticmethod
    def _ensure_active(identity: Identity) -> None:
        if identity.suspended_at is not None:
            raise IdentitySuspendedError()
