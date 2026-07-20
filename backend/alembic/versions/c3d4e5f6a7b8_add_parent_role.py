"""ai intelligence engine - add parent role

Revision ID: c3d4e5f6a7b8
Revises: b7c8d9e0f1a2
Create Date: 2026-07-16 05:05:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Parent AI needs parents to be able to log in as their own role. The
    # userrole enum previously only had STUDENT/TEACHER/PRINCIPAL/ADMIN/FOUNDER
    # even though a ParentProfile model already existed.
    # ALTER TYPE ... ADD VALUE cannot run inside the migration's outer
    # transaction, so it's wrapped in its own autocommit block.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'PARENT'")


def downgrade() -> None:
    # Postgres does not support removing a value from an enum type.
    # Downgrading this migration is a no-op; the value simply stays unused.
    pass
