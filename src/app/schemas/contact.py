import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

E164_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    phone_e164: str = Field(..., max_length=16)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("name must not be empty or whitespace only")
        if len(trimmed) > 120:
            raise ValueError("name must be at most 120 characters")
        return trimmed

    @field_validator("phone_e164")
    @classmethod
    def phone_e164_valid(cls, value: str) -> str:
        if not E164_PATTERN.match(value):
            raise ValueError("phone_e164 must be valid E.164 with leading +")
        return value


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    phone_e164: str | None = Field(default=None, max_length=16)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "ContactUpdate":
        if self.name is None and self.phone_e164 is None:
            raise ValueError("at least one field required")
        return self

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("name must not be empty or whitespace only")
        if len(trimmed) > 120:
            raise ValueError("name must be at most 120 characters")
        return trimmed

    @field_validator("phone_e164")
    @classmethod
    def phone_e164_valid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not E164_PATTERN.match(value):
            raise ValueError("phone_e164 must be valid E.164 with leading +")
        return value


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    phone_e164: str
    created_at: datetime
    updated_at: datetime