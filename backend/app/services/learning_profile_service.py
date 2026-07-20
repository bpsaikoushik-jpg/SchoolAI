from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.memory import LearningProfileRepository
from app.models.memory import QuizAttempt, ConversationMemory
from app.schemas.memory import LearningStyleUpdate
from app.services.weakness_engine_service import WeaknessEngineService


class LearningProfileService:
    """Auto-maintains each student's learning profile: knowledge level,
    difficulty level, learning speed, attention score, revision frequency
    and revision recommendations, plus cached weak/strong subjects."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LearningProfileRepository(db)
        self.weakness_engine = WeaknessEngineService(db)

    async def get_profile(self, student_id: UUID):
        return await self.repo.get_or_create(student_id)

    async def update_learning_style(self, student_id: UUID, data: LearningStyleUpdate):
        profile = await self.repo.get_or_create(student_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def recompute(self, student_id: UUID):
        profile = await self.repo.get_or_create(student_id)

        # 1. Recompute weakness data first - it feeds knowledge/difficulty/confidence.
        weakness = await self.weakness_engine.analyze(student_id)

        # 2. Knowledge level & difficulty level from overall quiz average.
        avg_query = select(func.avg(QuizAttempt.score)).where(
            QuizAttempt.student_id == student_id, QuizAttempt.deleted_at.is_(None)
        )
        avg_score = (await self.db.execute(avg_query)).scalar()

        if avg_score is None:
            knowledge_level, difficulty_level = "beginner", "easy"
        elif avg_score >= 85:
            knowledge_level, difficulty_level = "advanced", "hard"
        elif avg_score >= 60:
            knowledge_level, difficulty_level = "intermediate", "medium"
        else:
            knowledge_level, difficulty_level = "beginner", "easy"

        # 3. Confidence score = overall average score, dampened toward 50 when little data.
        confidence_score = round(avg_score, 2) if avg_score is not None else 50.0

        # 4. Learning speed from how quickly scores are trending upward across attempts.
        recent_query = (
            select(QuizAttempt.score, QuizAttempt.created_at)
            .where(QuizAttempt.student_id == student_id, QuizAttempt.deleted_at.is_(None))
            .order_by(QuizAttempt.created_at)
        )
        attempts = (await self.db.execute(recent_query)).all()
        learning_speed = "average"
        if len(attempts) >= 4:
            midpoint = len(attempts) // 2
            first_half_avg = sum(a.score for a in attempts[:midpoint]) / midpoint
            second_half_avg = sum(a.score for a in attempts[midpoint:]) / (len(attempts) - midpoint)
            delta = second_half_avg - first_half_avg
            if delta >= 10:
                learning_speed = "fast"
            elif delta <= -5:
                learning_speed = "slow"

        # 5. Attention score from conversation engagement frequency over the last 14 days.
        since = datetime.now(timezone.utc) - timedelta(days=14)
        convo_count_query = select(func.count(ConversationMemory.id)).where(
            ConversationMemory.student_id == student_id,
            ConversationMemory.deleted_at.is_(None),
            ConversationMemory.created_at >= since,
        )
        convo_count = (await self.db.execute(convo_count_query)).scalar() or 0
        # Heuristic: 1+ interaction/day over 14 days -> 100, scaled down from there.
        attention_score = min(100.0, round((convo_count / 14) * 100, 2))
        if convo_count == 0:
            attention_score = 30.0  # low baseline rather than 0, avoids over-penalizing new students

        # 6. Revision frequency & recommendation from forgotten topics count.
        forgotten_count = len(weakness.forgotten_topics or [])
        if forgotten_count >= 5:
            revision_frequency = "daily"
        elif forgotten_count >= 3:
            revision_frequency = "every_2_days"
        elif forgotten_count >= 1:
            revision_frequency = "weekly"
        else:
            revision_frequency = "biweekly"

        if forgotten_count:
            topic_list = ", ".join(t["topic"] for t in weakness.forgotten_topics[:3])
            revision_recommendation = (
                f"Revise {topic_list} soon - these haven't been touched in a while."
            )
        else:
            revision_recommendation = "No overdue topics right now - keep up regular practice."

        # 7. Weak / strong subjects cached from WeaknessProfile.subjects_weakness.
        weak_subjects = [s for s, score in (weakness.subjects_weakness or {}).items() if score and score >= 40]
        strong_subjects = [s for s, score in (weakness.subjects_weakness or {}).items() if score is not None and score < 20]

        profile.knowledge_level = knowledge_level
        profile.difficulty_level = difficulty_level
        profile.confidence_score = confidence_score
        profile.learning_speed = learning_speed
        profile.attention_score = attention_score
        profile.revision_frequency = revision_frequency
        profile.revision_recommendation = revision_recommendation
        profile.weak_subjects = weak_subjects
        profile.strong_subjects = strong_subjects
        profile.last_analyzed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile
