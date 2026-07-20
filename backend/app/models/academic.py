from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base

class Class(Base, AuditMixin):
    __tablename__ = "classes"

    name = Column(String, nullable=False)
    school_id = Column(ForeignKey("schools.id"), nullable=False)
    
    school = relationship("School", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_room")
    homeworks = relationship("Homework", back_populates="class_room")
    subjects = relationship("Subject", back_populates="class_room")

class Subject(Base, AuditMixin):
    __tablename__ = "subjects"

    name = Column(String, nullable=False)
    teacher_id = Column(ForeignKey("teacher_profiles.id"), nullable=True)
    class_id = Column(ForeignKey("classes.id"), nullable=True)
    
    teacher = relationship("TeacherProfile", back_populates="subjects")
    class_room = relationship("Class", back_populates="subjects")
    exams = relationship("Exam", back_populates="subject")

class Enrollment(Base, AuditMixin):
    __tablename__ = "enrollments"

    student_id = Column(ForeignKey("student_profiles.id"), nullable=False)
    class_id = Column(ForeignKey("classes.id"), nullable=False)
    
    student = relationship("StudentProfile", back_populates="enrollments")
    class_room = relationship("Class", back_populates="enrollments")
