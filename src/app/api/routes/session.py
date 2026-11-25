from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import get_session_service
from app.models.identity import Identity
from app.schemas.identity import IdentityRead, SessionBootstrapResponse
from app.services.session_service import SessionService

router = APIRouter(tags=["session"])
_optional_bearer = HTTPBearer(auto_error=False)


def to_identity_read(identity: Identity) -> IdentityRead:
    status = identity.registration_status
    if status not in ("guest", "registered"):
        status = "guest"
    return IdentityRead(
        id=identity.id,
        registration_status=status,  # type: ignore[arg-type]
        email=identity.email,
        phone_e164=identity.phone_e164,
        is_suspended=identity.suspended_at is not None,
        created_at=identity.created_at,
        updated_at=identity.updated_at,
    )


@router.post("/session", response_model=SessionBootstrapResponse)
def bootstrap_session(
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    service: SessionService = Depends(get_session_service),
) -> SessionBootstrapResponse:
    raw = credentials.credentials if credentials is not None else None
    token, identity, created = service.bootstrap(raw)
    response.status_code = 201 if created else 200
    return SessionBootstrapResponse(
        session_token=token,
        identity=to_identity_read(identity),
    )
