from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_client, AIClient
from app.ai import prompts
from app.repositories.family import ParentStudentLinkRepository
from app.repositories.memory import LearningProfileRepository, WeaknessProfileRepository
from app.services.student_memory_service import StudentMemoryService
from app.services.teacher_insight_service import TeacherInsightService
from app.services.recommendation_engine_service import RecommendationEngineService
from app.models.profiles import StudentProfile, ParentProfile
from app.models.user import User


class ParentAIService:
    def __init__(self, db: AsyncSession, ai_client: Optional[AIClient] = None):
        self.db = db
        self.links = ParentStudentLinkRepository(db)
        self.learning_profiles = LearningProfileRepository(db)
        self.weakness_profiles = WeaknessProfileRepository(db)
        self.memory = StudentMemoryService(db)
        self.teacher_insight = TeacherInsightService(db)
        self.recommendation_engine = RecommendationEngineService(db)
        self.ai = ai_client or get_ai_client()

    async def get_children(self, parent_profile_id: UUID) -> List[dict]:
        links = await self.links.get_children(parent_profile_id)
        children = []
        for link in links:
            sp_query = select(StudentProfile, User).join(User, StudentProfile.user_id == User.id).where(StudentProfile.id == link.student_id)
            row = (await self.db.execute(sp_query)).first()
            if row:
                children.append({
                    "student_id": link.student_id,
                    "full_name": row.User.full_name,
                    "grade_level": row.StudentProfile.grade_level,
                    "relationship_type": link.relationship_type,
                })
        return children

    async def child_progress(self, student_id: UUID) -> dict:
        learning_profile = await self.learning_profiles.get_or_create(student_id)
        weakness_profile = await self.weakness_profiles.get_or_create(student_id)
        weekly = await self.memory.get_weekly_progress(student_id, limit=1)
        monthly = await self.memory.get_monthly_progress(student_id, limit=1)

        def _week_dict(w):
            return {
                "week_start_date": w.week_start_date,
                "hours_studied": w.hours_studied,
                "topics_covered": w.topics_covered,
                "subjects_summary": w.subjects_summary,
                "average_score": w.average_score,
            }

        def _month_dict(m):
            return {
                "month": m.month,
                "year": m.year,
                "hours_studied": m.hours_studied,
                "average_score": m.average_score,
                "improvement_trend": m.improvement_trend,
            }

        return {
            "knowledge_level": learning_profile.knowledge_level,
            "confidence_score": learning_profile.confidence_score,
            "learning_speed": learning_profile.learning_speed,
            "weak_subjects": learning_profile.weak_subjects,
            "strong_subjects": learning_profile.strong_subjects,
            "weak_chapters": weakness_profile.weak_chapters,
            "forgotten_topics": weakness_profile.forgotten_topics,
            "latest_week": _week_dict(weekly[0]) if weekly else None,
            "latest_month": _month_dict(monthly[0]) if monthly else None,
        }

    async def attendance_summary(self, student_id: UUID) -> dict:
        rate = await self.teacher_insight.attendance_rate([student_id])
        return {"attendance_rate": rate}

    async def homework_status(self, student_id: UUID) -> List[dict]:
        return await self.memory.get_homework_history(student_id)

    async def exam_preparation(self, student_id: UUID):
        return await self.recommendation_engine.generate_exam_prep_plan(student_id)

    async def full_summary(self, student_id: UUID) -> dict:
        progress = await self.child_progress(student_id)
        attendance = await self.attendance_summary(student_id)
        homework = await self.homework_status(student_id)
        exam_prep = await self.exam_preparation(student_id)

        payload = {
            "progress": progress,
            "attendance": attendance,
            "pending_homework_count": len([h for h in homework if not h.get("submitted_at")]),
            "exam_preparation": exam_prep.content if exam_prep else None,
        }

        messages = prompts.parent_ai_summary_messages(payload)
        completion = await self.ai.complete(messages, temperature=0.5)

        return {
            "data": payload,
            "ai_summary": completion.content,
        }

    async def get_parent_profile_id(self, user_id: UUID) -> Optional[UUID]:
        query = select(ParentProfile.id).where(ParentProfile.user_id == user_id, ParentProfile.deleted_at.is_(None))
        row = (await self.db.execute(query)).first()
        return row[0] if row else None
