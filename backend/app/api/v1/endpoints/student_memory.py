from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, resolve_target_student_id
from app.models.user import UserRole, User
from app.services.student_memory_service import StudentMemoryService
from app.schemas.memory import (
    StudentMemoryCreate,
    StudentMemoryOut,
    ConversationMemoryCreate,
    ConversationMemoryOut,
    QuizAttemptCreate,
    QuizAttemptOut,
    MistakeLogCreate,
    MistakeLogOut,
    FrequentDoubtOut,
    DailyProgressCreate,
    DailyProgressOut,
    WeeklyProgressOut,
    MonthlyProgressOut,
)

router = APIRouter()

all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
staff_roles = RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
student_only = RoleChecker([UserRole.STUDENT])


# -- free-form facts -------------------------------------------------------
@router.post("/facts", response_model=StudentMemoryOut)
async def create_fact(payload: StudentMemoryCreate, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).remember(payload)


@router.get("/facts/{student_id}", response_model=list[StudentMemoryOut])
async def list_facts(student_id: UUID, category: Optional[str] = None, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_memories(student_id, category)


# -- conversation memory ----------------------------------------------------
@router.post("/conversations", response_model=ConversationMemoryOut)
async def log_conversation(payload: ConversationMemoryCreate, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).log_conversation(payload)


@router.get("/conversations/{student_id}", response_model=list[ConversationMemoryOut])
async def list_conversations(student_id: UUID, limit: int = 50, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_conversations(student_id, limit)


@router.get("/doubts/{student_id}", response_model=list[FrequentDoubtOut])
async def list_doubts(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_doubts(student_id)


# -- quiz history -------------------------------------------------------------
@router.post("/quiz-attempts", response_model=QuizAttemptOut)
async def log_quiz_attempt(payload: QuizAttemptCreate, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).log_quiz_attempt(payload)


@router.get("/quiz-attempts/{student_id}", response_model=list[QuizAttemptOut])
async def list_quiz_attempts(student_id: UUID, limit: int = 100, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_quiz_history(student_id, limit)


# -- homework history (reuses existing tracking models) -----------------------
@router.get("/homework-history/{student_id}")
async def homework_history(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_homework_history(student_id)


# -- mistakes -------------------------------------------------------------------
@router.post("/mistakes", response_model=MistakeLogOut)
async def log_mistake(payload: MistakeLogCreate, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).log_mistake(payload)


@router.get("/mistakes/{student_id}", response_model=list[MistakeLogOut])
async def list_mistakes(student_id: UUID, unresolved_only: bool = False, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_mistakes(student_id, unresolved_only)


@router.post("/mistakes/{mistake_id}/resolve", response_model=MistakeLogOut)
async def resolve_mistake(mistake_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(staff_roles)):
    return await StudentMemoryService(db).resolve_mistake(mistake_id)


# -- progress -------------------------------------------------------------------
@router.post("/daily-progress", response_model=DailyProgressOut)
async def record_daily_progress(payload: DailyProgressCreate, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).record_daily_progress(payload)


@router.get("/daily-progress/{student_id}", response_model=list[DailyProgressOut])
async def list_daily_progress(student_id: UUID, limit: int = 30, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_daily_progress(student_id, limit)


@router.post("/weekly-progress/{student_id}/recompute", response_model=WeeklyProgressOut)
async def recompute_weekly_progress(student_id: UUID, week_start_date: Optional[str] = None, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).aggregate_weekly_progress(student_id, week_start_date)


@router.get("/weekly-progress/{student_id}", response_model=list[WeeklyProgressOut])
async def list_weekly_progress(student_id: UUID, limit: int = 12, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_weekly_progress(student_id, limit)


@router.post("/monthly-progress/{student_id}/recompute", response_model=MonthlyProgressOut)
async def recompute_monthly_progress(student_id: UUID, month: Optional[int] = None, year: Optional[int] = None, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).aggregate_monthly_progress(student_id, month, year)


@router.get("/monthly-progress/{student_id}", response_model=list[MonthlyProgressOut])
async def list_monthly_progress(student_id: UUID, limit: int = 12, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_monthly_progress(student_id, limit)


# -- "me" convenience endpoints (student dashboard doesn't need its own profile id) --
@router.get("/daily-progress/me/list", response_model=list[DailyProgressOut])
async def my_daily_progress(limit: int = 7, db: AsyncSession = Depends(get_db), user: User = Depends(student_only)):
    student_id = await resolve_target_student_id(None, db, user)
    return await StudentMemoryService(db).get_daily_progress(student_id, limit)


@router.get("/recent-activity/{student_id}")
async def recent_activity(student_id: UUID, limit: int = 10, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await StudentMemoryService(db).get_recent_activity(student_id, limit)


@router.get("/recent-activity/me/list")
async def my_recent_activity(limit: int = 10, db: AsyncSession = Depends(get_db), user: User = Depends(student_only)):
    student_id = await resolve_target_student_id(None, db, user)
    return await StudentMemoryService(db).get_recent_activity(student_id, limit)
