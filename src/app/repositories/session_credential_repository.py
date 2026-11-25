import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.identity import SessionCredential


class SqlAlchemySessionCredentialRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, identity_id: uuid.UUID, token_hash: str) -> SessionCredential:
        credential = SessionCredential(identity_id=identity_id, token_hash=token_hash)
        self._session.add(credential)
        self._session.commit()
        self._session.refresh(credential)
        return credential

    def get_by_hash(self, token_hash: str) -> SessionCredential | None:
        credential = self._session.scalar(
            select(SessionCredential).where(SessionCredential.token_hash == token_hash)
        )
        if credential is not None:
            credential.last_used_at = datetime.now(timezone.utc)
            self._session.commit()
        return credential
