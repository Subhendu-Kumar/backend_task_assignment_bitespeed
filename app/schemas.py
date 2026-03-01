from datetime import datetime
from typing import Union

from pydantic import BaseModel, EmailStr, Field, field_validator


class IdentifyRequest(BaseModel):
    email: str | None = None
    phoneNumber: Union[str, int, None] = None

    @field_validator("phoneNumber", mode="before")
    @classmethod
    def coerce_phone_to_str(cls, v):
        if v is None:
            return None
        return str(v).strip() or None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        return v if v else None


class ConsolidatedContact(BaseModel):
    primaryContatctId: int
    emails: list[str]
    phoneNumbers: list[str]
    secondaryContactIds: list[int]


class IdentifyResponse(BaseModel):
    """POST /identify response body."""

    contact: ConsolidatedContact


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    createdAt: datetime
