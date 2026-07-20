from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# AI Mentor - chat
# ---------------------------------------------------------------------------
class MentorChatRequest(BaseModel):
    student_id: Optional[UUID] = None  # optional for students (defaults to self); required for staff/parent
    message: str
    subject: Optional[str] = None
    subject_id: Optional[UUID] = None
    topic: Optional[str] = None
    mode: str = "normal"  # easy | normal | advanced


class MentorChatResponse(BaseModel):
    response: str
    provider: str
    model: str
    subject: Optional[str] = None
    subject_id: Optional[UUID] = None
    topic: Optional[str] = None


# ---------------------------------------------------------------------------
# AI Mentor - quiz / flashcards
# ---------------------------------------------------------------------------
class MentorQuizRequest(BaseModel):
    student_id: Optional[UUID] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    num_questions: int = 5
    difficulty: str = "medium"


class MentorFlashcardRequest(BaseModel):
    student_id: Optional[UUID] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    count: int = 8


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------
class PredictionResult(BaseModel):
    model_config = ConfigDict(extra="allow")


# ---------------------------------------------------------------------------
# Teacher / Parent / Principal AI
# ---------------------------------------------------------------------------
class AISummaryResponse(BaseModel):
    data: Dict[str, Any]
    ai_summary: Optional[str] = None
    ai_recommendations: Optional[str] = None


class ChildSummary(BaseModel):
    student_id: UUID
    full_name: Optional[str] = None
    grade_level: Optional[int] = None
    relationship_type: str
