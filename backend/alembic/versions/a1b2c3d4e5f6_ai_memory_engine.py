"""ai memory engine

Revision ID: a1b2c3d4e5f6
Revises: 10bb18acac91
Create Date: 2026-07-16 04:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '10bb18acac91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Drop tables being replaced by richer memory-engine equivalents.
    # ------------------------------------------------------------------
    op.drop_index(op.f('ix_ai_conversations_id'), table_name='ai_conversations')
    op.drop_table('ai_conversations')

    op.drop_index(op.f('ix_learning_styles_id'), table_name='learning_styles')
    op.drop_table('learning_styles')

    # recommendations: content Text->JSON, is_completed String->Boolean, plus new columns.
    # Recreated from scratch since this is a structural type change.
    op.drop_index(op.f('ix_recommendations_id'), table_name='recommendations')
    op.drop_table('recommendations')

    # ------------------------------------------------------------------
    # New tables
    # ------------------------------------------------------------------
    op.create_table(
        'conversation_memories',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('subject_id', sa.UUID(), nullable=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('follow_up_to_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['follow_up_to_id'], ['conversation_memories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_conversation_memories_id'), 'conversation_memories', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_memories_student_id'), 'conversation_memories', ['student_id'], unique=False)
    op.create_index(op.f('ix_conversation_memories_subject_id'), 'conversation_memories', ['subject_id'], unique=False)
    op.create_index(op.f('ix_conversation_memories_topic'), 'conversation_memories', ['topic'], unique=False)

    op.create_table(
        'learning_profiles',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('visual', sa.Float(), nullable=True),
        sa.Column('auditory', sa.Float(), nullable=True),
        sa.Column('kinesthetic', sa.Float(), nullable=True),
        sa.Column('reading_writing', sa.Float(), nullable=True),
        sa.Column('preferred_explanation_style', sa.String(), nullable=True),
        sa.Column('weak_subjects', sa.JSON(), nullable=True),
        sa.Column('strong_subjects', sa.JSON(), nullable=True),
        sa.Column('knowledge_level', sa.String(), nullable=True),
        sa.Column('difficulty_level', sa.String(), nullable=True),
        sa.Column('learning_speed', sa.String(), nullable=True),
        sa.Column('attention_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('revision_frequency', sa.String(), nullable=True),
        sa.Column('revision_recommendation', sa.Text(), nullable=True),
        sa.Column('last_analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id'),
    )
    op.create_index(op.f('ix_learning_profiles_id'), 'learning_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_learning_profiles_student_id'), 'learning_profiles', ['student_id'], unique=False)

    op.create_table(
        'quiz_attempts',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('subject_id', sa.UUID(), nullable=True),
        sa.Column('quiz_title', sa.String(), nullable=False),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('correct_answers', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_quiz_attempts_id'), 'quiz_attempts', ['id'], unique=False)
    op.create_index(op.f('ix_quiz_attempts_student_id'), 'quiz_attempts', ['student_id'], unique=False)
    op.create_index(op.f('ix_quiz_attempts_subject_id'), 'quiz_attempts', ['subject_id'], unique=False)
    op.create_index(op.f('ix_quiz_attempts_topic'), 'quiz_attempts', ['topic'], unique=False)

    op.create_table(
        'mistake_logs',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('question', sa.Text(), nullable=True),
        sa.Column('student_answer', sa.Text(), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=True),
        sa.Column('mistake_type', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('repeat_count', sa.Integer(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_mistake_logs_id'), 'mistake_logs', ['id'], unique=False)
    op.create_index(op.f('ix_mistake_logs_student_id'), 'mistake_logs', ['student_id'], unique=False)
    op.create_index(op.f('ix_mistake_logs_subject'), 'mistake_logs', ['subject'], unique=False)
    op.create_index(op.f('ix_mistake_logs_topic'), 'mistake_logs', ['topic'], unique=False)

    op.create_table(
        'frequent_doubts',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('ask_count', sa.Integer(), nullable=True),
        sa.Column('last_asked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_frequent_doubts_id'), 'frequent_doubts', ['id'], unique=False)
    op.create_index(op.f('ix_frequent_doubts_student_id'), 'frequent_doubts', ['student_id'], unique=False)
    op.create_index(op.f('ix_frequent_doubts_subject'), 'frequent_doubts', ['subject'], unique=False)
    op.create_index(op.f('ix_frequent_doubts_topic'), 'frequent_doubts', ['topic'], unique=False)

    op.create_table(
        'weekly_progress',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('week_start_date', sa.String(), nullable=False),
        sa.Column('hours_studied', sa.Float(), nullable=True),
        sa.Column('topics_covered', sa.JSON(), nullable=True),
        sa.Column('subjects_summary', sa.JSON(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_weekly_progress_id'), 'weekly_progress', ['id'], unique=False)
    op.create_index(op.f('ix_weekly_progress_student_id'), 'weekly_progress', ['student_id'], unique=False)
    op.create_index(op.f('ix_weekly_progress_week_start_date'), 'weekly_progress', ['week_start_date'], unique=False)

    op.create_table(
        'monthly_progress',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('hours_studied', sa.Float(), nullable=True),
        sa.Column('topics_covered', sa.JSON(), nullable=True),
        sa.Column('subjects_summary', sa.JSON(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('improvement_trend', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_monthly_progress_id'), 'monthly_progress', ['id'], unique=False)
    op.create_index(op.f('ix_monthly_progress_student_id'), 'monthly_progress', ['student_id'], unique=False)

    op.create_table(
        'recommendations',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recommendations_id'), 'recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_recommendations_student_id'), 'recommendations', ['student_id'], unique=False)
    op.create_index(op.f('ix_recommendations_type'), 'recommendations', ['type'], unique=False)

    # ------------------------------------------------------------------
    # Alter existing tables
    # ------------------------------------------------------------------
    op.add_column('student_memories', sa.Column('importance', sa.Integer(), nullable=True))
    op.alter_column('student_memories', 'student_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('student_memories', 'key', existing_type=sa.String(), nullable=False)
    op.alter_column('student_memories', 'value', existing_type=sa.Text(), nullable=False)

    op.add_column('weakness_profiles', sa.Column('weak_chapters', sa.JSON(), nullable=True))
    op.add_column('weakness_profiles', sa.Column('weak_concepts', sa.JSON(), nullable=True))
    op.add_column('weakness_profiles', sa.Column('frequent_mistakes', sa.JSON(), nullable=True))
    op.add_column('weakness_profiles', sa.Column('forgotten_topics', sa.JSON(), nullable=True))
    op.add_column('weakness_profiles', sa.Column('last_analyzed_at', sa.DateTime(timezone=True), nullable=True))
    op.drop_column('weakness_profiles', 'topics_to_improve')
    op.alter_column('weakness_profiles', 'student_id', existing_type=sa.UUID(), nullable=False)

    op.add_column('daily_progress', sa.Column('subjects_summary', sa.JSON(), nullable=True))
    op.add_column('daily_progress', sa.Column('quizzes_taken', sa.Integer(), nullable=True))
    op.add_column('daily_progress', sa.Column('homework_completed', sa.Integer(), nullable=True))
    op.add_column('daily_progress', sa.Column('average_confidence', sa.Float(), nullable=True))
    op.alter_column('daily_progress', 'student_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('daily_progress', 'date', existing_type=sa.String(), nullable=False)
    op.create_index(op.f('ix_daily_progress_student_id'), 'daily_progress', ['student_id'], unique=False)
    op.create_index(op.f('ix_daily_progress_date'), 'daily_progress', ['date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_daily_progress_date'), table_name='daily_progress')
    op.drop_index(op.f('ix_daily_progress_student_id'), table_name='daily_progress')
    op.drop_column('daily_progress', 'average_confidence')
    op.drop_column('daily_progress', 'homework_completed')
    op.drop_column('daily_progress', 'quizzes_taken')
    op.drop_column('daily_progress', 'subjects_summary')

    op.add_column('weakness_profiles', sa.Column('topics_to_improve', sa.JSON(), nullable=True))
    op.drop_column('weakness_profiles', 'last_analyzed_at')
    op.drop_column('weakness_profiles', 'forgotten_topics')
    op.drop_column('weakness_profiles', 'frequent_mistakes')
    op.drop_column('weakness_profiles', 'weak_concepts')
    op.drop_column('weakness_profiles', 'weak_chapters')

    op.drop_column('student_memories', 'importance')

    op.drop_index(op.f('ix_recommendations_type'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_student_id'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_id'), table_name='recommendations')
    op.drop_table('recommendations')

    op.drop_index(op.f('ix_monthly_progress_student_id'), table_name='monthly_progress')
    op.drop_index(op.f('ix_monthly_progress_id'), table_name='monthly_progress')
    op.drop_table('monthly_progress')

    op.drop_index(op.f('ix_weekly_progress_week_start_date'), table_name='weekly_progress')
    op.drop_index(op.f('ix_weekly_progress_student_id'), table_name='weekly_progress')
    op.drop_index(op.f('ix_weekly_progress_id'), table_name='weekly_progress')
    op.drop_table('weekly_progress')

    op.drop_index(op.f('ix_frequent_doubts_topic'), table_name='frequent_doubts')
    op.drop_index(op.f('ix_frequent_doubts_subject'), table_name='frequent_doubts')
    op.drop_index(op.f('ix_frequent_doubts_student_id'), table_name='frequent_doubts')
    op.drop_index(op.f('ix_frequent_doubts_id'), table_name='frequent_doubts')
    op.drop_table('frequent_doubts')

    op.drop_index(op.f('ix_mistake_logs_topic'), table_name='mistake_logs')
    op.drop_index(op.f('ix_mistake_logs_subject'), table_name='mistake_logs')
    op.drop_index(op.f('ix_mistake_logs_student_id'), table_name='mistake_logs')
    op.drop_index(op.f('ix_mistake_logs_id'), table_name='mistake_logs')
    op.drop_table('mistake_logs')

    op.drop_index(op.f('ix_quiz_attempts_topic'), table_name='quiz_attempts')
    op.drop_index(op.f('ix_quiz_attempts_subject_id'), table_name='quiz_attempts')
    op.drop_index(op.f('ix_quiz_attempts_student_id'), table_name='quiz_attempts')
    op.drop_index(op.f('ix_quiz_attempts_id'), table_name='quiz_attempts')
    op.drop_table('quiz_attempts')

    op.drop_index(op.f('ix_learning_profiles_student_id'), table_name='learning_profiles')
    op.drop_index(op.f('ix_learning_profiles_id'), table_name='learning_profiles')
    op.drop_table('learning_profiles')

    op.drop_index(op.f('ix_conversation_memories_topic'), table_name='conversation_memories')
    op.drop_index(op.f('ix_conversation_memories_subject_id'), table_name='conversation_memories')
    op.drop_index(op.f('ix_conversation_memories_student_id'), table_name='conversation_memories')
    op.drop_index(op.f('ix_conversation_memories_id'), table_name='conversation_memories')
    op.drop_table('conversation_memories')

    op.create_table(
        'recommendations',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('is_completed', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recommendations_id'), 'recommendations', ['id'], unique=False)

    op.create_table(
        'learning_styles',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('visual', sa.Float(), nullable=True),
        sa.Column('auditory', sa.Float(), nullable=True),
        sa.Column('kinesthetic', sa.Float(), nullable=True),
        sa.Column('reading_writing', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id'),
    )
    op.create_index(op.f('ix_learning_styles_id'), 'learning_styles', ['id'], unique=False)

    op.create_table(
        'ai_conversations',
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('history', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ai_conversations_id'), 'ai_conversations', ['id'], unique=False)
