from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, resolve_target_student_id
from app.models.user import UserRole, User
from app.repositories.academic import EnrollmentRepository
from app.services.calendar_service import CalendarService
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEventOut

router = APIRouter()

staff_roles = RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


@router.post("", response_model=CalendarEventOut, status_code=status.HTTP_201_CREATED)
async def create_event(payload: CalendarEventCreate, db: AsyncSession = Depends(get_db), user: User = Depends(staff_roles)):
    if not user.school_id:
        raise HTTPException(status_code=400, detail="Account has no school assigned")
    return await CalendarService(db).create_event(user.id, user.school_id, payload)


@router.get("/me", response_model=list[CalendarEventOut])
async def my_events(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(staff_roles),
):
    return await CalendarService(db).get_my_events(user.id, start, end)


@router.get("/me/today", response_model=list[CalendarEventOut])
async def my_events_today(db: AsyncSession = Depends(get_db), user: User = Depends(staff_roles)):
    return await CalendarService(db).get_today(user.id)


@router.get("/student", response_model=list[CalendarEventOut])
async def student_calendar_events(
    student_id: Optional[UUID] = Query(None),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Class-linked calendar events for a student (parent/student view).
    Never exposes a staff member's personal, unlinked events."""
    target_id = await resolve_target_student_id(student_id, db, user)
    class_ids = [e.class_id for e in await EnrollmentRepository(db).get_by_student(target_id)]
    return await CalendarService(db).get_for_classes(class_ids, start, end)


@router.patch("/{event_id}", response_model=CalendarEventOut)
async def update_event(event_id: UUID, payload: CalendarEventUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(staff_roles)):
    is_admin = user.role in (UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER)
    try:
        updated = await CalendarService(db).update_event(event_id, payload, user.id, is_admin)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(staff_roles)):
    is_admin = user.role in (UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER)
    try:
        await CalendarService(db).delete_event(event_id, user.id, is_admin)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
