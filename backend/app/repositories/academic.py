from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.academic import Class, Subject, Enrollment


class ClassRepository(BaseRepository[Class]):
    def __init__(self, db: AsyncSession):
        super().__init__(Class, db)

    async def get_by_school(self, school_id: UUID) -> List[Class]:
        query = select(self.model).where(
            self.model.school_id == school_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self, db: AsyncSession):
        super().__init__(Subject, db)

    async def get_by_teacher(self, teacher_id: UUID) -> List[Subject]:
        query = select(self.model).where(
            self.model.teacher_id == teacher_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_class(self, class_id: UUID) -> List[Subject]:
        query = select(self.model).where(
            self.model.class_id == class_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_classes(self, class_ids: List[UUID]) -> List[Subject]:
        if not class_ids:
            return []
        query = select(self.model).where(
            self.model.class_id.in_(class_ids), self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Enrollment, db)

    async def get_by_student(self, student_id: UUID) -> List[Enrollment]:
        query = select(self.model).where(
            self.model.student_id == student_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_class(self, class_id: UUID) -> List[Enrollment]:
        query = select(self.model).where(
            self.model.class_id == class_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_existing(self, student_id: UUID, class_id: UUID) -> Optional[Enrollment]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.class_id == class_id,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()
