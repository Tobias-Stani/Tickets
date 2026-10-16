"""reply attachments

Revision ID: d7b3e5a1c942
Revises: c4a9d2e6f813
Create Date: 2026-10-16 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7b3e5a1c942"
down_revision: str | None = "c4a9d2e6f813"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("ticket_images", sa.Column("message_id", sa.Integer(), nullable=True))
    op.add_column("ticket_images", sa.Column("filename", sa.String(length=255), nullable=True))
    op.create_foreign_key(
        op.f("fk_ticket_images_message_id_ticket_messages"),
        "ticket_images",
        "ticket_messages",
        ["message_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_ticket_images_message_id"), "ticket_images", ["message_id"])
    # Office mime types are longer than 50 chars.
    for table in ("ticket_images", "stored_files"):
        op.alter_column(table, "content_type", type_=sa.String(length=100), existing_nullable=False)


def downgrade() -> None:
    for table in ("ticket_images", "stored_files"):
        op.alter_column(table, "content_type", type_=sa.String(length=50), existing_nullable=False)
    op.drop_index(op.f("ix_ticket_images_message_id"), table_name="ticket_images")
    op.drop_constraint(
        op.f("fk_ticket_images_message_id_ticket_messages"), "ticket_images", type_="foreignkey"
    )
    op.drop_column("ticket_images", "filename")
    op.drop_column("ticket_images", "message_id")
