"""
Note service — handles CRUD operations with ownership enforcement,
pagination, filtering, and sorting.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.note import Note
from app.models.tag import Tag
from app.schemas.note import NoteCreate, NoteListResponse, NoteResponse, NoteUpdate
from app.utils.errors import BadRequestError, ForbiddenError, NotFoundError


def create_note(
    data: NoteCreate, owner_id: str, db: Session
) -> NoteResponse:
    """Create a new note owned by the given user."""
    note = Note(
        title=data.title,
        content=data.content,
        owner_id=owner_id,
    )

    # Attach tags if provided
    if data.tag_ids:
        tags = _resolve_tags(data.tag_ids, owner_id, db)
        note.tags = tags

    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteResponse.model_validate(note)


def get_notes(
    owner_id: str,
    db: Session,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
    sort: str = "created_at",
    order: str = "desc",
    tag_id: str | None = None,
) -> NoteListResponse:
    """
    List notes for a user with pagination, search (ILIKE), sorting,
    and optional tag filtering.
    """
    # Validate sort field
    allowed_sort_fields = {"created_at", "updated_at", "title"}
    if sort not in allowed_sort_fields:
        raise BadRequestError(
            f"Invalid sort field. Allowed: {', '.join(allowed_sort_fields)}"
        )

    # Clamp pagination
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    # Base query
    query = db.query(Note).filter(Note.owner_id == owner_id)

    # Search filter (ILIKE on title + content)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Note.title.ilike(pattern),
                Note.content.ilike(pattern),
            )
        )

    # Tag filter
    if tag_id:
        query = query.filter(Note.tags.any(Tag.id == tag_id))

    # Total count (before pagination)
    total = query.count()

    # Sorting
    sort_column = getattr(Note, sort)
    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination + eager-load tags
    notes = (
        query.options(joinedload(Note.tags))
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Deduplicate (joinedload + limit can produce cartesian issues)
    seen = set()
    unique_notes = []
    for n in notes:
        if n.id not in seen:
            seen.add(n.id)
            unique_notes.append(n)

    return NoteListResponse(
        notes=[NoteResponse.model_validate(n) for n in unique_notes],
        total=total,
        limit=limit,
        offset=offset,
    )


def get_note(note_id: str, owner_id: str, db: Session) -> NoteResponse:
    """Get a single note by ID, enforcing ownership."""
    note = (
        db.query(Note)
        .options(joinedload(Note.tags))
        .filter(Note.id == note_id)
        .first()
    )
    if note is None:
        raise NotFoundError("Note not found")
    if note.owner_id != owner_id:
        raise ForbiddenError("You do not own this note")
    return NoteResponse.model_validate(note)


def update_note(
    note_id: str, data: NoteUpdate, owner_id: str, db: Session
) -> NoteResponse:
    """Update a note, enforcing ownership."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise NotFoundError("Note not found")
    if note.owner_id != owner_id:
        raise ForbiddenError("You do not own this note")

    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.tag_ids is not None:
        note.tags = _resolve_tags(data.tag_ids, owner_id, db)

    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(note)
    return NoteResponse.model_validate(note)


def delete_note(note_id: str, owner_id: str, db: Session) -> None:
    """Delete a note, enforcing ownership."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise NotFoundError("Note not found")
    if note.owner_id != owner_id:
        raise ForbiddenError("You do not own this note")

    db.delete(note)
    db.commit()


# ── Internal Helpers ───────────────────────────────────────────


def _resolve_tags(tag_ids: list[str], owner_id: str, db: Session) -> list[Tag]:
    """
    Resolve a list of tag IDs to Tag objects, ensuring all belong to
    the requesting user.
    """
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids), Tag.user_id == owner_id).all()
    if len(tags) != len(tag_ids):
        found_ids = {t.id for t in tags}
        missing = [tid for tid in tag_ids if tid not in found_ids]
        raise BadRequestError(f"Tags not found or not owned by you: {missing}")
    return tags
