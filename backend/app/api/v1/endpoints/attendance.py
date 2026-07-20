from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, resolve_target_student_id, authorize_student_data_access
from app.models.user import UserRole, User
from app.repositories.academic import EnrollmentRepository
from app.repositories.tracking import AttendanceRepository
from app.schemas.tracking import AttendanceCreate, AttendanceOut

router = APIRouter()

record_roles = RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


@router.post("", response_model=AttendanceOut, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    payload: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(record_roles),
):
    return await AttendanceRepository(db).upsert(payload.student_id, payload.date, payload.status)


@router.get("/student", response_model=List[AttendanceOut])
async def get_student_attendance(
    student_id: Optional[UUID] = Query(None),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target_id = await resolve_target_student_id(student_id, db, user)
    return await AttendanceRepository(db).get_by_student(target_id, start, end)


@router.get("/class/{class_id}", response_model=List[AttendanceOut])
async def get_class_attendance(
    class_id: UUID,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])),
):
    enrollments = await EnrollmentRepository(db).get_by_class(class_id)
    attendance_repo = AttendanceRepository(db)
    records = []
    for enrollment in enrollments:
        records.extend(await attendance_repo.get_by_student(enrollment.student_id, start, end))
    return records


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    attendance_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(record_roles),
):
    await AttendanceRepository(db).delete(attendance_id)
