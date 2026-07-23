"""Course-website provider support: page content hash on connections.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-03
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "connections",
        sa.Column("last_content_hash", sa.String(length=64), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("connections", "last_content_hash")
