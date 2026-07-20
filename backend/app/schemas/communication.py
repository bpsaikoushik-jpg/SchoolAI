from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    message: str
    is_read: bool
    type: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str
    message: str
    type: Optional[str] = "system"


class BroadcastCreate(BaseModel):
    user_ids: List[UUID]
    title: str
    message: str
    type: Optional[str] = "announcement"


class UnreadCountOut(BaseModel):
    unread: int
