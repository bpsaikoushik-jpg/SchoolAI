"""
AI Memory Engine models.

Covers: Student Memory, Conversation Memory, Learning Profile,
Weakness Engine outputs, and the Recommendation Engine's persisted plans.

Teacher Insights / Principal Analytics are computed on the fly by services
from this data (plus existing academic/tracking models) and are NOT
persisted as separate tables.
"""
from sqlalchemy import Column, String, Text, ForeignKey, JSON, Float, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import AuditMixin, Base


# ---------------------------------------------------------------------------
# Student Memory (free-form long-term facts about a student)
# ---------------------------------------------------------------------------
class StudentMemory(Base, AuditMixin):
    """Free-form key/value long term memory (goals, preferences, notable facts)."""
    __tablename__ = "student_memories"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String, index=True, nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String, default="general")  # academic, personal, goal, preference
    importance = Column(Integer, default=1)  # 1-5, used to prioritize retrieval

    student = relationship("StudentProfile", back_populates="memories")


# ---------------------------------------------------------------------------
# Conversation Memory (per-turn Q&A memory, NOT chat UI/session storage)
# ---------------------------------------------------------------------------
class ConversationMemory(Base, AuditMixin):
    """A single remembered question/answer exchange with the AI mentor."""
    __tablename__ = "conversation_memories"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True)

    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    topic = Column(String, index=True, nullable=True)
    difficulty = Column(String, default="medium")  # easy, medium, hard

    follow_up_to_id = Column(UUID(as_uuid=True), ForeignKey("conversation_memories.id", ondelete="SET NULL"), nullable=True)

    student = relationship("StudentProfile", back_populates="conversations")
    subject = relationship("Subject")
    follow_up_to = relationship("ConversationMemory", remote_side="ConversationMemory.id")


# ---------------------------------------------------------------------------
# Learning Profile (auto-maintained; also carries "student memory" style data)
# ---------------------------------------------------------------------------
class LearningProfile(Base, AuditMixin):
    """One row per student. Auto-recomputed by LearningProfileService."""
    __tablename__ = "learning_profiles"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Learning style (VAK-R model)
    visual = Column(Float, default=0.0)
    auditory = Column(Float, default=0.0)
    kinesthetic = Column(Float, default=0.0)
    reading_writing = Column(Float, default=0.0)
    preferred_explanation_style = Column(String, default="step_by_step")  # step_by_step, examples, visual, socratic

    # Subject strengths (cached summary; source of truth = WeaknessProfile + Result aggregates)
    weak_subjects = Column(JSON, default=list)
    strong_subjects = Column(JSON, default=list)

    # Auto-maintained profile
    knowledge_level = Column(String, default="beginner")  # beginner, intermediate, advanced
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    learning_speed = Column(String, default="average")  # slow, average, fast
    attention_score = Column(Float, default=50.0)  # 0-100
    confidence_score = Column(Float, default=50.0)  # 0-100
    revision_frequency = Column(String, default="weekly")  # daily, every_2_days, weekly, biweekly
    revision_recommendation = Column(Text, nullable=True)

    last_analyzed_at = Column(DateTime(timezone=True), nullable=True)

    student = relationship("StudentProfile", back_populates="learning_profile")


# ---------------------------------------------------------------------------
# Weakness Engine output
# ---------------------------------------------------------------------------
class WeaknessProfile(Base, AuditMixin):
    """One row per student. Auto-recomputed by WeaknessEngineService."""
    __tablename__ = "weakness_profiles"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    subjects_weakness = Column(JSON, default=dict)     # {subject: weakness_score(0-100)}
    weak_chapters = Column(JSON, default=list)         # [{subject, chapter, avg_score}]
    weak_concepts = Column(JSON, default=list)         # [{subject, topic, avg_score}]
    frequent_mistakes = Column(JSON, default=list)     # [{topic, mistake_type, count}]
    forgotten_topics = Column(JSON, default=list)      # [{subject, topic, last_seen_days_ago}]

    last_analyzed_at = Column(DateTime(timezone=True), nullable=True)

    student = relationship("StudentProfile", back_populates="weakness_profile")


# ---------------------------------------------------------------------------
# Quiz history (homework history reuses existing Homework/AssignmentSubmission/Result)
# ---------------------------------------------------------------------------
class QuizAttempt(Base, AuditMixin):
    __tablename__ = "quiz_attempts"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True)

    quiz_title = Column(String, nullable=False)
    topic = Column(String, index=True, nullable=True)
    difficulty = Column(String, default="medium")
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # percentage 0-100
    time_taken_seconds = Column(Integer, nullable=True)

    student = relationship("StudentProfile", back_populates="quiz_attempts")
    subject = relationship("Subject")


# ---------------------------------------------------------------------------
# Mistakes
# ---------------------------------------------------------------------------
class MistakeLog(Base, AuditMixin):
    __tablename__ = "mistake_logs"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String, index=True, nullable=True)
    topic = Column(String, index=True, nullable=True)

    question = Column(Text, nullable=True)
    student_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    mistake_type = Column(String, nullable=True)  # conceptual, careless, calculation, incomplete
    source = Column(String, default="quiz")  # quiz, homework, conversation

    repeat_count = Column(Integer, default=1)
    is_resolved = Column(Boolean, default=False)

    student = relationship("StudentProfile", back_populates="mistakes")


# ---------------------------------------------------------------------------
# Frequently asked doubts
# ---------------------------------------------------------------------------
class FrequentDoubt(Base, AuditMixin):
    __tablename__ = "frequent_doubts"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String, index=True, nullable=True)
    topic = Column(String, index=True, nullable=True)
    question_text = Column(Text, nullable=False)
    ask_count = Column(Integer, default=1)
    last_asked_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("StudentProfile", back_populates="doubts")


# ---------------------------------------------------------------------------
# Progress tracking: daily / weekly / monthly
# ---------------------------------------------------------------------------
class DailyProgress(Base, AuditMixin):
    __tablename__ = "daily_progress"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(String, index=True, nullable=False)  # ISO date "YYYY-MM-DD"
    hours_studied = Column(Float, default=0.0)
    topics_covered = Column(JSON, default=list)
    subjects_summary = Column(JSON, default=dict)  # {subject: minutes}
    quizzes_taken = Column(Integer, default=0)
    homework_completed = Column(Integer, default=0)
    average_confidence = Column(Float, nullable=True)
    mood = Column(String, nullable=True)

    student = relationship("StudentProfile", back_populates="daily_progress")


class WeeklyProgress(Base, AuditMixin):
    __tablename__ = "weekly_progress"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    week_start_date = Column(String, index=True, nullable=False)  # ISO date of Monday
    hours_studied = Column(Float, default=0.0)
    topics_covered = Column(JSON, default=list)
    subjects_summary = Column(JSON, default=dict)
    average_score = Column(Float, nullable=True)

    student = relationship("StudentProfile", back_populates="weekly_progress")


class MonthlyProgress(Base, AuditMixin):
    __tablename__ = "monthly_progress"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    hours_studied = Column(Float, default=0.0)
    topics_covered = Column(JSON, default=list)
    subjects_summary = Column(JSON, default=dict)
    average_score = Column(Float, nullable=True)
    improvement_trend = Column(String, nullable=True)  # improving, stable, declining

    student = relationship("StudentProfile", back_populates="monthly_progress")


# ---------------------------------------------------------------------------
# Recommendation Engine output
# ---------------------------------------------------------------------------
class Recommendation(Base, AuditMixin):
    __tablename__ = "recommendations"

    student_id = Column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    # daily_plan, weekly_plan, revision_plan, practice_questions, homework, exam_prep
    subject = Column(String, nullable=True)
    title = Column(String, nullable=False)
    content = Column(JSON, nullable=False)  # structured plan payload
    priority = Column(String, default="medium")  # high, medium, low
    due_date = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False)

    student = relationship("StudentProfile", back_populates="recommendations")
