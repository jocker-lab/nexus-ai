# -*- coding: utf-8 -*-
"""add_templates_table

Revision ID: e20695538e38
Revises: 2ff41e28880d
Create Date: 2025-12-01 11:18:16.995197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e20695538e38'
down_revision: Union[str, None] = '2ff41e28880d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 templates 表"""
    op.create_table(
        'templates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),

        # 基础信息
        sa.Column('title', sa.VARCHAR(255), nullable=False, index=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('category', sa.VARCHAR(50), index=True),

        # 原始内容
        sa.Column('original_filename', sa.VARCHAR(255)),
        sa.Column('markdown_content', sa.Text()),

        # 风格信息
        sa.Column('writing_style', sa.VARCHAR(20), server_default='business'),
        sa.Column('writing_tone', sa.VARCHAR(20), server_default='neutral'),
        sa.Column('target_audience', sa.Text()),

        # 结构信息
        sa.Column('sections', sa.JSON()),
        sa.Column('special_requirements', sa.Text()),

        # 时间戳
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    """删除 templates 表"""
    op.drop_table('templates')
