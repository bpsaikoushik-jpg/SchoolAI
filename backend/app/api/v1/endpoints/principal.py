from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.principal_service import PrincipalService
from app.schemas.principal import (
    SchoolOut,
    StudentCreateByPrincipal, StudentUpdateByPrincipal, StudentManageOut,
    TeacherCreateByPrincipal, TeacherUpdateByPrincipal, TeacherManageOut,
    AttendanceOverviewOut, HomeworkOverviewItem, ExamOverviewItem,
)

router = APIRouter()

# Matches the manage_roles convention already used in academic.py /
# principal_analytics.py / principal_ai.py: Principal, Admin, and Founder
# all have oversight access to a school's Principal Portal.
manage_roles = RoleChecker([UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


# ---------------------------------------------------------------------------
# School overview
# ---------------------------------------------------------------------------
@router.get("/school/{school_id}", response_model=SchoolOut)
async def get_school(
    school_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).get_school(school_id)


# ---------------------------------------------------------------------------
# Student management
# ---------------------------------------------------------------------------
@router.get("/students/{school_id}", response_model=List[StudentManageOut])
async def list_students(
    school_id: UUID,
    search: Optional[str] = Query(None),
    class_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).list_students(school_id, search, class_id, skip, limit)


@router.post("/students/{school_id}", response_model=StudentManageOut, status_code=status.HTTP_201_CREATED)
async def create_student(
    school_id: UUID,
    payload: StudentCreateByPrincipal,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).create_student(school_id, payload)


@router.patch("/students/{school_id}/{user_id}", response_model=StudentManageOut)
async def update_student(
    school_id: UUID,
    user_id: UUID,
    payload: StudentUpdateByPrincipal,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).update_student(school_id, user_id, payload)


@router.delete("/students/{school_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_student(
    school_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    await PrincipalService(db).deactivate_student(school_id, user_id)


# ---------------------------------------------------------------------------
# Teacher management
# ---------------------------------------------------------------------------
@router.get("/teachers/{school_id}", response_model=List[TeacherManageOut])
async def list_teachers(
    school_id: UUID,
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).list_teachers(school_id, search, skip, limit)


@router.post("/teachers/{school_id}", response_model=TeacherManageOut, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    school_id: UUID,
    payload: TeacherCreateByPrincipal,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).create_teacher(school_id, payload)


@router.patch("/teachers/{school_id}/{user_id}", response_model=TeacherManageOut)
async def update_teacher(
    school_id: UUID,
    user_id: UUID,
    payload: TeacherUpdateByPrincipal,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).update_teacher(school_id, user_id, payload)


@router.delete("/teachers/{school_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_teacher(
    school_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    await PrincipalService(db).deactivate_teacher(school_id, user_id)


# ---------------------------------------------------------------------------
# Attendance / homework / exam monitoring
# ---------------------------------------------------------------------------
@router.get("/attendance-overview/{school_id}", response_model=AttendanceOverviewOut)
async def attendance_overview(
    school_id: UUID,
    on_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).attendance_overview(school_id, on_date)


@router.get("/homework-overview/{school_id}", response_model=List[HomeworkOverviewItem])
async def homework_overview(
    school_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).homework_overview(school_id)


@router.get("/exams-overview/{school_id}", response_model=List[ExamOverviewItem])
async def exams_overview(
    school_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await PrincipalService(db).exams_overview(school_id)
