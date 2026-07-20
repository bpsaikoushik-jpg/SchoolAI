from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.family import ParentStudentLink


class ParentStudentLinkRepository(BaseRepository[ParentStudentLink]):
    def __init__(self, db: AsyncSession):
        super().__init__(ParentStudentLink, db)

    async def get_children(self, parent_id: UUID) -> List[ParentStudentLink]:
        query = select(self.model).where(self.model.parent_id == parent_id, self.model.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def is_linked(self, parent_id: UUID, student_id: UUID) -> bool:
        query = select(self.model).where(
            self.model.parent_id == parent_id,
            self.model.student_id == student_id,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    async def link(self, parent_id: UUID, student_id: UUID, relationship_type: str = "guardian") -> ParentStudentLink:
        existing_query = select(self.model).where(
            self.model.parent_id == parent_id,
            self.model.student_id == student_id,
        )
        existing = (await self.db.execute(existing_query)).scalars().first()
        if existing:
            existing.deleted_at = None
            existing.relationship_type = relationship_type
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        return await self.create({
            "parent_id": parent_id,
            "student_id": student_id,
            "relationship_type": relationship_type,
        })
