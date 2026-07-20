from uuid import UUID
from datetime import datetime, timezone
from collections import defaultdict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.memory import WeaknessProfileRepository
from app.models.memory import QuizAttempt, MistakeLog, ConversationMemory

WEAK_SCORE_THRESHOLD = 60.0
FORGOTTEN_AFTER_DAYS = 14
FREQUENT_MISTAKE_MIN_COUNT = 2


class WeaknessEngineService:
    """Detects weak chapters/concepts, frequently repeated mistakes, and
    topics the student hasn't revisited in a while, and persists the
    result on WeaknessProfile."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WeaknessProfileRepository(db)

    async def analyze(self, student_id: UUID):
        weak_concepts, subjects_weakness = await self._analyze_quiz_performance(student_id)
        weak_chapters = await self._analyze_chapter_performance(student_id)
        frequent_mistakes = await self._analyze_frequent_mistakes(student_id)
        forgotten_topics = await self._analyze_forgotten_topics(student_id)

        profile = await self.repo.get_or_create(student_id)
        profile.subjects_weakness = subjects_weakness
        profile.weak_chapters = weak_chapters
        profile.weak_concepts = weak_concepts
        profile.frequent_mistakes = frequent_mistakes
        profile.forgotten_topics = forgotten_topics
        profile.last_analyzed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def _analyze_quiz_performance(self, student_id: UUID):
        query = select(
            QuizAttempt.topic,
            func.avg(QuizAttempt.score).label("avg_score"),
            func.count(QuizAttempt.id).label("attempts"),
        ).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.deleted_at.is_(None),
            QuizAttempt.topic.is_not(None),
        ).group_by(QuizAttempt.topic)
        result = await self.db.execute(query)
        rows = result.all()

        weak_concepts = [
            {"topic": r.topic, "avg_score": round(float(r.avg_score), 2), "attempts": r.attempts}
            for r in rows if r.avg_score is not None and r.avg_score < WEAK_SCORE_THRESHOLD
        ]

        # Subject-level weakness via subject relationship
        subj_query = select(
            QuizAttempt.subject_id,
            func.avg(QuizAttempt.score).label("avg_score"),
        ).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.deleted_at.is_(None),
            QuizAttempt.subject_id.is_not(None),
        ).group_by(QuizAttempt.subject_id)
        subj_result = await self.db.execute(subj_query)
        subjects_weakness = {}
        for r in subj_result.all():
            weakness_score = round(100 - float(r.avg_score), 2) if r.avg_score is not None else None
            subjects_weakness[str(r.subject_id)] = weakness_score

        return weak_concepts, subjects_weakness

    async def _analyze_chapter_performance(self, student_id: UUID):
        # "Chapter" maps to quiz_title, which typically encodes the chapter/unit name.
        query = select(
            QuizAttempt.quiz_title,
            func.avg(QuizAttempt.score).label("avg_score"),
        ).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.deleted_at.is_(None),
        ).group_by(QuizAttempt.quiz_title)
        result = await self.db.execute(query)
        rows = result.all()
        return [
            {"chapter": r.quiz_title, "avg_score": round(float(r.avg_score), 2)}
            for r in rows if r.avg_score is not None and r.avg_score < WEAK_SCORE_THRESHOLD
        ]

    async def _analyze_frequent_mistakes(self, student_id: UUID):
        query = select(MistakeLog).where(
            MistakeLog.student_id == student_id,
            MistakeLog.deleted_at.is_(None),
            MistakeLog.repeat_count >= FREQUENT_MISTAKE_MIN_COUNT,
        )
        result = await self.db.execute(query)
        rows = result.scalars().all()
        return [
            {"topic": m.topic, "mistake_type": m.mistake_type, "count": m.repeat_count}
            for m in rows
        ]

    async def _analyze_forgotten_topics(self, student_id: UUID):
        """A topic is 'forgotten' if the student hasn't asked about it or been
        quizzed on it in FORGOTTEN_AFTER_DAYS days, but has engaged with it before."""
        now = datetime.now(timezone.utc)
        last_seen: dict = defaultdict(lambda: None)

        convo_query = select(
            ConversationMemory.topic, func.max(ConversationMemory.created_at)
        ).where(
            ConversationMemory.student_id == student_id,
            ConversationMemory.deleted_at.is_(None),
            ConversationMemory.topic.is_not(None),
        ).group_by(ConversationMemory.topic)
        for topic, last_dt in (await self.db.execute(convo_query)).all():
            if topic:
                last_seen[topic] = max(filter(None, [last_seen[topic], last_dt]))

        quiz_query = select(
            QuizAttempt.topic, func.max(QuizAttempt.created_at)
        ).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.deleted_at.is_(None),
            QuizAttempt.topic.is_not(None),
        ).group_by(QuizAttempt.topic)
        for topic, last_dt in (await self.db.execute(quiz_query)).all():
            if topic:
                last_seen[topic] = max(filter(None, [last_seen[topic], last_dt]))

        forgotten = []
        for topic, last_dt in last_seen.items():
            if last_dt is None:
                continue
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            days_ago = (now - last_dt).days
            if days_ago >= FORGOTTEN_AFTER_DAYS:
                forgotten.append({"topic": topic, "last_seen_days_ago": days_ago})

        return sorted(forgotten, key=lambda x: -x["last_seen_days_ago"])
