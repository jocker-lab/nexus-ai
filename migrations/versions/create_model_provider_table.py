"""Create model_provider table

Revision ID: a1b2c3d4e5f6
Revises: 2ff41e28880d
Create Date: 2025-11-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '2ff41e28880d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create model_provider table for storing user's model provider configurations."""
    op.create_table(
        'model_provider',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('api_key', sa.Text(), nullable=True),
        sa.Column('base_url', sa.Text(), nullable=True),
        sa.Column('provider_config', mysql.JSON(), nullable=True),
        sa.Column('supported_model_types', mysql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('connection_status', sa.String(length=20), nullable=False, server_default='unknown'),
        sa.Column('last_tested_at', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for common queries
    op.create_index('idx_model_provider_user_id', 'model_provider', ['user_id'], unique=False)
    op.create_index('idx_model_provider_type', 'model_provider', ['provider_type'], unique=False)
    op.create_index('idx_model_provider_user_type', 'model_provider', ['user_id', 'provider_type'], unique=False)


def downgrade() -> None:
    """Drop model_provider table."""
    op.drop_index('idx_model_provider_user_type', table_name='model_provider')
    op.drop_index('idx_model_provider_type', table_name='model_provider')
    op.drop_index('idx_model_provider_user_id', table_name='model_provider')
    op.drop_table('model_provider')
