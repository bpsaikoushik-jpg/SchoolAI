from uuid import UUID
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.memory import RecommendationRepository, LearningProfileRepository, WeaknessProfileRepository
from app.models.tracking import Homework, AssignmentSubmission, Exam
from app.models.academic import Enrollment, Subject
from app.models.profiles import StudentProfile


class RecommendationEngineService:
    """Turns the Weakness Engine + Learning Profile output into concrete,
    persisted study plans and recommendations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.recommendations = RecommendationRepository(db)
        self.learning_profiles = LearningProfileRepository(db)
        self.weakness_profiles = WeaknessProfileRepository(db)

    async def _context(self, student_id: UUID):
        profile = await self.learning_profiles.get_or_create(student_id)
        weakness = await self.weakness_profiles.get_or_create(student_id)
        return profile, weakness

    async def save_recommendation(self, student_id: UUID, type: str, title: str, content: dict, priority: str = "medium", due_date=None):
        """Public entry point (used by AI Mentor) for persisting a
        recommendation that isn't one of the built-in generators below,
        e.g. an AI-narrated version of a plan."""
        return await self._save(student_id, type, title, content, priority, due_date)

    async def _save(self, student_id: UUID, type: str, title: str, content: dict, priority: str = "medium", due_date=None):
        return await self.recommendations.create({
            "student_id": student_id,
            "type": type,
            "title": title,
            "content": content,
            "priority": priority,
            "due_date": due_date,
            "subject": content.get("primary_subject"),
        })

    async def generate_daily_plan(self, student_id: UUID):
        profile, weakness = await self._context(student_id)

        tasks = []
        for concept in (weakness.weak_concepts or [])[:3]:
            tasks.append({
                "type": "concept_review",
                "topic": concept.get("topic"),
                "reason": f"Average score {concept.get('avg_score')}% - below target",
                "suggested_minutes": 20,
            })
        for topic in (weakness.forgotten_topics or [])[:2]:
            tasks.append({
                "type": "quick_revision",
                "topic": topic.get("topic"),
                "reason": f"Not revisited in {topic.get('last_seen_days_ago')} days",
                "suggested_minutes": 10,
            })
        if not tasks:
            tasks.append({
                "type": "general_practice",
                "topic": "any subject",
                "reason": "No weaknesses detected - keep practicing to stay sharp",
                "suggested_minutes": 20,
            })

        content = {
            "explanation_style": profile.preferred_explanation_style,
            "difficulty_level": profile.difficulty_level,
            "tasks": tasks,
        }
        return await self._save(student_id, "daily_plan", "Today's Study Plan", content, priority="high")

    async def generate_weekly_plan(self, student_id: UUID):
        profile, weakness = await self._context(student_id)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        focus_topics = [c["topic"] for c in (weakness.weak_concepts or [])] or ["general revision"]
        schedule = {}
        for i, day in enumerate(days):
            topic = focus_topics[i % len(focus_topics)]
            schedule[day] = {
                "topic": topic,
                "suggested_minutes": 30 if day != "Sunday" else 15,
                "activity": "practice_questions" if i % 2 == 0 else "concept_review",
            }

        content = {
            "difficulty_level": profile.difficulty_level,
            "revision_frequency": profile.revision_frequency,
            "schedule": schedule,
        }
        return await self._save(student_id, "weekly_plan", "This Week's Study Plan", content, priority="high")

    async def generate_revision_plan(self, student_id: UUID):
        profile, weakness = await self._context(student_id)

        items = [
            {
                "topic": t.get("topic"),
                "last_seen_days_ago": t.get("last_seen_days_ago"),
                "priority": "high" if t.get("last_seen_days_ago", 0) >= 21 else "medium",
            }
            for t in (weakness.forgotten_topics or [])
        ]
        content = {
            "revision_frequency": profile.revision_frequency,
            "recommendation": profile.revision_recommendation,
            "items": items,
        }
        return await self._save(student_id, "revision_plan", "Revision Plan", content, priority="medium")

    async def recommend_practice_questions(self, student_id: UUID):
        profile, weakness = await self._context(student_id)

        recs = []
        for concept in (weakness.weak_concepts or []):
            recs.append({
                "topic": concept.get("topic"),
                "difficulty": profile.difficulty_level,
                "question_count": 10,
            })
        for mistake in (weakness.frequent_mistakes or []):
            recs.append({
                "topic": mistake.get("topic"),
                "difficulty": "easy",
                "question_count": 5,
                "reason": f"Repeated {mistake.get('mistake_type')} mistakes",
            })
        if not recs:
            recs.append({"topic": "mixed review", "difficulty": profile.difficulty_level, "question_count": 10})

        content = {"recommendations": recs}
        return await self._save(student_id, "practice_questions", "Recommended Practice Questions", content)

    async def recommend_homework(self, student_id: UUID):
        # Find homework assigned to the student's class(es) not yet submitted.
        enroll_query = select(Enrollment.class_id).where(Enrollment.student_id == student_id, Enrollment.deleted_at.is_(None))
        class_ids = [row[0] for row in (await self.db.execute(enroll_query)).all()]

        pending = []
        if class_ids:
            hw_query = select(Homework).where(Homework.class_id.in_(class_ids), Homework.deleted_at.is_(None))
            all_hw = (await self.db.execute(hw_query)).scalars().all()

            sub_query = select(AssignmentSubmission.homework_id).where(
                AssignmentSubmission.student_id == student_id, AssignmentSubmission.deleted_at.is_(None)
            )
            submitted_ids = {row[0] for row in (await self.db.execute(sub_query)).all()}

            pending = [
                {"homework_id": str(hw.id), "title": hw.title, "due_date": hw.due_date.isoformat() if hw.due_date else None}
                for hw in all_hw if hw.id not in submitted_ids
            ]

        content = {"pending_homework": pending}
        priority = "high" if pending else "low"
        return await self._save(student_id, "homework", "Homework Recommendations", content, priority=priority)

    async def generate_exam_prep_plan(self, student_id: UUID, days_ahead: int = 30):
        profile, weakness = await self._context(student_id)

        enroll_query = select(Enrollment.class_id).where(Enrollment.student_id == student_id, Enrollment.deleted_at.is_(None))
        class_ids = [row[0] for row in (await self.db.execute(enroll_query)).all()]

        upcoming_exams = []
        if class_ids:
            now = datetime.now(timezone.utc)
            window = now + timedelta(days=days_ahead)
            exam_query = select(Exam, Subject).join(Subject, Exam.subject_id == Subject.id).where(
                Exam.deleted_at.is_(None)
            )
            rows = (await self.db.execute(exam_query)).all()
            for exam, subject in rows:
                if exam.date and now.replace(tzinfo=None) <= exam.date <= window.replace(tzinfo=None):
                    upcoming_exams.append({
                        "exam_id": str(exam.id),
                        "subject": subject.name,
                        "date": exam.date.isoformat(),
                        "days_remaining": (exam.date - now.replace(tzinfo=None)).days,
                    })

        weak_topics = [c["topic"] for c in (weakness.weak_concepts or [])]
        content = {
            "upcoming_exams": upcoming_exams,
            "priority_topics": weak_topics,
            "recommended_daily_minutes": 45 if profile.knowledge_level == "beginner" else 30,
        }
        return await self._save(student_id, "exam_prep", "Exam Preparation Plan", content, priority="high")
