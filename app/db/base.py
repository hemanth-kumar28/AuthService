"""
Declarative base and model registry.

Import all models here so Alembic's `target_metadata` can discover them.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Import every model so Base.metadata is fully populated.
# These imports MUST stay at the bottom to avoid circular imports.
import app.models.user  # noqa: F401, E402
import app.models.note  # noqa: F401, E402
import app.models.tag  # noqa: F401, E402
import app.models.refresh_token  # noqa: F401, E402
