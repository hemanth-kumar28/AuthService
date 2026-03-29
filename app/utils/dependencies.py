"""
FastAPI dependencies used across routes.
"""

from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.utils.errors import UnauthorizedError


def get_current_user(
    authorization: str = Header(..., description="Bearer <access_token>"),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that extracts and validates the JWT from the Authorization
    header, then returns the corresponding User ORM object.
    """
    # Expect "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid authorization header format")

    token = parts[1]
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError("Invalid or expired access token")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Token payload missing subject")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedError("User not found")

    return user
