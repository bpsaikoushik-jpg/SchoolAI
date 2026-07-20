from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, resolve_target_student_id
from app.models.user import UserRole, User
from app.services.learning_profile_service import LearningProfileService
from app.services.weakness_engine_service import WeaknessEngineService
from app.services.recommendation_engine_service import RecommendationEngineService
from app.schemas.memory import (
    LearningProfileOut,
    LearningStyleUpdate,
    WeaknessProfileOut,
    RecommendationOut,
)

router = APIRouter()

all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


# -- Learning Profile ---------------------------------------------------------
@router.get("/profile/{student_id}", response_model=LearningProfileOut)
async def get_learning_profile(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await LearningProfileService(db).get_profile(student_id)


@router.put("/profile/{student_id}/learning-style", response_model=LearningProfileOut)
async def update_learning_style(student_id: UUID, payload: LearningStyleUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await LearningProfileService(db).update_learning_style(student_id, payload)


@router.post("/profile/{student_id}/recompute", response_model=LearningProfileOut)
async def recompute_learning_profile(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await LearningProfileService(db).recompute(student_id)


# -- Weakness Engine ------------------------------------------------------------
@router.get("/weakness/{student_id}", response_model=WeaknessProfileOut)
async def get_weakness_profile(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    from app.repositories.memory import WeaknessProfileRepository
    return await WeaknessProfileRepository(db).get_or_create(student_id)


@router.post("/weakness/{student_id}/analyze", response_model=WeaknessProfileOut)
async def analyze_weakness(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await WeaknessEngineService(db).analyze(student_id)


# -- Recommendation Engine -------------------------------------------------------
@router.get("/recommendations/daily/{student_id}", response_model=RecommendationOut)
async def daily_plan(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await RecommendationEngineService(db).generate_daily_plan(student_id)


@router.get("/recommendations/weekly/{student_id}", response_model=RecommendationOut)
async def weekly_plan(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await RecommendationEngineService(db).generate_weekly_plan(student_id)


@router.get("/recommendations/revision/{student_id}", response_model=RecommendationOut)
async def revision_plan(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await RecommendationEngineService(db).generate_revision_plan(student_id)


@router.get("/recommendations/practice/{student_id}", response_model=RecommendationOut)
async def practice_questions(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await RecommendationEngineService(db).recommend_practice_questions(student_id)


@router.get("/recommendations/homework/{student_id}", response_model=RecommendationOut)
async def homework_recommendation(student_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await RecommendationEngineService(db).recommend_homework(student_id)


@router.get("/recommendations/exam-prep/{student_id}", response_model=RecommendationOut)
async def exam_prep_plan(student_id: UUID, days_ahead: int = 30, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    return await RecommendationEngineService(db).generate_exam_prep_plan(student_id, days_ahead)


@router.get("/recommendations/{student_id}", response_model=list[RecommendationOut])
async def list_recommendations(student_id: UUID, type: str | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(all_roles)):
    from app.repositories.memory import RecommendationRepository
    return await RecommendationRepository(db).get_by_student(student_id, type)


@router.get("/recommendations/me/list", response_model=list[RecommendationOut])
async def my_recommendations(type: str | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(RoleChecker([UserRole.STUDENT]))):
    """Convenience endpoint so the student dashboard doesn't need to know its own profile id."""
    from app.repositories.memory import RecommendationRepository
    student_id = await resolve_target_student_id(None, db, user)
    return await RecommendationRepository(db).get_by_student(student_id, type)
