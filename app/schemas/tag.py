"""Tag-related Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Request Schemas ────────────────────────────────────────────


class TagCreate(BaseModel):
    """Create tag request body."""
    name: str = Field(min_length=1, max_length=50)


# ── Response Schemas ───────────────────────────────────────────


class TagResponse(BaseModel):
    """Single tag response."""
    id: str
    name: str

    model_config = {"from_attributes": True}
