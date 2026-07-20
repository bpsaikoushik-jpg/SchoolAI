from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base

class Attendance(Base, AuditMixin):
    __tablename__ = "attendance"

    student_id = Column(ForeignKey("student_profiles.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False) # present, absent, late

    student = relationship("StudentProfile", back_populates="attendances")

class Homework(Base, AuditMixin):
    __tablename__ = "homework"

    class_id = Column(ForeignKey("classes.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)

    class_room = relationship("Class", back_populates="homeworks")
    submissions = relationship("AssignmentSubmission", back_populates="homework")

class AssignmentSubmission(Base, AuditMixin):
    __tablename__ = "assignment_submissions"

    homework_id = Column(ForeignKey("homework.id"), nullable=False)
    student_id = Column(ForeignKey("student_profiles.id"), nullable=False)
    content = Column(Text)
    grade = Column(String)

    homework = relationship("Homework", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="submissions")

class Exam(Base, AuditMixin):
    __tablename__ = "exams"

    subject_id = Column(ForeignKey("subjects.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime)

    subject = relationship("Subject", back_populates="exams")
    results = relationship("Result", back_populates="exam")

class Result(Base, AuditMixin):
    __tablename__ = "results"

    exam_id = Column(ForeignKey("exams.id"), nullable=False)
    student_id = Column(ForeignKey("student_profiles.id"), nullable=False)
    score = Column(Float)
    remarks = Column(Text)

    exam = relationship("Exam", back_populates="results")
    student = relationship("StudentProfile", back_populates="results")
