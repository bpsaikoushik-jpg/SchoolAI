"""Context Engine.

Pulls only the *relevant* slice of everything SchoolAI knows about a student
- memory, conversation history, homework, exams, recommendations, learning
profile, weakness profile, previous mistakes, current goals - and shapes it
into a compact dict the AI Mentor (and Teacher/Parent/Principal AI) can turn
into a prompt. Keeping this in one place means every AI-facing service uses
the same context instead of hand-rolling its own queries.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.memory import (
    LearningProfileRepository,
    WeaknessProfileRepository,
    RecommendationRepository,
)
from app.services.student_memory_service import StudentMemoryService


class ContextEngineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.learning_profiles = LearningProfileRepository(db)
        self.weakness_profiles = WeaknessProfileRepository(db)
        self.recommendations = RecommendationRepository(db)
        self.memory = StudentMemoryService(db)

    async def build_student_context(
        self,
        student_id: UUID,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        conversation_limit: int = 6,
    ) -> dict:
        learning_profile = await self.learning_profiles.get_or_create(student_id)
        weakness_profile = await self.weakness_profiles.get_or_create(student_id)

        recent_conversations = await self.memory.get_conversations(student_id, limit=conversation_limit)
        recent_mistakes = await self.memory.get_mistakes(student_id, unresolved_only=True)
        recent_quiz_attempts = await self.memory.get_quiz_history(student_id, limit=10)
        long_term_facts = await self.memory.get_memories(student_id)
        active_recommendations = await self.recommendations.get_by_student(student_id, limit=5)

        return {
            "student_id": str(student_id),
            "current_subject": subject,
            "current_topic": topic,
            "learning_profile": {
                "knowledge_level": learning_profile.knowledge_level,
                "difficulty_level": learning_profile.difficulty_level,
                "learning_speed": learning_profile.learning_speed,
                "preferred_explanation_style": learning_profile.preferred_explanation_style,
                "confidence_score": learning_profile.confidence_score,
                "attention_score": learning_profile.attention_score,
                "revision_frequency": learning_profile.revision_frequency,
                "weak_subjects": learning_profile.weak_subjects,
                "strong_subjects": learning_profile.strong_subjects,
            },
            "weakness_profile": {
                "weak_chapters": weakness_profile.weak_chapters,
                "weak_concepts": weakness_profile.weak_concepts,
                "frequent_mistakes": weakness_profile.frequent_mistakes,
                "forgotten_topics": weakness_profile.forgotten_topics,
            },
            "unresolved_mistakes": [
                {"topic": m.topic, "mistake_type": m.mistake_type, "repeat_count": m.repeat_count}
                for m in recent_mistakes[:5]
            ],
            "recent_quiz_attempts": [
                {"topic": q.topic, "score": q.score, "difficulty": q.difficulty}
                for q in recent_quiz_attempts[:5]
            ],
            "long_term_facts": [
                {"key": f.key, "value": f.value, "category": f.category} for f in long_term_facts[:10]
            ],
            "active_goals": [
                {"type": r.type, "title": r.title, "priority": r.priority}
                for r in active_recommendations if not r.is_completed
            ],
            "previous_conversations": [
                {"question": c.question, "response": c.response[:400], "topic": c.topic}
                for c in reversed(recent_conversations)
            ],
        }
