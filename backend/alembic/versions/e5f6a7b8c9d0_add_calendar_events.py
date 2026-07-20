"""add calendar events table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-17 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'calendar_events',
        sa.Column('school_id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('class_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_calendar_events_id'), 'calendar_events', ['id'], unique=False)
    op.create_index(op.f('ix_calendar_events_school_id'), 'calendar_events', ['school_id'], unique=False)
    op.create_index(op.f('ix_calendar_events_owner_id'), 'calendar_events', ['owner_id'], unique=False)
    op.create_index(op.f('ix_calendar_events_class_id'), 'calendar_events', ['class_id'], unique=False)
    op.create_index(op.f('ix_calendar_events_starts_at'), 'calendar_events', ['starts_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_calendar_events_starts_at'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_class_id'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_owner_id'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_school_id'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_id'), table_name='calendar_events')
    op.drop_table('calendar_events')
