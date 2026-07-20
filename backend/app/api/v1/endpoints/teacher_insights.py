from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, get_own_teacher_profile_id
from app.models.user import UserRole, User
from app.services.teacher_insight_service import TeacherInsightService
from app.schemas.memory import (
    StudentPerformanceSummary,
    TopicPerformance,
    ClassSummary,
    HomeworkCompletionSummary,
    AttendanceCorrelation,
)

router = APIRouter()

teacher_roles = RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
teacher_only = RoleChecker([UserRole.TEACHER])


async def _own_teacher_id(db: AsyncSession, user: User):
    teacher_id = await get_own_teacher_profile_id(db, user)
    if teacher_id is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No teacher profile found for this account")
    return teacher_id


@router.get("/my-classes")
async def my_classes(db: AsyncSession = Depends(get_db), user: User = Depends(teacher_only)):
    teacher_id = await _own_teacher_id(db, user)
    return await TeacherInsightService(db).my_classes(teacher_id)


@router.get("/attendance-today")
async def attendance_today(db: AsyncSession = Depends(get_db), user: User = Depends(teacher_only)):
    teacher_id = await _own_teacher_id(db, user)
    return await TeacherInsightService(db).attendance_today(teacher_id)


@router.get("/homework-queue")
async def homework_queue(limit: int = 10, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_only)):
    teacher_id = await _own_teacher_id(db, user)
    return await TeacherInsightService(db).homework_queue(teacher_id, limit)


@router.get("/my-students")
async def my_students(db: AsyncSession = Depends(get_db), user: User = Depends(teacher_only)):
    teacher_id = await _own_teacher_id(db, user)
    return await TeacherInsightService(db).my_students(teacher_id)


@router.get("/weak-students/{class_id}", response_model=list[StudentPerformanceSummary])
async def weak_students(class_id: UUID, threshold: float = 60.0, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_roles)):
    return await TeacherInsightService(db).weak_students(class_id, threshold)


@router.get("/strong-students/{class_id}", response_model=list[StudentPerformanceSummary])
async def strong_students(class_id: UUID, threshold: float = 80.0, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_roles)):
    return await TeacherInsightService(db).strong_students(class_id, threshold)


@router.get("/topic-performance/{subject_id}", response_model=list[TopicPerformance])
async def topic_performance(subject_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_roles)):
    return await TeacherInsightService(db).topic_wise_performance(subject_id)


@router.get("/class-summary/{class_id}", response_model=ClassSummary)
async def class_summary(class_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_roles)):
    return await TeacherInsightService(db).class_summary(class_id)


@router.get("/homework-completion/{class_id}", response_model=HomeworkCompletionSummary)
async def homework_completion(class_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_roles)):
    return await TeacherInsightService(db).homework_completion(class_id)


@router.get("/attendance-correlation/{class_id}", response_model=AttendanceCorrelation)
async def attendance_correlation(class_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_roles)):
    return await TeacherInsightService(db).attendance_correlation(class_id)
