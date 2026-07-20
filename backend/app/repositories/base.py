from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id, self.model.deleted_at == None)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).where(self.model.deleted_at == None).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_ids(self, ids: List[UUID]) -> List[ModelType]:
        if not ids:
            return []
        query = select(self.model).where(self.model.id.in_(ids), self.model.deleted_at == None)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: Any) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: UUID, obj_in: Any) -> Optional[ModelType]:
        query = update(self.model).where(self.model.id == id).values(**obj_in).returning(self.model)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalars().first()

    async def delete(self, id: UUID) -> bool:
        # Soft delete
        from datetime import datetime
        query = update(self.model).where(self.model.id == id).values(deleted_at=datetime.utcnow())
        await self.db.execute(query)
        await self.db.commit()
        return True
