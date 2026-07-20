import enum
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import AuditMixin, Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
    PRINCIPAL = "principal"
    ADMIN = "admin"
    FOUNDER = "founder"

class User(Base, AuditMixin):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    
    school_id = Column(ForeignKey("schools.id", ondelete="SET NULL"), nullable=True)
    
    school = relationship("School", back_populates="users")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)
    parent_profile = relationship("ParentProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
