import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.identity import (
    Identity,
    IdentityCheckoutState,
    IdentityPurchaseHistoryEntry,
)


class SqlAlchemyIdentityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_guest(self) -> Identity:
        identity = Identity(registration_status="guest")
        self._session.add(identity)
        self._session.commit()
        self._session.refresh(identity)
        return identity

    def get_by_id(self, identity_id: uuid.UUID) -> Identity | None:
        return self._session.get(Identity, identity_id)

    def get_by_email(self, email: str) -> Identity | None:
        normalized = email.strip().lower()
        return self._session.scalar(
            select(Identity).where(func.lower(Identity.email) == normalized)
        )

    def get_by_phone(self, phone_e164: str) -> Identity | None:
        return self._session.scalar(
            select(Identity).where(Identity.phone_e164 == phone_e164)
        )

    def save(self, identity: Identity) -> Identity:
        identity.updated_at = datetime.now(timezone.utc)
        self._session.add(identity)
        self._session.commit()
        self._session.refresh(identity)
        return identity

    def suspend(self, identity: Identity, when: datetime) -> Identity:
        identity.suspended_at = when
        return self.save(identity)

    def get_checkout(self, identity_id: uuid.UUID) -> IdentityCheckoutState | None:
        return self._session.get(IdentityCheckoutState, identity_id)

    def upsert_checkout(
        self, identity_id: uuid.UUID, state: dict[str, Any]
    ) -> IdentityCheckoutState:
        row = self.get_checkout(identity_id)
        now = datetime.now(timezone.utc)
        if row is None:
            row = IdentityCheckoutState(
                identity_id=identity_id,
                state=state,
                updated_at=now,
            )
            self._session.add(row)
        else:
            row.state = state
            row.updated_at = now
        self._session.commit()
        self._session.refresh(row)
        return row

    def list_purchases(self, identity_id: uuid.UUID) -> list[IdentityPurchaseHistoryEntry]:
        return list(
            self._session.scalars(
                select(IdentityPurchaseHistoryEntry)
                .where(IdentityPurchaseHistoryEntry.identity_id == identity_id)
                .order_by(IdentityPurchaseHistoryEntry.created_at)
            )
        )

    def add_purchase(
        self, identity_id: uuid.UUID, summary: str
    ) -> IdentityPurchaseHistoryEntry:
        entry = IdentityPurchaseHistoryEntry(identity_id=identity_id, summary=summary)
        self._session.add(entry)
        self._session.commit()
        self._session.refresh(entry)
        return entry
