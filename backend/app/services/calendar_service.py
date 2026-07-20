from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.calendar import CalendarEventRepository
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate


class CalendarService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.events = CalendarEventRepository(db)

    async def create_event(self, owner_id: UUID, school_id: UUID, data: CalendarEventCreate):
        payload = data.model_dump()
        payload["owner_id"] = owner_id
        payload["school_id"] = school_id
        return await self.events.create(payload)

    async def update_event(self, event_id: UUID, data: CalendarEventUpdate, requester_id: UUID, requester_is_admin: bool):
        event = await self.events.get(event_id)
        if not event:
            return None
        if not requester_is_admin and event.owner_id != requester_id:
            raise PermissionError("Only the event owner can modify this event")
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.events.update(event_id, payload)

    async def delete_event(self, event_id: UUID, requester_id: UUID, requester_is_admin: bool):
        event = await self.events.get(event_id)
        if not event:
            return False
        if not requester_is_admin and event.owner_id != requester_id:
            raise PermissionError("Only the event owner can delete this event")
        return await self.events.delete(event_id)

    async def get_my_events(self, owner_id: UUID, start: Optional[datetime] = None, end: Optional[datetime] = None):
        return await self.events.get_by_owner(owner_id, start, end)

    async def get_today(self, owner_id: UUID):
        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return await self.events.get_by_owner(owner_id, start, end)

    async def get_for_classes(self, class_ids, start: Optional[datetime] = None, end: Optional[datetime] = None):
        return await self.events.get_by_classes(class_ids, start, end)
