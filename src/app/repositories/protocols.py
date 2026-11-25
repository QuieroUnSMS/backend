import uuid
from datetime import datetime
from typing import Any, Protocol

from app.models.identity import (
    Identity,
    IdentityCheckoutState,
    IdentityPurchaseHistoryEntry,
    SessionCredential,
)


class IdentityRepositoryProtocol(Protocol):
    def create_guest(self) -> Identity: ...

    def get_by_id(self, identity_id: uuid.UUID) -> Identity | None: ...

    def get_by_email(self, email: str) -> Identity | None: ...

    def get_by_phone(self, phone_e164: str) -> Identity | None: ...

    def save(self, identity: Identity) -> Identity: ...

    def suspend(self, identity: Identity, when: datetime) -> Identity: ...

    def get_checkout(self, identity_id: uuid.UUID) -> IdentityCheckoutState | None: ...

    def upsert_checkout(
        self, identity_id: uuid.UUID, state: dict[str, Any]
    ) -> IdentityCheckoutState: ...

    def list_purchases(self, identity_id: uuid.UUID) -> list[IdentityPurchaseHistoryEntry]: ...

    def add_purchase(
        self, identity_id: uuid.UUID, summary: str
    ) -> IdentityPurchaseHistoryEntry: ...


class SessionCredentialRepositoryProtocol(Protocol):
    def create(self, identity_id: uuid.UUID, token_hash: str) -> SessionCredential: ...

    def get_by_hash(self, token_hash: str) -> SessionCredential | None: ...