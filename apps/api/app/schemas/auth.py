"""Auth schemas — login request, token response, current-user payload."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class AuthUser(BaseModel):
    """The shape the frontend keeps in session — identity + permissions."""

    id: uuid.UUID
    full_name: str
    email: str
    preferred_language: str
    role_name: str | None
    permissions: dict[str, bool]

    model_config = ConfigDict(from_attributes=False)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: AuthUser
