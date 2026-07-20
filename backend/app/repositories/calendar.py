from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.calendar import CalendarEvent


class CalendarEventRepository(BaseRepository[CalendarEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(CalendarEvent, db)

    async def get_by_owner(self, owner_id: UUID, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[CalendarEvent]:
        query = select(self.model).where(self.model.owner_id == owner_id, self.model.deleted_at.is_(None))
        if start is not None:
            query = query.where(self.model.starts_at >= start)
        if end is not None:
            query = query.where(self.model.starts_at < end)
        query = query.order_by(self.model.starts_at.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_classes(self, class_ids: List[UUID], start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[CalendarEvent]:
        """Class-linked events only (never a teacher's personal, unlinked tasks)."""
        if not class_ids:
            return []
        query = select(self.model).where(
            self.model.class_id.in_(class_ids),
            self.model.deleted_at.is_(None),
        )
        if start is not None:
            query = query.where(self.model.starts_at >= start)
        if end is not None:
            query = query.where(self.model.starts_at < end)
        query = query.order_by(self.model.starts_at.asc())
        result = await self.db.execute(query)
        return result.scalars().all()
