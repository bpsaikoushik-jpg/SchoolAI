from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.principal_analytics_service import PrincipalAnalyticsService
from app.schemas.memory import (
    SchoolPerformance,
    ClassSummary,
    SubjectPerformance,
    TeacherPerformance,
    AIUsageStats,
)

router = APIRouter()

principal_roles = RoleChecker([UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


@router.get("/school-performance/{school_id}", response_model=SchoolPerformance)
async def school_performance(school_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(principal_roles)):
    return await PrincipalAnalyticsService(db).school_performance(school_id)


@router.get("/class-performance/{school_id}", response_model=list[ClassSummary])
async def class_performance(school_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(principal_roles)):
    return await PrincipalAnalyticsService(db).class_performance(school_id)


@router.get("/subject-performance/{school_id}", response_model=list[SubjectPerformance])
async def subject_performance(school_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(principal_roles)):
    return await PrincipalAnalyticsService(db).subject_performance(school_id)


@router.get("/teacher-performance/{school_id}", response_model=list[TeacherPerformance])
async def teacher_performance(school_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(principal_roles)):
    return await PrincipalAnalyticsService(db).teacher_performance(school_id)


@router.get("/ai-usage/{school_id}", response_model=AIUsageStats)
async def ai_usage(school_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(principal_roles)):
    return await PrincipalAnalyticsService(db).ai_usage_stats(school_id)
