"""subject class link

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-17 00:00:00.000000

"""
from typing import Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subjects', sa.Column('class_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_subjects_class_id_classes', 'subjects', 'classes', ['class_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_subjects_class_id_classes', 'subjects', type_='foreignkey')
    op.drop_column('subjects', 'class_id')
