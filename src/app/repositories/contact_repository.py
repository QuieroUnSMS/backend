import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact


class SqlAlchemyContactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, name: str, phone_e164: str) -> Contact:
        contact = Contact(name=name, phone_e164=phone_e164)
        self._session.add(contact)
        self._session.commit()
        self._session.refresh(contact)
        return contact

    def list(self) -> list[Contact]:
        return list(self._session.scalars(select(Contact).order_by(Contact.created_at)))

    def get_by_id(self, contact_id: uuid.UUID) -> Contact | None:
        return self._session.get(Contact, contact_id)

    def get_by_phone(self, phone_e164: str) -> Contact | None:
        return self._session.scalar(
            select(Contact).where(Contact.phone_e164 == phone_e164)
        )

    def update(
        self,
        contact: Contact,
        *,
        name: str | None = None,
        phone_e164: str | None = None,
    ) -> Contact:
        if name is not None:
            contact.name = name
        if phone_e164 is not None:
            contact.phone_e164 = phone_e164
        contact.updated_at = datetime.now(timezone.utc)
        self._session.commit()
        self._session.refresh(contact)
        return contact

    def delete(self, contact: Contact) -> None:
        self._session.delete(contact)
        self._session.commit()