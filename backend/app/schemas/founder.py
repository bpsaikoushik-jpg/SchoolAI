from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------------------------------------------------------------------------
# School management (Founder Portal: platform-wide, every school)
# ---------------------------------------------------------------------------
class SchoolManageOut(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime
    total_students: int = 0
    total_teachers: int = 0
    total_classes: int = 0
    average_score: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class SchoolCreateInput(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    # Optionally onboard the school's Principal account in the same step.
    principal_email: Optional[EmailStr] = None
    principal_password: Optional[str] = None
    principal_full_name: Optional[str] = None


class SchoolUpdateInput(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


# ---------------------------------------------------------------------------
# Organization overview
# ---------------------------------------------------------------------------
class OrgOverviewOut(BaseModel):
    total_schools: int
    active_schools: int
    inactive_schools: int
    total_students: int
    total_teachers: int
    total_parents: int
    total_staff: int
    average_score: Optional[float] = None


class RoleBreakdownItem(BaseModel):
    role: str
    count: int


# ---------------------------------------------------------------------------
# Org-wide user directory (backs Founder notifications audience + user list)
# ---------------------------------------------------------------------------
class OrgUserOut(BaseModel):
    user_id: UUID
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    school_id: Optional[UUID] = None
    school_name: Optional[str] = None


# ---------------------------------------------------------------------------
# Org-wide school performance (Multi-School Dashboard / School Performance)
# ---------------------------------------------------------------------------
class FounderSchoolPerformance(BaseModel):
    school_id: UUID
    school_name: str
    is_active: bool
    average_score: Optional[float] = None
    total_students: int
    total_teachers: int
    total_classes: int


# ---------------------------------------------------------------------------
# Org-wide attendance
# ---------------------------------------------------------------------------
class SchoolAttendanceSummary(BaseModel):
    school_id: UUID
    school_name: str
    present: int
    absent: int
    late: int
    total_marked: int


class OrgAttendanceOverviewOut(BaseModel):
    date: date
    present: int
    absent: int
    late: int
    total_marked: int
    by_school: List[SchoolAttendanceSummary]


# ---------------------------------------------------------------------------
# Org-wide homework
# ---------------------------------------------------------------------------
class OrgHomeworkSummary(BaseModel):
    school_id: UUID
    school_name: str
    total_assigned: int
    total_submitted: int
    total_students_covered: int
    completion_rate: Optional[float] = None


# ---------------------------------------------------------------------------
# Org-wide exams / results (one shape backs both Exam Analytics and
# Results Analytics pages, mirroring how the Principal Portal's
# exams-overview endpoint already backs two separate pages).
# ---------------------------------------------------------------------------
class OrgExamSummary(BaseModel):
    school_id: UUID
    school_name: str
    total_exams: int
    results_recorded: int
    average_score: Optional[float] = None


# ---------------------------------------------------------------------------
# Org-wide student / teacher analytics
# ---------------------------------------------------------------------------
class SchoolStudentSummary(BaseModel):
    school_id: UUID
    school_name: str
    student_count: int
    average_score: Optional[float] = None


class GradeLevelSummary(BaseModel):
    grade_level: Optional[int] = None
    count: int


class OrgStudentAnalyticsOut(BaseModel):
    by_school: List[SchoolStudentSummary]
    by_grade: List[GradeLevelSummary]


class SchoolTeacherSummary(BaseModel):
    school_id: UUID
    school_name: str
    teacher_count: int


class TopTeacher(BaseModel):
    teacher_id: UUID
    full_name: Optional[str] = None
    school_name: str
    subjects_taught: List[str] = []
    average_student_score: Optional[float] = None


class OrgTeacherAnalyticsOut(BaseModel):
    by_school: List[SchoolTeacherSummary]
    top_teachers: List[TopTeacher]
