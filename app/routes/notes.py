"""Notes routes — full CRUD with pagination, filtering, sorting."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.note import NoteCreate, NoteUpdate
from app.services import note_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("", status_code=201)
def create_note(
    data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Create a new note."""
    note = note_service.create_note(data, current_user.id, db)
    return SuccessResponse(data=note)


@router.get("")
def list_notes(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Items to skip"),
    search: str | None = Query(default=None, description="Search in title/content"),
    sort: str = Query(default="created_at", description="Sort field"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    tag_id: str | None = Query(default=None, description="Filter by tag ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """List the current user's notes with pagination, search, and sorting."""
    result = note_service.get_notes(
        owner_id=current_user.id,
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        sort=sort,
        order=order,
        tag_id=tag_id,
    )
    return SuccessResponse(data=result)


@router.get("/{note_id}")
def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Get a single note by ID."""
    note = note_service.get_note(note_id, current_user.id, db)
    return SuccessResponse(data=note)


@router.put("/{note_id}")
def update_note(
    note_id: str,
    data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Update a note."""
    note = note_service.update_note(note_id, data, current_user.id, db)
    return SuccessResponse(data=note)


@router.delete("/{note_id}")
def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Delete a note."""
    note_service.delete_note(note_id, current_user.id, db)
    return SuccessResponse(data={"message": "Note deleted successfully"})
