from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


# ---------------------------------------------------------------------------
# Student Memory (free-form facts)
# ---------------------------------------------------------------------------
class StudentMemoryCreate(BaseModel):
    student_id: UUID
    key: str
    value: str
    category: str = "general"
    importance: int = 1


class StudentMemoryOut(StudentMemoryCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Conversation Memory
# ---------------------------------------------------------------------------
class ConversationMemoryCreate(BaseModel):
    student_id: UUID
    subject_id: Optional[UUID] = None
    question: str
    response: str
    topic: Optional[str] = None
    difficulty: str = "medium"
    follow_up_to_id: Optional[UUID] = None


class ConversationMemoryOut(ConversationMemoryCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Learning Profile
# ---------------------------------------------------------------------------
class LearningProfileOut(BaseModel):
    id: UUID
    student_id: UUID
    visual: float
    auditory: float
    kinesthetic: float
    reading_writing: float
    preferred_explanation_style: str
    weak_subjects: List[str]
    strong_subjects: List[str]
    knowledge_level: str
    difficulty_level: str
    learning_speed: str
    attention_score: float
    confidence_score: float
    revision_frequency: str
    revision_recommendation: Optional[str] = None
    last_analyzed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class LearningStyleUpdate(BaseModel):
    visual: Optional[float] = None
    auditory: Optional[float] = None
    kinesthetic: Optional[float] = None
    reading_writing: Optional[float] = None
    preferred_explanation_style: Optional[str] = None


# ---------------------------------------------------------------------------
# Weakness Profile
# ---------------------------------------------------------------------------
class WeaknessProfileOut(BaseModel):
    id: UUID
    student_id: UUID
    subjects_weakness: Dict[str, Any]
    weak_chapters: List[Any]
    weak_concepts: List[Any]
    frequent_mistakes: List[Any]
    forgotten_topics: List[Any]
    last_analyzed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Quiz Attempts
# ---------------------------------------------------------------------------
class QuizAttemptCreate(BaseModel):
    student_id: UUID
    subject_id: Optional[UUID] = None
    quiz_title: str
    topic: Optional[str] = None
    difficulty: str = "medium"
    total_questions: int
    correct_answers: int
    time_taken_seconds: Optional[int] = None


class QuizAttemptOut(QuizAttemptCreate):
    id: UUID
    score: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Mistakes
# ---------------------------------------------------------------------------
class MistakeLogCreate(BaseModel):
    student_id: UUID
    subject: Optional[str] = None
    topic: Optional[str] = None
    question: Optional[str] = None
    student_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    mistake_type: Optional[str] = None
    source: str = "quiz"


class MistakeLogOut(MistakeLogCreate):
    id: UUID
    repeat_count: int
    is_resolved: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Frequent Doubts
# ---------------------------------------------------------------------------
class FrequentDoubtOut(BaseModel):
    id: UUID
    student_id: UUID
    subject: Optional[str] = None
    topic: Optional[str] = None
    question_text: str
    ask_count: int
    last_asked_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------
class DailyProgressCreate(BaseModel):
    student_id: UUID
    date: str
    hours_studied: float = 0.0
    topics_covered: List[str] = []
    subjects_summary: Dict[str, Any] = {}
    quizzes_taken: int = 0
    homework_completed: int = 0
    average_confidence: Optional[float] = None
    mood: Optional[str] = None


class DailyProgressOut(DailyProgressCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WeeklyProgressOut(BaseModel):
    id: UUID
    student_id: UUID
    week_start_date: str
    hours_studied: float
    topics_covered: List[Any]
    subjects_summary: Dict[str, Any]
    average_score: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class MonthlyProgressOut(BaseModel):
    id: UUID
    student_id: UUID
    month: int
    year: int
    hours_studied: float
    topics_covered: List[Any]
    subjects_summary: Dict[str, Any]
    average_score: Optional[float] = None
    improvement_trend: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------
class RecommendationOut(BaseModel):
    id: UUID
    student_id: UUID
    type: str
    subject: Optional[str] = None
    title: str
    content: Any
    priority: str
    due_date: Optional[datetime] = None
    is_completed: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Teacher Insights / Principal Analytics (pure response DTOs, not persisted)
# ---------------------------------------------------------------------------
class StudentPerformanceSummary(BaseModel):
    student_id: UUID
    full_name: Optional[str] = None
    average_score: Optional[float] = None
    confidence_score: Optional[float] = None
    weak_subjects: List[str] = []
    strong_subjects: List[str] = []


class TopicPerformance(BaseModel):
    topic: str
    average_score: float
    attempts: int


class ClassSummary(BaseModel):
    class_id: UUID
    class_name: str
    student_count: int
    average_score: Optional[float] = None
    homework_completion_rate: Optional[float] = None
    attendance_rate: Optional[float] = None


class HomeworkCompletionSummary(BaseModel):
    class_id: UUID
    total_homework: int
    total_expected_submissions: int
    total_actual_submissions: int
    completion_rate: float


class AttendanceCorrelation(BaseModel):
    class_id: UUID
    correlation_coefficient: Optional[float] = None
    sample_size: int
    interpretation: str


class SchoolPerformance(BaseModel):
    school_id: UUID
    school_name: str
    average_score: Optional[float] = None
    total_students: int
    total_teachers: int
    total_classes: int


class SubjectPerformance(BaseModel):
    subject_id: UUID
    subject_name: str
    average_score: Optional[float] = None
    total_exams: int


class TeacherPerformance(BaseModel):
    teacher_id: UUID
    full_name: Optional[str] = None
    subjects_taught: List[str] = []
    average_student_score: Optional[float] = None


class AIUsageStats(BaseModel):
    total_conversations: int
    total_quiz_attempts: int
    active_students: int
    average_conversations_per_student: float


# ---------------------------------------------------------------------------
# Parent <-> Student linking
# ---------------------------------------------------------------------------
class ParentStudentLinkCreate(BaseModel):
    parent_id: UUID
    student_id: UUID
    relationship_type: str = "guardian"


class ParentStudentLinkOut(ParentStudentLinkCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
