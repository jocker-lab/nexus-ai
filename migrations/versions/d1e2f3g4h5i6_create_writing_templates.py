"""Create writing_templates table

Revision ID: d1e2f3g4h5i6
Revises: c1d2e3f4g5h6
Create Date: 2025-12-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, None] = 'c1d2e3f4g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create writing_templates table."""

    op.create_table(
        'writing_templates',
        # 主键
        sa.Column('id', sa.String(length=36), nullable=False, comment='模版ID'),

        # 基础信息
        sa.Column('title', sa.String(length=255), nullable=False, comment='模版标题'),
        sa.Column('summary', sa.Text(), nullable=False, comment='模版摘要/描述'),
        sa.Column('category', sa.String(length=50), nullable=True, comment='分类'),

        # 来源信息
        sa.Column('original_filename', sa.String(length=255), nullable=True, comment='原始文件名'),
        sa.Column('markdown_content', mysql.MEDIUMTEXT(), nullable=True, comment='完整 Markdown 内容'),

        # 写作参数
        sa.Column('writing_style', sa.Enum(
            'academic', 'business', 'technical', 'creative', 'journalistic',
            name='writingstyle'
        ), nullable=True, server_default='business', comment='写作风格'),
        sa.Column('writing_tone', sa.Enum(
            'formal', 'neutral', 'casual', 'professional', 'persuasive',
            name='writingtone'
        ), nullable=True, server_default='neutral', comment='写作语气'),
        sa.Column('target_audience', sa.Text(), nullable=True, comment='目标受众描述'),

        # 结构化内容
        sa.Column('sections', mysql.JSON(), nullable=True, comment='章节结构定义'),

        # 解析状态
        sa.Column('status', sa.Enum(
            'pending', 'parsing', 'completed', 'failed',
            name='templatestatus'
        ), nullable=True, server_default='pending', comment='解析状态'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='解析失败时的错误信息'),

        # 作用域
        sa.Column('scope', sa.Enum(
            'private', 'shared', 'public',
            name='templatescope'
        ), nullable=True, server_default='private', comment='可见范围'),

        # 使用统计
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default=sa.text('0'), comment='使用次数'),

        # 关联
        sa.Column('user_id', sa.String(length=36), nullable=False, comment='创建者'),

        # 时间戳
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp(), comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp(), comment='更新时间'),

        # 约束
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),

        # 表注释
        comment='写作模版表'
    )

    # 创建索引
    op.create_index('ix_wt_user_id', 'writing_templates', ['user_id'], unique=False)
    op.create_index('ix_wt_created_at', 'writing_templates', ['created_at'], unique=False)
    op.create_index('ix_wt_user_status', 'writing_templates', ['user_id', 'status'], unique=False)
    op.create_index('ix_wt_user_category', 'writing_templates', ['user_id', 'category'], unique=False)
    op.create_index('ix_wt_scope_status', 'writing_templates', ['scope', 'status'], unique=False)


def downgrade() -> None:
    """Drop writing_templates table."""

    # 删除索引
    op.drop_index('ix_wt_scope_status', table_name='writing_templates')
    op.drop_index('ix_wt_user_category', table_name='writing_templates')
    op.drop_index('ix_wt_user_status', table_name='writing_templates')
    op.drop_index('ix_wt_created_at', table_name='writing_templates')
    op.drop_index('ix_wt_user_id', table_name='writing_templates')

    # 删除表
    op.drop_table('writing_templates')

    # 删除枚举类型 (MySQL 不需要显式删除枚举)
