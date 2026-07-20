from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base

class StudentProfile(Base, AuditMixin):
    __tablename__ = "student_profiles"

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id_number = Column(String, unique=True, index=True)
    grade_level = Column(Integer)
    bio = Column(Text)

    user = relationship("User", back_populates="student_profile")
    enrollments = relationship("Enrollment", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    submissions = relationship("AssignmentSubmission", back_populates="student")
    results = relationship("Result", back_populates="student")
    memories = relationship("StudentMemory", back_populates="student")
    conversations = relationship("ConversationMemory", back_populates="student")
    learning_profile = relationship("LearningProfile", back_populates="student", uselist=False)
    weakness_profile = relationship("WeaknessProfile", back_populates="student", uselist=False)
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    mistakes = relationship("MistakeLog", back_populates="student")
    doubts = relationship("FrequentDoubt", back_populates="student")
    daily_progress = relationship("DailyProgress", back_populates="student")
    weekly_progress = relationship("WeeklyProgress", back_populates="student")
    monthly_progress = relationship("MonthlyProgress", back_populates="student")
    recommendations = relationship("Recommendation", back_populates="student")
    parent_links = relationship("ParentStudentLink", back_populates="student", foreign_keys="ParentStudentLink.student_id")

class TeacherProfile(Base, AuditMixin):
    __tablename__ = "teacher_profiles"

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = Column(String, unique=True, index=True)
    specialization = Column(String)

    user = relationship("User", back_populates="teacher_profile")
    subjects = relationship("Subject", back_populates="teacher")

class ParentProfile(Base, AuditMixin):
    __tablename__ = "parent_profiles"

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    occupation = Column(String)

    user = relationship("User", back_populates="parent_profile")
    child_links = relationship("ParentStudentLink", back_populates="parent", foreign_keys="ParentStudentLink.parent_id")
