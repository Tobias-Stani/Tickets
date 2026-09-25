"""optional ticket topic

Revision ID: a7d3e2b41c90
Revises: 5605446c55ff
Create Date: 2026-09-25 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a7d3e2b41c90"
down_revision: str | None = "5605446c55ff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("tickets", "topic_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    # Fails if any ticket has no topic; assign one first.
    op.alter_column("tickets", "topic_id", existing_type=sa.Integer(), nullable=False)
