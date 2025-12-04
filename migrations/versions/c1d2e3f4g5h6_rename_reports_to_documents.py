"""Rename reports to documents

Revision ID: c1d2e3f4g5h6
Revises: b1c2d3e4f5g6
Create Date: 2025-12-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, None] = 'b1c2d3e4f5g6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename reports tables and related objects to documents."""

    # ==================== 1. 重命名 reports 表的索引 ====================
    # 先删除旧索引
    op.drop_index('ix_reports_category', table_name='reports')
    op.drop_index('ix_reports_chat_id', table_name='reports')
    op.drop_index('ix_reports_created_at', table_name='reports')
    op.drop_index('ix_reports_status', table_name='reports')
    op.drop_index('ix_reports_title', table_name='reports')
    op.drop_index('ix_reports_user_id', table_name='reports')

    # ==================== 2. 重命名主表 reports -> documents ====================
    op.rename_table('reports', 'documents')

    # ==================== 3. 为 documents 表创建新索引 ====================
    op.create_index('ix_documents_category', 'documents', ['category'], unique=False)
    op.create_index('ix_documents_chat_id', 'documents', ['chat_id'], unique=False)
    op.create_index('ix_documents_created_at', 'documents', ['created_at'], unique=False)
    op.create_index('ix_documents_status', 'documents', ['status'], unique=False)
    op.create_index('ix_documents_title', 'documents', ['title'], unique=False)
    op.create_index('ix_documents_user_id', 'documents', ['user_id'], unique=False)

    # ==================== 4. 重命名 report_versions 表的索引 ====================
    op.drop_index('idx_report_version', table_name='report_versions')
    op.drop_index('ix_report_versions_change_type', table_name='report_versions')
    op.drop_index('ix_report_versions_created_at', table_name='report_versions')
    op.drop_index('ix_report_versions_report_id', table_name='report_versions')

    # ==================== 5. 重命名版本表 report_versions -> document_versions ====================
    op.rename_table('report_versions', 'document_versions')

    # ==================== 6. 重命名列 report_id -> document_id ====================
    op.alter_column('document_versions', 'report_id',
                    new_column_name='document_id',
                    existing_type=sa.String(36),
                    existing_nullable=False)

    # ==================== 7. 为 document_versions 表创建新索引 ====================
    op.create_index('idx_document_version', 'document_versions', ['document_id', 'version_number'], unique=False)
    op.create_index('ix_document_versions_change_type', 'document_versions', ['change_type'], unique=False)
    op.create_index('ix_document_versions_created_at', 'document_versions', ['created_at'], unique=False)
    op.create_index('ix_document_versions_document_id', 'document_versions', ['document_id'], unique=False)

    # ==================== 8. 重命名枚举类型（可选，MySQL 不支持直接重命名枚举） ====================
    # 注意：MySQL 不支持 ALTER TYPE，枚举类型名称保持不变
    # reportstatus 和 changetype 枚举在 MySQL 中实际上是作为列定义的一部分存储的


def downgrade() -> None:
    """Revert documents tables back to reports."""

    # ==================== 1. 删除 document_versions 表的索引 ====================
    op.drop_index('idx_document_version', table_name='document_versions')
    op.drop_index('ix_document_versions_change_type', table_name='document_versions')
    op.drop_index('ix_document_versions_created_at', table_name='document_versions')
    op.drop_index('ix_document_versions_document_id', table_name='document_versions')

    # ==================== 2. 重命名列 document_id -> report_id ====================
    op.alter_column('document_versions', 'document_id',
                    new_column_name='report_id',
                    existing_type=sa.String(36),
                    existing_nullable=False)

    # ==================== 3. 重命名表 document_versions -> report_versions ====================
    op.rename_table('document_versions', 'report_versions')

    # ==================== 4. 为 report_versions 表创建索引 ====================
    op.create_index('idx_report_version', 'report_versions', ['report_id', 'version_number'], unique=False)
    op.create_index('ix_report_versions_change_type', 'report_versions', ['change_type'], unique=False)
    op.create_index('ix_report_versions_created_at', 'report_versions', ['created_at'], unique=False)
    op.create_index('ix_report_versions_report_id', 'report_versions', ['report_id'], unique=False)

    # ==================== 5. 删除 documents 表的索引 ====================
    op.drop_index('ix_documents_category', table_name='documents')
    op.drop_index('ix_documents_chat_id', table_name='documents')
    op.drop_index('ix_documents_created_at', table_name='documents')
    op.drop_index('ix_documents_status', table_name='documents')
    op.drop_index('ix_documents_title', table_name='documents')
    op.drop_index('ix_documents_user_id', table_name='documents')

    # ==================== 6. 重命名表 documents -> reports ====================
    op.rename_table('documents', 'reports')

    # ==================== 7. 为 reports 表创建索引 ====================
    op.create_index('ix_reports_category', 'reports', ['category'], unique=False)
    op.create_index('ix_reports_chat_id', 'reports', ['chat_id'], unique=False)
    op.create_index('ix_reports_created_at', 'reports', ['created_at'], unique=False)
    op.create_index('ix_reports_status', 'reports', ['status'], unique=False)
    op.create_index('ix_reports_title', 'reports', ['title'], unique=False)
    op.create_index('ix_reports_user_id', 'reports', ['user_id'], unique=False)
