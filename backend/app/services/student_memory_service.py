from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta, date as date_cls

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.memory import (
    StudentMemoryRepository,
    ConversationMemoryRepository,
    QuizAttemptRepository,
    MistakeLogRepository,
    FrequentDoubtRepository,
    DailyProgressRepository,
    WeeklyProgressRepository,
    MonthlyProgressRepository,
)
from app.models.tracking import Homework, AssignmentSubmission
from app.schemas.memory import (
    StudentMemoryCreate,
    ConversationMemoryCreate,
    QuizAttemptCreate,
    MistakeLogCreate,
    DailyProgressCreate,
)


class StudentMemoryService:
    """
    Owns raw capture of everything the AI Memory Engine remembers about a
    student: free-form facts, conversation turns, quiz attempts, mistakes,
    frequently asked doubts, and daily/weekly/monthly progress rollups.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.memories = StudentMemoryRepository(db)
        self.conversations = ConversationMemoryRepository(db)
        self.quiz_attempts = QuizAttemptRepository(db)
        self.mistakes = MistakeLogRepository(db)
        self.doubts = FrequentDoubtRepository(db)
        self.daily_progress = DailyProgressRepository(db)
        self.weekly_progress = WeeklyProgressRepository(db)
        self.monthly_progress = MonthlyProgressRepository(db)

    # -- free-form facts -----------------------------------------------
    async def remember(self, data: StudentMemoryCreate):
        return await self.memories.create(data.model_dump())

    async def get_memories(self, student_id: UUID, category: Optional[str] = None):
        return await self.memories.get_by_student(student_id, category)

    # -- conversation memory --------------------------------------------
    async def log_conversation(self, data: ConversationMemoryCreate):
        convo = await self.conversations.create(data.model_dump())
        # Every question is a candidate "doubt" - track recurrence.
        await self.doubts.upsert_doubt(
            student_id=data.student_id,
            subject=None,
            topic=data.topic,
            question_text=data.question,
        )
        return convo

    async def get_conversations(self, student_id: UUID, limit: int = 50):
        return await self.conversations.get_by_student(student_id, limit)

    async def get_doubts(self, student_id: UUID):
        return await self.doubts.get_by_student(student_id)

    # -- quiz history ------------------------------------------------------
    async def log_quiz_attempt(self, data: QuizAttemptCreate):
        payload = data.model_dump()
        total = payload["total_questions"] or 1
        correct = payload["correct_answers"]
        payload["score"] = round((correct / total) * 100, 2)
        return await self.quiz_attempts.create(payload)

    async def get_quiz_history(self, student_id: UUID, limit: int = 100):
        return await self.quiz_attempts.get_by_student(student_id, limit)

    # -- homework history (reuses existing tracking models) ----------------
    async def get_homework_history(self, student_id: UUID) -> List[dict]:
        query = (
            select(AssignmentSubmission, Homework)
            .join(Homework, AssignmentSubmission.homework_id == Homework.id)
            .where(AssignmentSubmission.student_id == student_id, AssignmentSubmission.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        rows = result.all()
        return [
            {
                "homework_id": str(hw.id),
                "title": hw.title,
                "due_date": hw.due_date,
                "submitted_at": sub.created_at,
                "grade": sub.grade,
            }
            for sub, hw in rows
        ]

    # -- mistakes ------------------------------------------------------
    async def log_mistake(self, data: MistakeLogCreate):
        similar = await self.mistakes.find_similar(data.student_id, data.topic, data.mistake_type)
        if similar:
            similar.repeat_count += 1
            similar.question = data.question or similar.question
            similar.student_answer = data.student_answer or similar.student_answer
            similar.correct_answer = data.correct_answer or similar.correct_answer
            similar.is_resolved = False
            await self.db.commit()
            await self.db.refresh(similar)
            return similar
        return await self.mistakes.create(data.model_dump())

    async def get_mistakes(self, student_id: UUID, unresolved_only: bool = False):
        return await self.mistakes.get_by_student(student_id, unresolved_only)

    async def resolve_mistake(self, mistake_id: UUID):
        return await self.mistakes.update(mistake_id, {"is_resolved": True})

    # -- progress: daily -------------------------------------------------
    async def record_daily_progress(self, data: DailyProgressCreate):
        payload = data.model_dump()
        student_id = payload.pop("student_id")
        date = payload.pop("date")
        return await self.daily_progress.upsert(student_id, date, **payload)

    async def get_daily_progress(self, student_id: UUID, limit: int = 30):
        return await self.daily_progress.get_by_student(student_id, limit)

    # -- progress: weekly rollup (computed from daily progress + quizzes) --
    async def aggregate_weekly_progress(self, student_id: UUID, week_start_date: Optional[str] = None):
        if week_start_date is None:
            today = date_cls.today()
            monday = today - timedelta(days=today.weekday())
            week_start_date = monday.isoformat()

        start = datetime.fromisoformat(week_start_date)
        end = start + timedelta(days=7)

        daily_entries = await self.daily_progress.get_by_student(student_id, limit=400)
        week_entries = [
            d for d in daily_entries
            if start.date() <= date_cls.fromisoformat(d.date) < end.date()
        ]

        hours_studied = sum(d.hours_studied or 0 for d in week_entries)
        topics = sorted({t for d in week_entries for t in (d.topics_covered or [])})
        subjects_summary: dict = {}
        for d in week_entries:
            for subj, minutes in (d.subjects_summary or {}).items():
                subjects_summary[subj] = subjects_summary.get(subj, 0) + minutes

        quiz_scores = [q.score for q in await self.quiz_attempts.get_since(student_id, start)]
        average_score = round(sum(quiz_scores) / len(quiz_scores), 2) if quiz_scores else None

        return await self.weekly_progress.upsert(
            student_id,
            week_start_date,
            hours_studied=hours_studied,
            topics_covered=topics,
            subjects_summary=subjects_summary,
            average_score=average_score,
        )

    async def get_weekly_progress(self, student_id: UUID, limit: int = 12):
        return await self.weekly_progress.get_by_student(student_id, limit)

    # -- progress: monthly rollup ------------------------------------------
    async def aggregate_monthly_progress(self, student_id: UUID, month: Optional[int] = None, year: Optional[int] = None):
        today = date_cls.today()
        month = month or today.month
        year = year or today.year

        daily_entries = await self.daily_progress.get_by_student(student_id, limit=400)
        month_entries = [
            d for d in daily_entries
            if date_cls.fromisoformat(d.date).month == month and date_cls.fromisoformat(d.date).year == year
        ]

        hours_studied = sum(d.hours_studied or 0 for d in month_entries)
        topics = sorted({t for d in month_entries for t in (d.topics_covered or [])})
        subjects_summary: dict = {}
        for d in month_entries:
            for subj, minutes in (d.subjects_summary or {}).items():
                subjects_summary[subj] = subjects_summary.get(subj, 0) + minutes

        start = datetime(year, month, 1)
        quiz_scores = [q.score for q in await self.quiz_attempts.get_since(student_id, start)]
        average_score = round(sum(quiz_scores) / len(quiz_scores), 2) if quiz_scores else None

        # Improvement trend vs previous month
        prev_month, prev_year = (month - 1, year) if month > 1 else (12, year - 1)
        prev = await self.monthly_progress.get_by_student_month(student_id, prev_month, prev_year)
        trend = "stable"
        if prev and prev.average_score is not None and average_score is not None:
            if average_score > prev.average_score + 3:
                trend = "improving"
            elif average_score < prev.average_score - 3:
                trend = "declining"

        return await self.monthly_progress.upsert(
            student_id,
            month,
            year,
            hours_studied=hours_studied,
            topics_covered=topics,
            subjects_summary=subjects_summary,
            average_score=average_score,
            improvement_trend=trend,
        )

    async def get_monthly_progress(self, student_id: UUID, limit: int = 12):
        return await self.monthly_progress.get_by_student(student_id, limit)

    # -- recent activity feed (aggregated from existing tracking tables) ---
    async def get_recent_activity(self, student_id: UUID, limit: int = 10) -> List[dict]:
        """Normalizes recent quiz attempts, homework submissions, and logged
        mistakes into a single reverse-chronological feed. No new tables -
        purely a read-side aggregation over data already being captured."""
        events: List[dict] = []

        for quiz in await self.quiz_attempts.get_by_student(student_id, limit=limit):
            events.append({
                "id": f"quiz-{quiz.id}",
                "type": "quiz",
                "text": f"Scored {quiz.score:.0f}% on \"{quiz.quiz_title}\"",
                "timestamp": quiz.created_at,
            })

        for submission, homework in await self._recent_submissions(student_id, limit):
            events.append({
                "id": f"submission-{submission.id}",
                "type": "homework",
                "text": f"Submitted \"{homework.title}\"" + (f" · graded {submission.grade}" if submission.grade else ""),
                "timestamp": submission.created_at,
            })

        for mistake in await self.mistakes.get_by_student(student_id, unresolved_only=False):
            if mistake.repeat_count and mistake.repeat_count > 0:
                events.append({
                    "id": f"mistake-{mistake.id}",
                    "type": "mistake",
                    "text": f"Logged a {mistake.mistake_type or 'practice'} mistake in {mistake.topic or mistake.subject or 'a topic'}",
                    "timestamp": mistake.updated_at or mistake.created_at,
                })

        events.sort(key=lambda e: e["timestamp"] or datetime.min, reverse=True)
        return events[:limit]

    async def _recent_submissions(self, student_id: UUID, limit: int):
        query = (
            select(AssignmentSubmission, Homework)
            .join(Homework, AssignmentSubmission.homework_id == Homework.id)
            .where(AssignmentSubmission.student_id == student_id, AssignmentSubmission.deleted_at.is_(None))
            .order_by(AssignmentSubmission.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.all()
