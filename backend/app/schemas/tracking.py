from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ------------------------------------------------------------------
# Attendance
# ------------------------------------------------------------------

class AttendanceBase(BaseModel):
    student_id: UUID
    date: datetime
    status: str = Field(pattern="^(present|absent|late)$")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        return str(value).lower()


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceOut(AttendanceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------
# Homework
# ------------------------------------------------------------------

class HomeworkBase(BaseModel):
    class_id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class HomeworkOut(HomeworkBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------
# Submission
# ------------------------------------------------------------------

class SubmissionBase(BaseModel):
    homework_id: UUID
    student_id: UUID
    content: Optional[str] = None


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionGrade(BaseModel):
    grade: str


class SubmissionOut(SubmissionBase):
    id: UUID
    grade: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------
# Exam
# ------------------------------------------------------------------

class ExamBase(BaseModel):
    subject_id: UUID
    title: str
    date: Optional[datetime] = None


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None


class ExamOut(ExamBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------
# Result
# ------------------------------------------------------------------

class ResultBase(BaseModel):
    exam_id: UUID
    student_id: UUID
    score: Optional[float] = None
    remarks: Optional[str] = None


class ResultCreate(ResultBase):
    pass


class ResultUpdate(BaseModel):
    score: Optional[float] = None
    remarks: Optional[str] = None


class ResultOut(ResultBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------
# Detailed Result
# ------------------------------------------------------------------

class ResultDetailOut(BaseModel):
    """
    Enriched result row joining exam and subject information.
    Used by Parent Portal Results/Performance pages.
    """

    id: UUID
    exam_id: UUID
    student_id: UUID
    score: Optional[float] = None
    remarks: Optional[str] = None

    exam_title: str
    exam_date: Optional[datetime] = None

    subject_id: UUID
    subject_name: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
