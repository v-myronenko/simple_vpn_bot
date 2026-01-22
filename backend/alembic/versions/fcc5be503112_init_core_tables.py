from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fcc5be503112"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str] | None] = None
depends_on: Union[str, Sequence[str] | None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    # plans
    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("price_stars", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.create_index("ix_plans_code", "plans", ["code"], unique=True)

    # servers
    op.create_table(
        "servers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("region", sa.String(length=20), nullable=False),
        sa.Column("provider_type", sa.String(length=50), nullable=False),
        sa.Column("api_url", sa.String(length=255), nullable=True),
        sa.Column("api_user", sa.String(length=100), nullable=True),
        sa.Column("api_password", sa.String(length=100), nullable=True),
        sa.Column("api_token", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.create_index("ix_servers_name", "servers", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_servers_name", table_name="servers")
    op.drop_table("servers")

    op.drop_index("ix_plans_code", table_name="plans")
    op.drop_table("plans")

    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
