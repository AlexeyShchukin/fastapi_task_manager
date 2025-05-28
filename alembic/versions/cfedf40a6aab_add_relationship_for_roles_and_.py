"""Add relationship for roles and permissions

Revision ID: cfedf40a6aab
Revises: 7f4b5cbf9bc6
Create Date: 2025-05-27 21:06:28.692404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfedf40a6aab'
down_revision: Union[str, None] = '7f4b5cbf9bc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles_permissions (role_id, permission_id)
        SELECT roles.id, permissions.id
        FROM roles, permissions
        WHERE (roles.name = 'admin' AND permissions.name IN (
        'task:create', 
        'task:read:any', 
        'task:update:any', 
        'task:delete:any'
        ))
        OR (roles.name = 'moderator' AND permissions.name IN (
        'task:read:any', 
        'task:delete:any'
        ))
        OR (roles.name = 'user' AND permissions.name IN (
        'task:create',
        'task:read:own', 
        'task:update:own', 
        'task:delete:own'
        ));
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM roles_permissions
        WHERE role_id IN (
            SELECT id FROM roles WHERE name IN ('admin', 'moderator', 'user')
        )
        AND permission_id IN (
            SELECT id FROM permissions WHERE name IN (
                'task:create',
                'task:read:any',
                'task:update:any',
                'task:delete:any',
                'task:read:own',
                'task:update:own',
                'task:delete:own'
            )
        );
        """
    )
