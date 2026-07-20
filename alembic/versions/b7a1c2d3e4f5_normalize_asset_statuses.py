"""Normalize asset statuses for the admin lead table.

Revision ID: b7a1c2d3e4f5
Revises: 09047e8fa54c
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7a1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "09047e8fa54c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE assets
        SET status = CASE
            WHEN status IS NULL OR btrim(status) = '' THEN 'pending'
            WHEN lower(btrim(status)) = 'new' THEN 'pending'
            ELSE lower(btrim(status))
        END
        """
    )

    op.alter_column(
        "assets",
        "status",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default="pending",
    )


def downgrade() -> None:
    op.alter_column(
        "assets",
        "status",
        existing_type=sa.String(length=20),
        nullable=True,
        server_default=None,
    )
