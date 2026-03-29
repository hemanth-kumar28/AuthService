"""User-related Pydantic schemas with strict validation."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, Field


# ── Password validation helper ─────────────────────────────────

_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:'\",.<>?/`~\\])"
)


def _validate_password(value: str) -> str:
    """Enforce strong password rules."""
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(value) > 128:
        raise ValueError("Password must be at most 128 characters long")
    if not _PASSWORD_PATTERN.match(value):
        raise ValueError(
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character"
        )
    return value


# ── Request Schemas ────────────────────────────────────────────


class UserRegister(BaseModel):
    """Registration request body."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username may only contain letters, digits, and underscores"
            )
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password(v)


class UserLogin(BaseModel):
    """Login request body."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Profile update request body."""
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=30)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username may only contain letters, digits, and underscores"
            )
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request body."""
    refresh_token: str


# ── Response Schemas ───────────────────────────────────────────


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    username: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Auth token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
