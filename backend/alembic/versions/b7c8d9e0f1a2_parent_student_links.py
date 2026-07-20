"""ai intelligence engine - parent student links

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-16 05:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The only new table the AI Intelligence Engine needs: everything else
    # (mentor chat, adaptive learning, predictions, recommendations, teacher
    # insights, principal analytics) is computed from tables that already
    # exist. Parent AI, however, has no way to know which students belong to
    # which parent without this link table.
    op.create_table(
        'parent_student_links',
        sa.Column('parent_id', sa.UUID(), nullable=False),
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['parent_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('parent_id', 'student_id', name='uq_parent_student_link'),
    )
    op.create_index(op.f('ix_parent_student_links_id'), 'parent_student_links', ['id'], unique=False)
    op.create_index(op.f('ix_parent_student_links_parent_id'), 'parent_student_links', ['parent_id'], unique=False)
    op.create_index(op.f('ix_parent_student_links_student_id'), 'parent_student_links', ['student_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_parent_student_links_student_id'), table_name='parent_student_links')
    op.drop_index(op.f('ix_parent_student_links_parent_id'), table_name='parent_student_links')
    op.drop_index(op.f('ix_parent_student_links_id'), table_name='parent_student_links')
    op.drop_table('parent_student_links')
