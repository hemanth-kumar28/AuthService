"""Note-related Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.tag import TagResponse


# ── Request Schemas ────────────────────────────────────────────


class NoteCreate(BaseModel):
    """Create note request body."""
    title: str = Field(min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=50_000)
    tag_ids: list[str] | None = None


class NoteUpdate(BaseModel):
    """Update note request body."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=50_000)
    tag_ids: list[str] | None = None


# ── Response Schemas ───────────────────────────────────────────


class NoteResponse(BaseModel):
    """Single note response."""
    id: str
    title: str
    content: str | None
    owner_id: str
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    """Paginated note list response."""
    notes: list[NoteResponse]
    total: int
    limit: int
    offset: int
