"""Allow multiple connections per provider (per-course feeds).

- items gain connection_id (FK -> connections, CASCADE) so each feed owns its
  synced items; uniqueness moves from (owner, source, external_id) to
  (owner, connection, external_id).
- connections drop the (owner, provider) unique constraint.
- Backfill: before this migration each user had at most one connection per
  provider, so existing synced items map unambiguously onto it.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-03
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # batch_alter_table so constraint changes work on SQLite (table rebuild).
    with op.batch_alter_table("items") as batch:
        batch.add_column(sa.Column("connection_id", sa.Integer(), nullable=True))
        batch.drop_constraint("uq_item_source", type_="unique")
        batch.create_unique_constraint(
            "uq_item_connection_external", ["owner_id", "connection_id", "external_id"]
        )
        batch.create_foreign_key(
            "fk_items_connection_id",
            "connections",
            ["connection_id"],
            ["id"],
            ondelete="CASCADE",
        )
    op.create_index("ix_items_connection_id", "items", ["connection_id"])

    # Attach pre-existing synced items to their (previously unique) connection.
    op.execute(
        """
        UPDATE items SET connection_id = (
            SELECT c.id FROM connections c
            WHERE c.owner_id = items.owner_id AND c.provider = items.source
        )
        WHERE items.source != 'manual'
        """
    )

    with op.batch_alter_table("connections") as batch:
        batch.drop_constraint("uq_connection_provider", type_="unique")


def downgrade() -> None:
    with op.batch_alter_table("connections") as batch:
        batch.create_unique_constraint("uq_connection_provider", ["owner_id", "provider"])
    op.drop_index("ix_items_connection_id", table_name="items")
    with op.batch_alter_table("items") as batch:
        batch.drop_constraint("fk_items_connection_id", type_="foreignkey")
        batch.drop_constraint("uq_item_connection_external", type_="unique")
        batch.create_unique_constraint(
            "uq_item_source", ["owner_id", "source", "external_id"]
        )
        batch.drop_column("connection_id")
