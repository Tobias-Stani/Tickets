"""ticket unread flags

Revision ID: b3e8f1c27d05
Revises: a7d3e2b41c90
Create Date: 2026-09-25 11:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3e8f1c27d05"
down_revision: str | None = "a7d3e2b41c90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for column in ("unread_by_admin", "unread_by_client"):
        op.add_column(
            "tickets", sa.Column(column, sa.Boolean(), server_default=sa.false(), nullable=False)
        )


def downgrade() -> None:
    op.drop_column("tickets", "unread_by_client")
    op.drop_column("tickets", "unread_by_admin")
