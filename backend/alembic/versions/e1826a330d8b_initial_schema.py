"""Initial schema for AI Calendar Planner."""

from typing import Sequence, Union

from alembic import op

from app.database.base import Base
from app import models  # Register all models with Base.metadata

revision: str = "e1826a330d8b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial database schema."""
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Drop the schema created by this initial migration."""
    Base.metadata.drop_all(bind=op.get_bind())