from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_client, AIClient
from app.ai import prompts
from app.services.teacher_insight_service import TeacherInsightService


class TeacherAIService:
    """Wraps TeacherInsightService's deterministic class analytics with an
    AI-generated plain-language summary and concrete teaching suggestions."""

    def __init__(self, db: AsyncSession, ai_client: Optional[AIClient] = None):
        self.db = db
        self.insight = TeacherInsightService(db)
        self.ai = ai_client or get_ai_client()

    async def ai_summary(self, class_id: UUID) -> dict:
        class_summary = await self.insight.class_summary(class_id)
        weak_students = await self.insight.weak_students(class_id)
        strong_students = await self.insight.strong_students(class_id)
        homework_completion = await self.insight.homework_completion(class_id)
        attendance_correlation = await self.insight.attendance_correlation(class_id)

        payload = {
            "class_summary": class_summary,
            "weak_students": weak_students,
            "strong_students": strong_students,
            "homework_completion": homework_completion,
            "attendance_correlation": attendance_correlation,
        }

        messages = prompts.teacher_ai_summary_messages(payload)
        completion = await self.ai.complete(messages, temperature=0.5)

        return {
            "data": payload,
            "ai_summary": completion.content,
        }
