from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.repositories.contact_repository import SqlAlchemyContactRepository
from app.services.contact_service import ContactService


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


def get_contact_service(db: Session = Depends(get_db)) -> ContactService:
    repository = SqlAlchemyContactRepository(db)
    return ContactService(repository)