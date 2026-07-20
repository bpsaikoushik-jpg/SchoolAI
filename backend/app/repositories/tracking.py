from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.tracking import Attendance, Homework, AssignmentSubmission, Exam, Result


class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, db: AsyncSession):
        super().__init__(Attendance, db)

    async def get_by_student(
        self,
        student_id: UUID,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Attendance]:
        conditions = [self.model.student_id == student_id, self.model.deleted_at.is_(None)]
        if start:
            conditions.append(self.model.date >= start)
        if end:
            conditions.append(self.model.date <= end)
        query = select(self.model).where(and_(*conditions)).order_by(self.model.date.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_for_student_on_date(self, student_id: UUID, on_date: date) -> Optional[Attendance]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        rows = result.scalars().all()
        for row in rows:
            if row.date.date() == on_date:
                return row
        return None

    async def upsert(self, student_id: UUID, on_date: datetime, status: str) -> Attendance:
        existing = await self.get_for_student_on_date(student_id, on_date.date())
        if existing:
            existing.status = status
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        return await self.create({"student_id": student_id, "date": on_date, "status": status})


class HomeworkRepository(BaseRepository[Homework]):
    def __init__(self, db: AsyncSession):
        super().__init__(Homework, db)

    async def get_by_class(self, class_id: UUID) -> List[Homework]:
        query = (
            select(self.model)
            .where(self.model.class_id == class_id, self.model.deleted_at.is_(None))
            .order_by(self.model.due_date.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_classes(self, class_ids: List[UUID]) -> List[Homework]:
        if not class_ids:
            return []
        query = (
            select(self.model)
            .where(self.model.class_id.in_(class_ids), self.model.deleted_at.is_(None))
            .order_by(self.model.due_date.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class AssignmentSubmissionRepository(BaseRepository[AssignmentSubmission]):
    def __init__(self, db: AsyncSession):
        super().__init__(AssignmentSubmission, db)

    async def get_by_homework(self, homework_id: UUID) -> List[AssignmentSubmission]:
        query = select(self.model).where(
            self.model.homework_id == homework_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_student(self, student_id: UUID) -> List[AssignmentSubmission]:
        query = select(self.model).where(
            self.model.student_id == student_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_existing(self, homework_id: UUID, student_id: UUID) -> Optional[AssignmentSubmission]:
        query = select(self.model).where(
            self.model.homework_id == homework_id,
            self.model.student_id == student_id,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()


class ExamRepository(BaseRepository[Exam]):
    def __init__(self, db: AsyncSession):
        super().__init__(Exam, db)

    async def get_by_subject(self, subject_id: UUID) -> List[Exam]:
        query = (
            select(self.model)
            .where(self.model.subject_id == subject_id, self.model.deleted_at.is_(None))
            .order_by(self.model.date.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_subjects(self, subject_ids: List[UUID]) -> List[Exam]:
        if not subject_ids:
            return []
        query = (
            select(self.model)
            .where(self.model.subject_id.in_(subject_ids), self.model.deleted_at.is_(None))
            .order_by(self.model.date.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class ResultRepository(BaseRepository[Result]):
    def __init__(self, db: AsyncSession):
        super().__init__(Result, db)

    async def get_by_exam(self, exam_id: UUID) -> List[Result]:
        query = select(self.model).where(
            self.model.exam_id == exam_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_student(self, student_id: UUID) -> List[Result]:
        query = select(self.model).where(
            self.model.student_id == student_id, self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_existing(self, exam_id: UUID, student_id: UUID) -> Optional[Result]:
        query = select(self.model).where(
            self.model.exam_id == exam_id,
            self.model.student_id == student_id,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()
