from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import me, session
from app.core.exceptions import (
    AlreadyRegisteredError,
    DuplicateIdentifierError,
    IdentitySuspendedError,
    InvalidSessionError,
    RegistrationRequiredError,
)
from app.models import identity as _identity_models  # noqa: F401

app = FastAPI(title="QuieroUnSMS Backend", version="0.2.0")
app.include_router(session.router)
app.include_router(me.router)


@app.exception_handler(InvalidSessionError)
async def invalid_session_handler(
    _request: Request, _exc: InvalidSessionError
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Sesión no válida o ausente"},
    )


@app.exception_handler(IdentitySuspendedError)
async def suspended_handler(
    _request: Request, _exc: IdentitySuspendedError
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": "La identidad está suspendida"},
    )


@app.exception_handler(DuplicateIdentifierError)
async def duplicate_identifier_handler(
    _request: Request, _exc: DuplicateIdentifierError
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "El correo o el teléfono ya pertenece a otra cuenta"},
    )


@app.exception_handler(AlreadyRegisteredError)
async def already_registered_handler(
    _request: Request, _exc: AlreadyRegisteredError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": "La identidad ya está registrada"},
    )


@app.exception_handler(RegistrationRequiredError)
async def registration_required_handler(
    _request: Request, _exc: RegistrationRequiredError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": "La cuenta aún no está registrada"},
    )


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
