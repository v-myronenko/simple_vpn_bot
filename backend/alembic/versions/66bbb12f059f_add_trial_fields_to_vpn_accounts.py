"""add trial fields to vpn_accounts

Revision ID: 66bbb12f059f
Revises: 3878c4b069ef
Create Date: 2026-02-02 20:25:02.845802
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66bbb12f059f'
down_revision: Union[str, None] = '3878c4b069ef'
branch_labels: Union[str, Sequence[str] | None] = None
depends_on: Union[str, Sequence[str] | None] = None


def upgrade() -> None:
    # Колонки trial_* уже були додані вручну / попереднім запуском на SQLite.
    # Для уникнення помилки duplicate column робимо цю міграцію no-op.
    pass


def downgrade() -> None:
    op.drop_column("vpn_accounts", "trial_used")
    op.drop_column("vpn_accounts", "trial_end_at")
    op.drop_column("vpn_accounts", "trial_started_at")
