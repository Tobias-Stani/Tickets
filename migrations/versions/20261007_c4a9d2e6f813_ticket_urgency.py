"""ticket urgency

Revision ID: c4a9d2e6f813
Revises: b3e8f1c27d05
Create Date: 2026-10-07 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4a9d2e6f813"
down_revision: str | None = "b3e8f1c27d05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column(
            "urgency",
            sa.Enum("LOW", "MEDIUM", "HIGH", name="ticketurgency", native_enum=False, length=10),
            server_default="MEDIUM",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("tickets", "urgency")
