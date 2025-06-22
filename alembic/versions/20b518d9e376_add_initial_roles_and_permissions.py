"""Add initial roles and permissions

Revision ID: 20b518d9e376
Revises: e052157dedfa
Create Date: 2025-05-24 13:22:22.642904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20b518d9e376'
down_revision: Union[str, None] = 'cc1b1f62e661'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO roles (name)
        VALUES ('admin'), ('moderator'), ('user')
        ON CONFLICT (name) DO NOTHING;
        """
    )

    op.execute(
        """
        INSERT INTO permissions (name) VALUES
        ('task:create'),
        ('task:read:own'),
        ('task:update:own'),
        ('task:delete:own'),
        ('task:read:any'),
        ('task:update:any'),
        ('task:delete:any')
        ON CONFLICT (name) DO NOTHING;
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM roles_permissions
        WHERE role_id IN (
        SELECT id FROM roles WHERE name IN ('admin', 'user', 'moderator')
        );
        """
    )

    op.execute(
        """
        DELETE FROM roles WHERE name IN ('admin', 'moderator', 'user');
        """
    )

    op.execute(
        """
        DELETE FROM permissions
        WHERE name IN (
        'task:create',
        'task:read:own',
        'task:update:own',
        'task:delete:own',
        'task:read:any',
        'task:update:any',
        'task:delete:any'
        );
        """
    )
