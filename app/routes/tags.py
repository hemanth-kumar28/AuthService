"""Tags routes — create, list, delete (per-user scoped)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.tag import TagCreate
from app.services import tag_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("", status_code=201)
def create_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Create a new tag."""
    tag = tag_service.create_tag(data, current_user.id, db)
    return SuccessResponse(data=tag)


@router.get("")
def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """List the current user's tags."""
    tags = tag_service.get_tags(current_user.id, db)
    return SuccessResponse(data=tags)


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Delete a tag."""
    tag_service.delete_tag(tag_id, current_user.id, db)
    return SuccessResponse(data={"message": "Tag deleted successfully"})
