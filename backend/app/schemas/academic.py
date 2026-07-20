from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ClassBase(BaseModel):
    name: str
    school_id: UUID


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: Optional[str] = None


class ClassOut(ClassBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubjectBase(BaseModel):
    name: str
    teacher_id: Optional[UUID] = None
    class_id: Optional[UUID] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[UUID] = None
    class_id: Optional[UUID] = None


class SubjectOut(SubjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EnrollmentBase(BaseModel):
    student_id: UUID
    class_id: UUID


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentOut(EnrollmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TeacherContactOut(BaseModel):
    """Read-only directory entry used by the Parent Portal's Communication
    page: which teacher teaches which subject for a given child."""
    subject_id: UUID
    subject_name: str
    teacher_id: Optional[UUID] = None
    teacher_name: Optional[str] = None
    specialization: Optional[str] = None
