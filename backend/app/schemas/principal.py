from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------------------------------------------------------------------------
# School overview
# ---------------------------------------------------------------------------
class SchoolOut(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Student management
# ---------------------------------------------------------------------------
class StudentCreateByPrincipal(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    student_id_number: Optional[str] = None
    grade_level: Optional[int] = None
    class_id: Optional[UUID] = None  # optionally enroll immediately


class StudentUpdateByPrincipal(BaseModel):
    full_name: Optional[str] = None
    student_id_number: Optional[str] = None
    grade_level: Optional[int] = None
    is_active: Optional[bool] = None


class StudentManageOut(BaseModel):
    user_id: UUID
    student_id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool
    student_id_number: Optional[str] = None
    grade_level: Optional[int] = None
    class_id: Optional[UUID] = None
    class_name: Optional[str] = None


# ---------------------------------------------------------------------------
# Teacher management
# ---------------------------------------------------------------------------
class TeacherCreateByPrincipal(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    employee_id: Optional[str] = None
    specialization: Optional[str] = None


class TeacherUpdateByPrincipal(BaseModel):
    full_name: Optional[str] = None
    employee_id: Optional[str] = None
    specialization: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherManageOut(BaseModel):
    user_id: UUID
    teacher_id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool
    employee_id: Optional[str] = None
    specialization: Optional[str] = None
    subjects_count: int = 0


# ---------------------------------------------------------------------------
# Attendance monitoring
# ---------------------------------------------------------------------------
class ClassAttendanceSummary(BaseModel):
    class_id: UUID
    class_name: str
    present: int
    absent: int
    late: int
    total_marked: int


class AttendanceOverviewOut(BaseModel):
    date: date
    present: int
    absent: int
    late: int
    total_marked: int
    by_class: List[ClassAttendanceSummary]


# ---------------------------------------------------------------------------
# Homework / assignment monitoring
# ---------------------------------------------------------------------------
class HomeworkOverviewItem(BaseModel):
    id: UUID
    title: str
    class_id: UUID
    class_name: str
    due_date: Optional[datetime] = None
    submitted: int
    total_students: int
    completion_rate: Optional[float] = None


# ---------------------------------------------------------------------------
# Exam / results monitoring
# ---------------------------------------------------------------------------
class ExamOverviewItem(BaseModel):
    id: UUID
    title: str
    subject_id: UUID
    subject_name: str
    class_id: Optional[UUID] = None
    class_name: Optional[str] = None
    date: Optional[datetime] = None
    results_recorded: int
    average_score: Optional[float] = None
