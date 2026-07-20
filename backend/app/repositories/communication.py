from typing import List
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.communication import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_by_user(self, user_id: UUID, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        query = select(self.model).where(self.model.user_id == user_id, self.model.deleted_at.is_(None))
        if unread_only:
            query = query.where(self.model.is_read.is_(False))
        query = query.order_by(self.model.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def unread_count(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(self.model).where(
            self.model.user_id == user_id,
            self.model.is_read.is_(False),
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> bool:
        query = (
            update(self.model)
            .where(self.model.id == notification_id, self.model.user_id == user_id)
            .values(is_read=True)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def mark_all_read(self, user_id: UUID) -> int:
        query = (
            update(self.model)
            .where(self.model.user_id == user_id, self.model.is_read.is_(False))
            .values(is_read=True)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

    async def notify(self, user_id: UUID, title: str, message: str, type_: str = "system") -> Notification:
        return await self.create({
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type_,
        })

    async def notify_many(self, user_ids: List[UUID], title: str, message: str, type_: str = "system") -> int:
        count = 0
        for uid in user_ids:
            await self.notify(uid, title, message, type_)
            count += 1
        return count
