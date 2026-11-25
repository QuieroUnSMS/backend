import re
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

E164_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class IdentityRead(BaseModel):
    id: uuid.UUID
    registration_status: Literal["guest", "registered"]
    email: str | None = None
    phone_e164: str | None = None
    is_suspended: bool
    created_at: datetime
    updated_at: datetime


class SessionBootstrapResponse(BaseModel):
    session_token: str
    identity: IdentityRead


class _OneIdentifier(BaseModel):
    email: str | None = Field(default=None, max_length=320)
    phone_e164: str | None = Field(default=None, max_length=16)

    @model_validator(mode="after")
    def exactly_one(self) -> "_OneIdentifier":
        has_email = self.email is not None
        has_phone = self.phone_e164 is not None
        if has_email == has_phone:
            raise ValueError("exactly one of email or phone_e164 is required")
        if self.phone_e164 is not None and not E164_PATTERN.fullmatch(self.phone_e164):
            raise ValueError("phone_e164 must be valid E.164 with leading +")
        if self.email is not None:
            normalized = self.email.strip().lower()
            if not EMAIL_PATTERN.fullmatch(normalized):
                raise ValueError("email must be a valid address")
            self.email = normalized
        return self


class RegistrationRequest(_OneIdentifier):
    pass


class ContactPatchRequest(_OneIdentifier):
    pass


class CheckoutStateWrite(BaseModel):
    state: dict[str, Any]


class CheckoutStateRead(BaseModel):
    state: dict[str, Any]
    updated_at: datetime


class PurchaseHistoryCreate(BaseModel):
    summary: str = Field(..., min_length=1, max_length=255)


class PurchaseHistoryEntry(BaseModel):
    id: uuid.UUID
    summary: str
    created_at: datetime
