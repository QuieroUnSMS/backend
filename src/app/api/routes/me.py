from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_identity, get_identity_service
from app.api.routes.session import to_identity_read
from app.models.identity import Identity
from app.schemas.identity import (
    CheckoutStateRead,
    CheckoutStateWrite,
    ContactPatchRequest,
    IdentityRead,
    PurchaseHistoryCreate,
    PurchaseHistoryEntry,
    RegistrationRequest,
)
from app.services.identity_service import IdentityService

router = APIRouter(prefix="/me", tags=["identity"])


@router.get("", response_model=IdentityRead)
def get_me(identity: Identity = Depends(get_current_identity)) -> IdentityRead:
    return to_identity_read(identity)


@router.post("/registration", response_model=IdentityRead)
def register(
    payload: RegistrationRequest,
    identity: Identity = Depends(get_current_identity),
    service: IdentityService = Depends(get_identity_service),
) -> IdentityRead:
    updated = service.register(
        identity,
        email=payload.email,
        phone_e164=payload.phone_e164,
    )
    return to_identity_read(updated)


@router.patch("/contact", response_model=IdentityRead)
def add_contact(
    payload: ContactPatchRequest,
    identity: Identity = Depends(get_current_identity),
    service: IdentityService = Depends(get_identity_service),
) -> IdentityRead:
    updated = service.add_complementary_contact(
        identity,
        email=payload.email,
        phone_e164=payload.phone_e164,
    )
    return to_identity_read(updated)


@router.get("/checkout-state", response_model=CheckoutStateRead)
def get_checkout(
    identity: Identity = Depends(get_current_identity),
    service: IdentityService = Depends(get_identity_service),
) -> CheckoutStateRead:
    state, updated_at = service.get_checkout(identity)
    return CheckoutStateRead(state=state, updated_at=updated_at)


@router.put("/checkout-state", response_model=CheckoutStateRead)
def put_checkout(
    payload: CheckoutStateWrite,
    identity: Identity = Depends(get_current_identity),
    service: IdentityService = Depends(get_identity_service),
) -> CheckoutStateRead:
    row = service.put_checkout(identity, payload.state)
    return CheckoutStateRead(state=dict(row.state), updated_at=row.updated_at)


@router.get("/purchase-history", response_model=list[PurchaseHistoryEntry])
def list_purchases(
    identity: Identity = Depends(get_current_identity),
    service: IdentityService = Depends(get_identity_service),
) -> list[PurchaseHistoryEntry]:
    return [
        PurchaseHistoryEntry(id=entry.id, summary=entry.summary, created_at=entry.created_at)
        for entry in service.list_purchases(identity)
    ]


@router.post(
    "/purchase-history",
    response_model=PurchaseHistoryEntry,
    status_code=status.HTTP_201_CREATED,
)
def add_purchase(
    payload: PurchaseHistoryCreate,
    identity: Identity = Depends(get_current_identity),
    service: IdentityService = Depends(get_identity_service),
) -> PurchaseHistoryEntry:
    entry = service.add_purchase(identity, payload.summary)
    return PurchaseHistoryEntry(
        id=entry.id,
        summary=entry.summary,
        created_at=entry.created_at,
    )
