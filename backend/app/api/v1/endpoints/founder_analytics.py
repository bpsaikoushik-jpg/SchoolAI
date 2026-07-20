from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.founder_analytics_service import FounderAnalyticsService
from app.schemas.founder import (
    FounderSchoolPerformance, OrgAttendanceOverviewOut, OrgHomeworkSummary,
    OrgExamSummary, OrgStudentAnalyticsOut, OrgTeacherAnalyticsOut,
)

router = APIRouter()

founder_roles = RoleChecker([UserRole.FOUNDER, UserRole.ADMIN])


@router.get("/school-performance", response_model=List[FounderSchoolPerformance])
async def school_performance(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAnalyticsService(db).school_performance()


@router.get("/attendance", response_model=OrgAttendanceOverviewOut)
async def attendance_overview(
    on_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(founder_roles),
):
    return await FounderAnalyticsService(db).attendance_overview(on_date)


@router.get("/homework", response_model=List[OrgHomeworkSummary])
async def homework_overview(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAnalyticsService(db).homework_overview()


# Exams and Results Analytics both read from the same org-wide rollup,
# same as the Principal Portal's single exams-overview endpoint already
# backs its separate Exam Monitoring and Results Monitoring pages.
@router.get("/exams", response_model=List[OrgExamSummary])
async def exam_overview(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAnalyticsService(db).exam_overview()


@router.get("/students", response_model=OrgStudentAnalyticsOut)
async def student_analytics(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAnalyticsService(db).student_analytics()


@router.get("/teachers", response_model=OrgTeacherAnalyticsOut)
async def teacher_analytics(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAnalyticsService(db).teacher_analytics()
