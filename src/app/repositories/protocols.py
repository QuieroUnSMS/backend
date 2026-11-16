import uuid
from typing import Protocol

from app.models.contact import Contact


class ContactRepositoryProtocol(Protocol):
    def create(self, name: str, phone_e164: str) -> Contact: ...

    def list(self) -> list[Contact]: ...

    def get_by_id(self, contact_id: uuid.UUID) -> Contact | None: ...

    def get_by_phone(self, phone_e164: str) -> Contact | None: ...

    def update(
        self,
        contact: Contact,
        *,
        name: str | None = None,
        phone_e164: str | None = None,
    ) -> Contact: ...

    def delete(self, contact: Contact) -> None: ...