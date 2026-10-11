"""Add task notes."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f8d5fca4ec49"
down_revision: Union[str, Sequence[str], None] = "e1826a330d8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add notes if the column does not already exist."""
    inspector = sa.inspect(op.get_bind())

    columns = {
        column["name"]
        for column in inspector.get_columns("tasks")
    }

    if "notes" not in columns:
        op.add_column(
            "tasks",
            sa.Column("notes", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    """Remove notes if the column exists."""
    inspector = sa.inspect(op.get_bind())

    columns = {
        column["name"]
        for column in inspector.get_columns("tasks")
    }

    if "notes" in columns:
        op.drop_column("tasks", "notes")