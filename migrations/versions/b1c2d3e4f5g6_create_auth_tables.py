"""Create authentication and RBAC tables

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2025-12-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import time
import uuid

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create authentication and RBAC tables."""

    # 1. Create user table if not exists, or alter existing table
    # First check if user table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'user' not in tables:
        # Create user table from scratch
        op.create_table(
            'user',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(length=50), nullable=True),
            sa.Column('role', sa.String(length=50), nullable=True),
            sa.Column('profile_image_url', sa.Text(), nullable=True),
            sa.Column('password_hash', sa.String(length=255), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
            sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default=sa.text('0')),
            sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default=sa.text('0')),
            sa.Column('locked_until', sa.BigInteger(), nullable=True),
            sa.Column('last_login_at', sa.BigInteger(), nullable=True),
            sa.Column('last_active_at', sa.BigInteger(), nullable=True),
            sa.Column('updated_at', sa.BigInteger(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
            sa.Column('api_key', sa.String(length=255), nullable=True),
            sa.Column('settings', mysql.JSON(), nullable=True),
            sa.Column('info', mysql.JSON(), nullable=True),
            sa.Column('oauth_sub', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_user_email', 'user', ['email'], unique=True)
    else:
        # Add auth columns to existing user table
        op.add_column('user', sa.Column('password_hash', sa.String(length=255), nullable=True))
        op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')))
        op.add_column('user', sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        op.add_column('user', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default=sa.text('0')))
        op.add_column('user', sa.Column('locked_until', sa.BigInteger(), nullable=True))

        # Create unique index on email if not exists
        try:
            op.create_index('idx_user_email', 'user', ['email'], unique=True)
        except Exception:
            pass  # Index may already exist

    # 2. Create group table
    op.create_table(
        'group',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_group_name', 'group', ['name'], unique=True)

    # 3. Create role table
    op.create_table(
        'role',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_role_name', 'role', ['name'], unique=True)

    # 4. Create permission table
    op.create_table(
        'permission',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('idx_permission_code', 'permission', ['code'], unique=True)
    op.create_index('idx_permission_resource', 'permission', ['resource'], unique=False)

    # 5. Create user_groups association table
    op.create_table(
        'user_groups',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('group_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_groups_user_id', 'user_groups', ['user_id'], unique=False)
    op.create_index('idx_user_groups_group_id', 'user_groups', ['group_id'], unique=False)
    op.create_index('idx_user_groups_unique', 'user_groups', ['user_id', 'group_id'], unique=True)

    # 6. Create group_roles association table
    op.create_table(
        'group_roles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('group_id', sa.String(length=36), nullable=False),
        sa.Column('role_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_group_roles_group_id', 'group_roles', ['group_id'], unique=False)
    op.create_index('idx_group_roles_role_id', 'group_roles', ['role_id'], unique=False)
    op.create_index('idx_group_roles_unique', 'group_roles', ['group_id', 'role_id'], unique=True)

    # 7. Create role_permissions association table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('role_id', sa.String(length=36), nullable=False),
        sa.Column('permission_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_role_permissions_role_id', 'role_permissions', ['role_id'], unique=False)
    op.create_index('idx_role_permissions_permission_id', 'role_permissions', ['permission_id'], unique=False)
    op.create_index('idx_role_permissions_unique', 'role_permissions', ['role_id', 'permission_id'], unique=True)

    # 8. Create refresh_token table
    op.create_table(
        'refresh_token',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('device_info', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('expires_at', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_refresh_token_user_id', 'refresh_token', ['user_id'], unique=False)
    op.create_index('idx_refresh_token_hash', 'refresh_token', ['token_hash'], unique=False)

    # 9. Insert default permissions
    now = int(time.time() * 1000)
    permissions_data = [
        # Chat permissions
        ('perm-chat-create', 'chat:create', 'Create Chat', 'chat', 'create'),
        ('perm-chat-read', 'chat:read', 'Read Chat', 'chat', 'read'),
        ('perm-chat-update', 'chat:update', 'Update Chat', 'chat', 'update'),
        ('perm-chat-delete', 'chat:delete', 'Delete Chat', 'chat', 'delete'),
        # Report permissions
        ('perm-report-create', 'report:create', 'Create Report', 'report', 'create'),
        ('perm-report-read', 'report:read', 'Read Report', 'report', 'read'),
        ('perm-report-update', 'report:update', 'Update Report', 'report', 'update'),
        ('perm-report-delete', 'report:delete', 'Delete Report', 'report', 'delete'),
        # User management permissions
        ('perm-user-read', 'user:read', 'Read Users', 'user', 'read'),
        ('perm-user-manage', 'user:manage', 'Manage Users', 'user', 'manage'),
        # Group management permissions
        ('perm-group-read', 'group:read', 'Read Groups', 'group', 'read'),
        ('perm-group-manage', 'group:manage', 'Manage Groups', 'group', 'manage'),
        # Role management permissions
        ('perm-role-read', 'role:read', 'Read Roles', 'role', 'read'),
        ('perm-role-manage', 'role:manage', 'Manage Roles', 'role', 'manage'),
        # System permissions
        ('perm-system-admin', 'system:admin', 'System Administration', 'system', 'admin'),
    ]

    for perm_id, code, name, resource, action in permissions_data:
        op.execute(
            f"INSERT INTO permission (id, code, name, resource, action, created_at) "
            f"VALUES ('{perm_id}', '{code}', '{name}', '{resource}', '{action}', {now})"
        )

    # 10. Insert default roles
    op.execute(
        f"INSERT INTO role (id, name, description, is_system, created_at, updated_at) VALUES "
        f"('role-admin', 'Administrator', 'Full system access', 1, {now}, {now})"
    )
    op.execute(
        f"INSERT INTO role (id, name, description, is_system, created_at, updated_at) VALUES "
        f"('role-user', 'User', 'Standard user access', 1, {now}, {now})"
    )
    op.execute(
        f"INSERT INTO role (id, name, description, is_system, created_at, updated_at) VALUES "
        f"('role-viewer', 'Viewer', 'Read-only access', 1, {now}, {now})"
    )

    # 11. Assign permissions to roles
    # Admin role - all permissions
    admin_permissions = [
        'perm-chat-create', 'perm-chat-read', 'perm-chat-update', 'perm-chat-delete',
        'perm-report-create', 'perm-report-read', 'perm-report-update', 'perm-report-delete',
        'perm-user-read', 'perm-user-manage',
        'perm-group-read', 'perm-group-manage',
        'perm-role-read', 'perm-role-manage',
        'perm-system-admin'
    ]
    for perm_id in admin_permissions:
        rp_id = f'rp-admin-{perm_id.split("-")[1]}-{perm_id.split("-")[2]}'
        op.execute(
            f"INSERT INTO role_permissions (id, role_id, permission_id, created_at) VALUES "
            f"('{rp_id}', 'role-admin', '{perm_id}', {now})"
        )

    # User role - basic permissions
    user_permissions = [
        'perm-chat-create', 'perm-chat-read', 'perm-chat-update', 'perm-chat-delete',
        'perm-report-create', 'perm-report-read', 'perm-report-update', 'perm-report-delete'
    ]
    for perm_id in user_permissions:
        rp_id = f'rp-user-{perm_id.split("-")[1]}-{perm_id.split("-")[2]}'
        op.execute(
            f"INSERT INTO role_permissions (id, role_id, permission_id, created_at) VALUES "
            f"('{rp_id}', 'role-user', '{perm_id}', {now})"
        )

    # Viewer role - read-only permissions
    viewer_permissions = ['perm-chat-read', 'perm-report-read']
    for perm_id in viewer_permissions:
        rp_id = f'rp-viewer-{perm_id.split("-")[1]}-{perm_id.split("-")[2]}'
        op.execute(
            f"INSERT INTO role_permissions (id, role_id, permission_id, created_at) VALUES "
            f"('{rp_id}', 'role-viewer', '{perm_id}', {now})"
        )

    # 12. Insert default groups
    op.execute(
        f"INSERT INTO `group` (id, name, description, created_at, updated_at) VALUES "
        f"('group-admins', 'Administrators', 'System administrators group', {now}, {now})"
    )
    op.execute(
        f"INSERT INTO `group` (id, name, description, created_at, updated_at) VALUES "
        f"('group-users', 'Users', 'Default user group', {now}, {now})"
    )

    # 13. Assign roles to groups
    op.execute(
        f"INSERT INTO group_roles (id, group_id, role_id, created_at) VALUES "
        f"('gr-admins-admin', 'group-admins', 'role-admin', {now})"
    )
    op.execute(
        f"INSERT INTO group_roles (id, group_id, role_id, created_at) VALUES "
        f"('gr-users-user', 'group-users', 'role-user', {now})"
    )


def downgrade() -> None:
    """Drop authentication and RBAC tables."""
    # Drop tables in reverse order (respect foreign keys)
    op.drop_table('refresh_token')
    op.drop_table('role_permissions')
    op.drop_table('group_roles')
    op.drop_table('user_groups')
    op.drop_table('permission')
    op.drop_table('role')
    op.drop_table('group')

    # Remove user auth columns
    op.drop_column('user', 'locked_until')
    op.drop_column('user', 'failed_login_attempts')
    op.drop_column('user', 'is_superadmin')
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'password_hash')

    try:
        op.drop_index('idx_user_email', table_name='user')
    except Exception:
        pass
