"""
Authentication service — handles registration, login, token refresh,
profile updates, and account deletion.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import TokenResponse, UserRegister, UserResponse, UserUpdate
from app.utils.errors import ConflictError, UnauthorizedError


def register_user(data: UserRegister, db: Session) -> dict:
    """Register a new user and return tokens."""
    # Check uniqueness
    if db.query(User).filter(User.email == data.email).first():
        raise ConflictError("Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise ConflictError("Username already taken")

    # Create user
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.flush()

    # Generate tokens
    tokens = _create_token_pair(user.id, db)
    db.commit()

    return {
        "user": UserResponse.model_validate(user),
        "tokens": tokens,
    }


def authenticate_user(email: str, password: str, db: Session) -> dict:
    """Authenticate a user and return tokens."""
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    tokens = _create_token_pair(user.id, db)
    db.commit()

    return {
        "user": UserResponse.model_validate(user),
        "tokens": tokens,
    }


def refresh_tokens(refresh_token_str: str, db: Session) -> TokenResponse:
    """Validate a refresh token, revoke it, and issue a new pair."""
    now = datetime.now(timezone.utc)

    token_record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.revoked == False,  # noqa: E712
        )
        .first()
    )

    if token_record is None:
        raise UnauthorizedError("Invalid refresh token")

    if token_record.expires_at.replace(tzinfo=timezone.utc) < now:
        token_record.revoked = True
        db.commit()
        raise UnauthorizedError("Refresh token has expired")

    # Revoke old token
    token_record.revoked = True

    # Issue new pair
    tokens = _create_token_pair(token_record.user_id, db)
    db.commit()

    return tokens


def update_profile(user: User, data: UserUpdate, db: Session) -> UserResponse:
    """Update user profile fields."""
    if data.email is not None and data.email != user.email:
        if db.query(User).filter(User.email == data.email).first():
            raise ConflictError("Email already registered")
        user.email = data.email

    if data.username is not None and data.username != user.username:
        if db.query(User).filter(User.username == data.username).first():
            raise ConflictError("Username already taken")
        user.username = data.username

    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def delete_account(user: User, db: Session) -> None:
    """Delete user and all associated data (cascade)."""
    db.delete(user)
    db.commit()


# ── Internal Helpers ───────────────────────────────────────────


def _create_token_pair(user_id: str, db: Session) -> TokenResponse:
    """Create an access + refresh token pair and persist the refresh token."""
    access_token = create_access_token(user_id)
    raw_refresh = create_refresh_token()

    refresh_record = RefreshToken(
        user_id=user_id,
        token=raw_refresh,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
    )
