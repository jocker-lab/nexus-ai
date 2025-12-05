"""change_markdown_content_to_mediumtext

Revision ID: 34baa9496527
Revises: e20695538e38
Create Date: 2025-12-01 15:28:19.663194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT


# revision identifiers, used by Alembic.
revision: str = '34baa9496527'
down_revision: Union[str, None] = 'e20695538e38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """将 markdown_content 从 TEXT 改为 MEDIUMTEXT（支持最大 16MB）"""
    op.alter_column(
        'templates',
        'markdown_content',
        existing_type=sa.Text(),
        type_=MEDIUMTEXT(),
        existing_nullable=True
    )


def downgrade() -> None:
    """回滚：将 markdown_content 从 MEDIUMTEXT 改回 TEXT"""
    op.alter_column(
        'templates',
        'markdown_content',
        existing_type=MEDIUMTEXT(),
        type_=sa.Text(),
        existing_nullable=True
    )
