from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AttendanceBase(BaseModel):
    student_id: UUID
    date: datetime
    status: str = Field(pattern="^(present|absent|late)$")


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceOut(AttendanceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


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


class ResultDetailOut(BaseModel):
    """Enriched result row (joins exam title + subject name) used by the
    Parent Portal's Results/Performance pages, which have no other way to
    resolve exam metadata for a bare student_id/exam_id result list."""
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
