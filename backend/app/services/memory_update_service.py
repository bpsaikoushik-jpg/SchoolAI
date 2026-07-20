"""Memory Update Engine.

After every AI Mentor response this service:
  1. Logs the conversation turn (synchronous - needed immediately for /mentor/history)
  2. Bumps today's daily progress (topic covered, subject minutes, mood if given)
  3. Recomputes the Learning Profile + Weakness Profile (confidence score,
     weak/strong subjects, revision recommendation, ...)
  4. Regenerates the daily study-plan recommendation
  5. Rolls up weekly/monthly progress

Steps 3-5 are pure re-aggregations of existing data (not needed to answer the
current request) and are comparatively expensive, so callers normally run
them via FastAPI BackgroundTasks rather than blocking the chat response.
"""
from datetime import date as date_cls
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.student_memory_service import StudentMemoryService
from app.services.learning_profile_service import LearningProfileService
from app.services.recommendation_engine_service import RecommendationEngineService
from app.schemas.memory import ConversationMemoryCreate, DailyProgressCreate


class MemoryUpdateService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.memory = StudentMemoryService(db)
        self.learning_profile_service = LearningProfileService(db)
        self.recommendation_engine = RecommendationEngineService(db)

    async def log_interaction(
        self,
        student_id: UUID,
        question: str,
        response: str,
        subject_id: Optional[UUID] = None,
        topic: Optional[str] = None,
        difficulty: str = "medium",
    ):
        """Synchronous part: must happen before the API responds so
        /mentor/history immediately reflects this turn."""
        return await self.memory.log_conversation(
            ConversationMemoryCreate(
                student_id=student_id,
                subject_id=subject_id,
                question=question,
                response=response,
                topic=topic,
                difficulty=difficulty,
            )
        )

    async def bump_daily_progress(self, student_id: UUID, subject: Optional[str], topic: Optional[str], minutes: int = 5):
        today = date_cls.today().isoformat()
        existing = await self.memory.daily_progress.get_by_student_and_date(student_id, today)

        topics_covered = list(existing.topics_covered) if existing and existing.topics_covered else []
        if topic and topic not in topics_covered:
            topics_covered.append(topic)

        subjects_summary = dict(existing.subjects_summary) if existing and existing.subjects_summary else {}
        if subject:
            subjects_summary[subject] = subjects_summary.get(subject, 0) + minutes

        hours_studied = (existing.hours_studied if existing else 0.0) + (minutes / 60.0)

        return await self.memory.record_daily_progress(
            DailyProgressCreate(
                student_id=student_id,
                date=today,
                hours_studied=round(hours_studied, 3),
                topics_covered=topics_covered,
                subjects_summary=subjects_summary,
                quizzes_taken=existing.quizzes_taken if existing else 0,
                homework_completed=existing.homework_completed if existing else 0,
                average_confidence=existing.average_confidence if existing else None,
                mood=existing.mood if existing else None,
            )
        )

    async def refresh_profiles_and_recommendations(self, student_id: UUID, regenerate_daily_plan: bool = True):
        """Heavier re-aggregation work - safe to run as a background task."""
        await self.learning_profile_service.recompute(student_id)  # also recomputes weakness profile
        if regenerate_daily_plan:
            await self.recommendation_engine.generate_daily_plan(student_id)
        await self.memory.aggregate_weekly_progress(student_id)
        await self.memory.aggregate_monthly_progress(student_id)

    async def full_update_after_interaction(
        self,
        student_id: UUID,
        question: str,
        response: str,
        subject_id: Optional[UUID] = None,
        subject_name: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: str = "medium",
    ):
        """Convenience method that runs everything sequentially. Used when
        there's no background-task runner available (e.g. streaming
        endpoint after the last chunk)."""
        convo = await self.log_interaction(student_id, question, response, subject_id, topic, difficulty)
        await self.bump_daily_progress(student_id, subject_name, topic)
        await self.refresh_profiles_and_recommendations(student_id)
        return convo
