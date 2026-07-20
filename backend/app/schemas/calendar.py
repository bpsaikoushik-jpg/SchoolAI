from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CalendarEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: str = "task"  # class, meeting, task, other
    starts_at: datetime
    ends_at: Optional[datetime] = None
    class_id: Optional[UUID] = None


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    class_id: Optional[UUID] = None


class CalendarEventOut(BaseModel):
    id: UUID
    school_id: UUID
    owner_id: UUID
    class_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    event_type: str
    starts_at: datetime
    ends_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
