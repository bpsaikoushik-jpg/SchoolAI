"""AI Mentor - the student-facing AI tutor.

Every answer is grounded in the Context Engine (student memory, learning
profile, weakness profile, previous conversations, current subject/topic)
and, after answering, hands off to the Memory Update Engine so the next
answer is even better informed.
"""
import json
import logging
import re
from typing import AsyncIterator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_client, AIClient
from app.ai.schemas import AIAllProvidersFailedError
from app.ai import prompts
from app.services.context_engine_service import ContextEngineService
from app.services.recommendation_engine_service import RecommendationEngineService

logger = logging.getLogger("schoolai.mentor")


def _extract_json(text: str) -> dict:
    """LLMs occasionally wrap JSON in markdown fences despite instructions -
    strip those before parsing, and fall back gracefully on failure."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return json.loads(cleaned)


class AIMentorService:
    def __init__(self, db: AsyncSession, ai_client: Optional[AIClient] = None):
        self.db = db
        self.context_engine = ContextEngineService(db)
        self.recommendation_engine = RecommendationEngineService(db)
        self.ai = ai_client or get_ai_client()

    # -- core chat -----------------------------------------------------
    async def chat(
        self,
        student_id: UUID,
        question: str,
        subject: Optional[str] = None,
        subject_id: Optional[UUID] = None,
        topic: Optional[str] = None,
        mode: str = "normal",
    ) -> dict:
        context = await self.context_engine.build_student_context(student_id, subject, topic)
        messages = prompts.mentor_messages(context, question, mode)
        try:
            completion = await self.ai.complete(messages)
        except AIAllProvidersFailedError as exc:
            logger.error("AI Mentor chat failed for student %s: %s", student_id, exc)
            raise
        return {
            "response": completion.content,
            "provider": completion.provider,
            "model": completion.model,
            "subject_id": subject_id,
            "subject": subject,
            "topic": topic,
        }

    async def stream_chat(
        self,
        student_id: UUID,
        question: str,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        mode: str = "normal",
    ) -> AsyncIterator[str]:
        context = await self.context_engine.build_student_context(student_id, subject, topic)
        messages = prompts.mentor_messages(context, question, mode)
        async for chunk in self.ai.stream(messages):
            yield chunk

    # -- quiz / flashcards ------------------------------------------------
    async def generate_quiz(self, student_id: UUID, subject: Optional[str], topic: Optional[str], num_questions: int = 5, difficulty: str = "medium") -> dict:
        context = await self.context_engine.build_student_context(student_id, subject, topic)
        messages = prompts.quiz_generation_messages(context, subject, topic, num_questions, difficulty)
        completion = await self.ai.complete(messages, temperature=0.6)
        try:
            data = _extract_json(completion.content)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Quiz generation returned non-JSON for student %s; returning raw text.", student_id)
            data = {"questions": [], "raw_response": completion.content}
        data["subject"] = subject
        data["topic"] = topic
        data["difficulty"] = difficulty
        return data

    async def generate_flashcards(self, student_id: UUID, subject: Optional[str], topic: Optional[str], count: int = 8) -> dict:
        context = await self.context_engine.build_student_context(student_id, subject, topic)
        messages = prompts.flashcard_generation_messages(context, subject, topic, count)
        completion = await self.ai.complete(messages, temperature=0.5)
        try:
            data = _extract_json(completion.content)
        except (json.JSONDecodeError, ValueError):
            data = {"flashcards": [], "raw_response": completion.content}
        data["subject"] = subject
        data["topic"] = topic
        return data

    # -- study planning (wraps the deterministic Recommendation Engine with an AI narrative) --
    async def study_plan_with_narrative(self, student_id: UUID) -> dict:
        plan = await self.recommendation_engine.generate_daily_plan(student_id)
        context = await self.context_engine.build_student_context(student_id)
        messages = prompts.study_plan_narrative_messages(context, plan.content, "daily study plan")
        completion = await self.ai.complete(messages, temperature=0.5)
        return {"plan": plan, "narrative": completion.content}

    async def revision_plan_with_narrative(self, student_id: UUID) -> dict:
        plan = await self.recommendation_engine.generate_revision_plan(student_id)
        context = await self.context_engine.build_student_context(student_id)
        messages = prompts.study_plan_narrative_messages(context, plan.content, "revision plan")
        completion = await self.ai.complete(messages, temperature=0.5)
        return {"plan": plan, "narrative": completion.content}

    # -- motivation & goals -------------------------------------------------
    async def motivation_message(self, student_id: UUID) -> str:
        context = await self.context_engine.build_student_context(student_id)
        messages = prompts.motivation_messages(context)
        completion = await self.ai.complete(messages, temperature=0.7, max_tokens=200)
        return completion.content

    async def daily_learning_goal(self, student_id: UUID) -> dict:
        context = await self.context_engine.build_student_context(student_id)
        messages = prompts.daily_goal_messages(context)
        completion = await self.ai.complete(messages, temperature=0.5, max_tokens=150)
        goal_text = completion.content.strip()
        saved = await self.recommendation_engine.save_recommendation(
            student_id,
            type="daily_goal",
            title="Today's Learning Goal",
            content={"goal": goal_text},
            priority="high",
        )
        return {"goal": goal_text, "recommendation": saved}
