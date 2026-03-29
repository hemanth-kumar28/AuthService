"""Auth routes — registration, login, refresh, profile, account deletion."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.user import (
    RefreshTokenRequest,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)
from app.services import auth_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Public Routes ──────────────────────────────────────────────


@router.post("/register", status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)) -> SuccessResponse:
    """Register a new user account."""
    result = auth_service.register_user(data, db)
    return SuccessResponse(data=result)


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)) -> SuccessResponse:
    """Authenticate and receive access + refresh tokens."""
    result = auth_service.authenticate_user(data.email, data.password, db)
    return SuccessResponse(data=result)


@router.post("/refresh")
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)) -> SuccessResponse:
    """Exchange a valid refresh token for a new token pair."""
    tokens = auth_service.refresh_tokens(data.refresh_token, db)
    return SuccessResponse(data=tokens)


# ── Protected Routes ───────────────────────────────────────────


@router.get("/me")
def me(current_user: User = Depends(get_current_user)) -> SuccessResponse:
    """Get the currently authenticated user's profile."""
    return SuccessResponse(data=UserResponse.model_validate(current_user))


@router.put("/update-profile")
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Update the current user's email or username."""
    updated = auth_service.update_profile(current_user, data, db)
    return SuccessResponse(data=updated)


@router.delete("/delete-account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Permanently delete the current user and all their data."""
    auth_service.delete_account(current_user, db)
    return SuccessResponse(data={"message": "Account deleted successfully"})
