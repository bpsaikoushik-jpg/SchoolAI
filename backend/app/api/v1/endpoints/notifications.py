from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.repositories.communication import NotificationRepository
from app.schemas.communication import NotificationOut, BroadcastCreate, UnreadCountOut

router = APIRouter()

all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
broadcast_roles = RoleChecker([UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


@router.get("", response_model=List[NotificationOut])
async def list_my_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    return await NotificationRepository(db).get_by_user(user.id, unread_only, limit)


@router.get("/unread-count", response_model=UnreadCountOut)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    count = await NotificationRepository(db).unread_count(user.id)
    return UnreadCountOut(unread=count)


@router.post("/{notification_id}/read", response_model=UnreadCountOut)
async def mark_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    repo = NotificationRepository(db)
    ok = await repo.mark_read(notification_id, user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")
    return UnreadCountOut(unread=await repo.unread_count(user.id))


@router.post("/read-all", response_model=UnreadCountOut)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    repo = NotificationRepository(db)
    await repo.mark_all_read(user.id)
    return UnreadCountOut(unread=await repo.unread_count(user.id))


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    notif = await NotificationRepository(db).get(notification_id)
    if not notif or notif.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    await NotificationRepository(db).delete(notification_id)


@router.post("/broadcast", response_model=UnreadCountOut, status_code=status.HTTP_201_CREATED)
async def broadcast_announcement(
    payload: BroadcastCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(broadcast_roles),
):
    count = await NotificationRepository(db).notify_many(
        payload.user_ids, payload.title, payload.message, payload.type or "announcement"
    )
    return UnreadCountOut(unread=count)
