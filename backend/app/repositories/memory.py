from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.memory import (
    StudentMemory,
    ConversationMemory,
    LearningProfile,
    WeaknessProfile,
    QuizAttempt,
    MistakeLog,
    FrequentDoubt,
    DailyProgress,
    WeeklyProgress,
    MonthlyProgress,
    Recommendation,
)


class StudentMemoryRepository(BaseRepository[StudentMemory]):
    def __init__(self, db: AsyncSession):
        super().__init__(StudentMemory, db)

    async def get_by_student(self, student_id: UUID, category: Optional[str] = None) -> List[StudentMemory]:
        query = select(self.model).where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
        if category:
            query = query.where(self.model.category == category)
        result = await self.db.execute(query.order_by(desc(self.model.importance), desc(self.model.created_at)))
        return result.scalars().all()


class ConversationMemoryRepository(BaseRepository[ConversationMemory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ConversationMemory, db)

    async def get_by_student(self, student_id: UUID, limit: int = 50) -> List[ConversationMemory]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_topic(self, student_id: UUID, topic: str) -> List[ConversationMemory]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.topic == topic,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_since(self, student_id: UUID, since: datetime) -> List[ConversationMemory]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.created_at >= since,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class LearningProfileRepository(BaseRepository[LearningProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(LearningProfile, db)

    async def get_by_student(self, student_id: UUID) -> Optional[LearningProfile]:
        query = select(self.model).where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_or_create(self, student_id: UUID) -> LearningProfile:
        existing = await self.get_by_student(student_id)
        if existing:
            return existing
        obj = self.model(student_id=student_id)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


class WeaknessProfileRepository(BaseRepository[WeaknessProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(WeaknessProfile, db)

    async def get_by_student(self, student_id: UUID) -> Optional[WeaknessProfile]:
        query = select(self.model).where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_or_create(self, student_id: UUID) -> WeaknessProfile:
        existing = await self.get_by_student(student_id)
        if existing:
            return existing
        obj = self.model(student_id=student_id)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, db: AsyncSession):
        super().__init__(QuizAttempt, db)

    async def get_by_student(self, student_id: UUID, limit: int = 100) -> List[QuizAttempt]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_since(self, student_id: UUID, since: datetime) -> List[QuizAttempt]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.created_at >= since,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class MistakeLogRepository(BaseRepository[MistakeLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(MistakeLog, db)

    async def get_by_student(self, student_id: UUID, unresolved_only: bool = False) -> List[MistakeLog]:
        query = select(self.model).where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
        if unresolved_only:
            query = query.where(self.model.is_resolved.is_(False))
        result = await self.db.execute(query.order_by(desc(self.model.repeat_count)))
        return result.scalars().all()

    async def find_similar(self, student_id: UUID, topic: Optional[str], mistake_type: Optional[str]) -> Optional[MistakeLog]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.topic == topic,
            self.model.mistake_type == mistake_type,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()


class FrequentDoubtRepository(BaseRepository[FrequentDoubt]):
    def __init__(self, db: AsyncSession):
        super().__init__(FrequentDoubt, db)

    async def get_by_student(self, student_id: UUID) -> List[FrequentDoubt]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
            .order_by(desc(self.model.ask_count))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_matching(self, student_id: UUID, topic: Optional[str], question_text: str) -> Optional[FrequentDoubt]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.topic == topic,
            self.model.question_text == question_text,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def upsert_doubt(self, student_id: UUID, subject: Optional[str], topic: Optional[str], question_text: str) -> FrequentDoubt:
        existing = await self.find_matching(student_id, topic, question_text)
        if existing:
            existing.ask_count += 1
            existing.last_asked_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        obj = self.model(student_id=student_id, subject=subject, topic=topic, question_text=question_text)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


class DailyProgressRepository(BaseRepository[DailyProgress]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyProgress, db)

    async def get_by_student(self, student_id: UUID, limit: int = 30) -> List[DailyProgress]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
            .order_by(desc(self.model.date))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_student_and_date(self, student_id: UUID, date: str) -> Optional[DailyProgress]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.date == date,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def upsert(self, student_id: UUID, date: str, **fields) -> DailyProgress:
        existing = await self.get_by_student_and_date(student_id, date)
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        obj = self.model(student_id=student_id, date=date, **fields)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


class WeeklyProgressRepository(BaseRepository[WeeklyProgress]):
    def __init__(self, db: AsyncSession):
        super().__init__(WeeklyProgress, db)

    async def get_by_student(self, student_id: UUID, limit: int = 12) -> List[WeeklyProgress]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
            .order_by(desc(self.model.week_start_date))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_student_and_week(self, student_id: UUID, week_start_date: str) -> Optional[WeeklyProgress]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.week_start_date == week_start_date,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def upsert(self, student_id: UUID, week_start_date: str, **fields) -> WeeklyProgress:
        existing = await self.get_by_student_and_week(student_id, week_start_date)
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        obj = self.model(student_id=student_id, week_start_date=week_start_date, **fields)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


class MonthlyProgressRepository(BaseRepository[MonthlyProgress]):
    def __init__(self, db: AsyncSession):
        super().__init__(MonthlyProgress, db)

    async def get_by_student(self, student_id: UUID, limit: int = 12) -> List[MonthlyProgress]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
            .order_by(desc(self.model.year), desc(self.model.month))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_student_month(self, student_id: UUID, month: int, year: int) -> Optional[MonthlyProgress]:
        query = select(self.model).where(
            self.model.student_id == student_id,
            self.model.month == month,
            self.model.year == year,
            self.model.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def upsert(self, student_id: UUID, month: int, year: int, **fields) -> MonthlyProgress:
        existing = await self.get_by_student_month(student_id, month, year)
        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        obj = self.model(student_id=student_id, month=month, year=year, **fields)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Recommendation, db)

    async def get_by_student(self, student_id: UUID, type: Optional[str] = None, limit: int = 50) -> List[Recommendation]:
        query = select(self.model).where(self.model.student_id == student_id, self.model.deleted_at.is_(None))
        if type:
            query = query.where(self.model.type == type)
        query = query.order_by(desc(self.model.created_at)).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_latest_by_type(self, student_id: UUID, type: str) -> Optional[Recommendation]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id, self.model.type == type, self.model.deleted_at.is_(None))
            .order_by(desc(self.model.created_at))
        )
        result = await self.db.execute(query)
        return result.scalars().first()
