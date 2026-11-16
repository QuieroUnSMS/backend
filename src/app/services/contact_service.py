import uuid

from app.core.exceptions import ContactNotFoundError, DuplicatePhoneError
from app.models.contact import Contact
from app.repositories.protocols import ContactRepositoryProtocol
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    def __init__(self, repository: ContactRepositoryProtocol) -> None:
        self._repository = repository

    def create(self, payload: ContactCreate) -> Contact:
        if self._repository.get_by_phone(payload.phone_e164):
            raise DuplicatePhoneError(payload.phone_e164)
        return self._repository.create(payload.name, payload.phone_e164)

    def list(self) -> list[Contact]:
        return self._repository.list()

    def get(self, contact_id: uuid.UUID) -> Contact:
        contact = self._repository.get_by_id(contact_id)
        if contact is None:
            raise ContactNotFoundError(str(contact_id))
        return contact

    def update(self, contact_id: uuid.UUID, payload: ContactUpdate) -> Contact:
        contact = self._repository.get_by_id(contact_id)
        if contact is None:
            raise ContactNotFoundError(str(contact_id))

        new_phone = payload.phone_e164
        if new_phone is not None and new_phone != contact.phone_e164:
            existing = self._repository.get_by_phone(new_phone)
            if existing is not None and existing.id != contact.id:
                raise DuplicatePhoneError(new_phone)

        return self._repository.update(
            contact,
            name=payload.name,
            phone_e164=payload.phone_e164,
        )

    def delete(self, contact_id: uuid.UUID) -> None:
        contact = self._repository.get_by_id(contact_id)
        if contact is None:
            raise ContactNotFoundError(str(contact_id))
        self._repository.delete(contact)