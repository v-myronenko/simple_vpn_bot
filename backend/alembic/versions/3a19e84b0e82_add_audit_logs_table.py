"""add audit_logs table

Revision ID: 3a19e84b0e82
Revises: 66bbb12f059f
Create Date: 2026-02-10 19:36:09.459389
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a19e84b0e82'
down_revision: Union[str, None] = '66bbb12f059f'
branch_labels: Union[str, Sequence[str] | None] = None
depends_on: Union[str, Sequence[str] | None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("level", sa.String(length=10), nullable=False, server_default="info"),
        sa.Column("object_type", sa.String(length=30), nullable=True),
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.Text(), nullable=True),
    )
    op.create_index("ix_audit_logs_telegram_id", "audit_logs", ["telegram_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
