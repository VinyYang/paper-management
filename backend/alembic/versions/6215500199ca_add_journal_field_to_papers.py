"""add_journal_field_to_papers

Revision ID: 6215500199ca
Revises: cc467ae35143
Create Date: 2025-03-22 13:25:28.285631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6215500199ca'
down_revision: Union[str, None] = 'cc467ae35143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 添加 journal 字段
    op.add_column('papers', sa.Column('journal', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # 删除 journal 字段
    op.drop_column('papers', 'journal')
