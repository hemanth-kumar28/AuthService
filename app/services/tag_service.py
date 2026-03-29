"""
Tag service — handles tag CRUD with per-user scoping.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse
from app.utils.errors import ConflictError, ForbiddenError, NotFoundError


def create_tag(data: TagCreate, user_id: str, db: Session) -> TagResponse:
    """Create a new tag scoped to the user."""
    # Per-user uniqueness
    existing = (
        db.query(Tag)
        .filter(Tag.user_id == user_id, Tag.name == data.name)
        .first()
    )
    if existing:
        raise ConflictError(f"Tag '{data.name}' already exists")

    tag = Tag(name=data.name, user_id=user_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return TagResponse.model_validate(tag)


def get_tags(user_id: str, db: Session) -> list[TagResponse]:
    """List all tags belonging to the user."""
    tags = (
        db.query(Tag)
        .filter(Tag.user_id == user_id)
        .order_by(Tag.name.asc())
        .all()
    )
    return [TagResponse.model_validate(t) for t in tags]


def delete_tag(tag_id: str, user_id: str, db: Session) -> None:
    """Delete a tag, enforcing ownership."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise NotFoundError("Tag not found")
    if tag.user_id != user_id:
        raise ForbiddenError("You do not own this tag")

    db.delete(tag)
    db.commit()
