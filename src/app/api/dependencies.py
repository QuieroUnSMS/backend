from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.repositories.contact_repository import SqlAlchemyContactRepository
from app.repositories.identity_repository import SqlAlchemyIdentityRepository
from app.repositories.session_credential_repository import (
    SqlAlchemySessionCredentialRepository,
)
from app.services.contact_service import ContactService
from app.services.identity_service import IdentityService
from app.services.session_service import SessionService

_bearer = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


def get_contact_service(db: Session = Depends(get_db)) -> ContactService:
    repository = SqlAlchemyContactRepository(db)
    return ContactService(repository)


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    return SessionService(
        SqlAlchemyIdentityRepository(db),
        SqlAlchemySessionCredentialRepository(db),
    )


def get_identity_service(db: Session = Depends(get_db)) -> IdentityService:
    return IdentityService(SqlAlchemyIdentityRepository(db))


def get_current_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session_service: SessionService = Depends(get_session_service),
):
    from app.core.exceptions import InvalidSessionError

    if credentials is None:
        raise InvalidSessionError()
    return session_service.resolve(credentials.credentials)
