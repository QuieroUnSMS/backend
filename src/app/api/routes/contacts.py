import uuid

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_contact_service
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    service: ContactService = Depends(get_contact_service),
) -> ContactRead:
    contact = service.create(payload)
    return ContactRead.model_validate(contact)


@router.get("", response_model=list[ContactRead])
def list_contacts(
    service: ContactService = Depends(get_contact_service),
) -> list[ContactRead]:
    contacts = service.list()
    return [ContactRead.model_validate(c) for c in contacts]


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(
    contact_id: uuid.UUID,
    service: ContactService = Depends(get_contact_service),
) -> ContactRead:
    contact = service.get(contact_id)
    return ContactRead.model_validate(contact)


@router.patch("/{contact_id}", response_model=ContactRead)
def update_contact(
    contact_id: uuid.UUID,
    payload: ContactUpdate,
    service: ContactService = Depends(get_contact_service),
) -> ContactRead:
    contact = service.update(contact_id, payload)
    return ContactRead.model_validate(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: uuid.UUID,
    service: ContactService = Depends(get_contact_service),
) -> Response:
    service.delete(contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)