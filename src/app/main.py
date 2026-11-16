from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import contacts
from app.core.exceptions import ContactNotFoundError, DuplicatePhoneError

app = FastAPI(title="QuieroUnSMS Backend — Contacts", version="0.1.0")
app.include_router(contacts.router)


@app.exception_handler(ContactNotFoundError)
async def contact_not_found_handler(
    _request: Request, exc: ContactNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": f"Contact not found: {exc.args[0]}"},
    )


@app.exception_handler(DuplicatePhoneError)
async def duplicate_phone_handler(
    _request: Request, exc: DuplicatePhoneError
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": f"Phone number already in use: {exc.args[0]}"},
    )