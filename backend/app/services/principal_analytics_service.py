from uuid import UUID
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.school import School
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile, TeacherProfile
from app.models.academic import Class, Subject, Enrollment
from app.models.tracking import Result, Exam
from app.models.memory import ConversationMemory, QuizAttempt


class PrincipalAnalyticsService:
    """School-wide analytics for principals/admins."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def school_performance(self, school_id: UUID):
        school = (await self.db.execute(select(School).where(School.id == school_id))).scalars().first()

        student_count = (await self.db.execute(
            select(func.count(User.id)).where(User.school_id == school_id, User.role == UserRole.STUDENT, User.deleted_at.is_(None))
        )).scalar() or 0
        teacher_count = (await self.db.execute(
            select(func.count(User.id)).where(User.school_id == school_id, User.role == UserRole.TEACHER, User.deleted_at.is_(None))
        )).scalar() or 0
        class_count = (await self.db.execute(
            select(func.count(Class.id)).where(Class.school_id == school_id, Class.deleted_at.is_(None))
        )).scalar() or 0

        student_ids = await self._school_student_profile_ids(school_id)
        average_score = await self._avg_score(student_ids)

        return {
            "school_id": school_id,
            "school_name": school.name if school else "",
            "average_score": average_score,
            "total_students": student_count,
            "total_teachers": teacher_count,
            "total_classes": class_count,
        }

    async def _school_student_profile_ids(self, school_id: UUID) -> List[UUID]:
        query = (
            select(StudentProfile.id)
            .join(User, StudentProfile.user_id == User.id)
            .where(User.school_id == school_id, User.deleted_at.is_(None))
        )
        return [row[0] for row in (await self.db.execute(query)).all()]

    async def _avg_score(self, student_ids: List[UUID]):
        if not student_ids:
            return None
        query = select(func.avg(Result.score)).where(Result.student_id.in_(student_ids), Result.deleted_at.is_(None))
        val = (await self.db.execute(query)).scalar()
        return round(float(val), 2) if val is not None else None

    async def class_performance(self, school_id: UUID):
        classes = (await self.db.execute(
            select(Class).where(Class.school_id == school_id, Class.deleted_at.is_(None))
        )).scalars().all()

        summaries = []
        for c in classes:
            student_ids = [row[0] for row in (await self.db.execute(
                select(Enrollment.student_id).where(Enrollment.class_id == c.id, Enrollment.deleted_at.is_(None))
            )).all()]
            avg_score = await self._avg_score(student_ids)
            summaries.append({
                "class_id": c.id,
                "class_name": c.name,
                "student_count": len(student_ids),
                "average_score": avg_score,
                "homework_completion_rate": None,
                "attendance_rate": None,
            })
        return summaries

    async def subject_performance(self, school_id: UUID):
        # Subjects aren't directly tied to a school in the current schema; scope via
        # teachers belonging to the school.
        query = (
            select(Subject)
            .join(TeacherProfile, Subject.teacher_id == TeacherProfile.id, isouter=True)
            .join(User, TeacherProfile.user_id == User.id, isouter=True)
            .where((User.school_id == school_id) | (Subject.teacher_id.is_(None)))
        )
        subjects = (await self.db.execute(query)).scalars().all()

        results = []
        for subject in subjects:
            exam_ids = [row[0] for row in (await self.db.execute(
                select(Exam.id).where(Exam.subject_id == subject.id, Exam.deleted_at.is_(None))
            )).all()]
            avg_score = None
            if exam_ids:
                val = (await self.db.execute(
                    select(func.avg(Result.score)).where(Result.exam_id.in_(exam_ids), Result.deleted_at.is_(None))
                )).scalar()
                avg_score = round(float(val), 2) if val is not None else None
            results.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "average_score": avg_score,
                "total_exams": len(exam_ids),
            })
        return results

    async def teacher_performance(self, school_id: UUID):
        query = (
            select(TeacherProfile, User)
            .join(User, TeacherProfile.user_id == User.id)
            .where(User.school_id == school_id, User.deleted_at.is_(None))
        )
        rows = (await self.db.execute(query)).all()

        results = []
        for teacher_profile, user in rows:
            subjects = (await self.db.execute(
                select(Subject).where(Subject.teacher_id == teacher_profile.id, Subject.deleted_at.is_(None))
            )).scalars().all()

            scores = []
            for subject in subjects:
                exam_ids = [row[0] for row in (await self.db.execute(
                    select(Exam.id).where(Exam.subject_id == subject.id, Exam.deleted_at.is_(None))
                )).all()]
                if exam_ids:
                    val = (await self.db.execute(
                        select(func.avg(Result.score)).where(Result.exam_id.in_(exam_ids), Result.deleted_at.is_(None))
                    )).scalar()
                    if val is not None:
                        scores.append(float(val))

            results.append({
                "teacher_id": teacher_profile.id,
                "full_name": user.full_name,
                "subjects_taught": [s.name for s in subjects],
                "average_student_score": round(sum(scores) / len(scores), 2) if scores else None,
            })
        return results

    async def ai_usage_stats(self, school_id: UUID):
        student_ids = await self._school_student_profile_ids(school_id)
        if not student_ids:
            return {
                "total_conversations": 0,
                "total_quiz_attempts": 0,
                "active_students": 0,
                "average_conversations_per_student": 0.0,
            }

        convo_query = select(ConversationMemory.student_id, func.count(ConversationMemory.id)).where(
            ConversationMemory.student_id.in_(student_ids), ConversationMemory.deleted_at.is_(None)
        ).group_by(ConversationMemory.student_id)
        convo_rows = (await self.db.execute(convo_query)).all()
        total_conversations = sum(count for _, count in convo_rows)
        active_students = len(convo_rows)

        quiz_query = select(func.count(QuizAttempt.id)).where(
            QuizAttempt.student_id.in_(student_ids), QuizAttempt.deleted_at.is_(None)
        )
        total_quiz_attempts = (await self.db.execute(quiz_query)).scalar() or 0

        avg_per_student = round(total_conversations / len(student_ids), 2) if student_ids else 0.0

        return {
            "total_conversations": total_conversations,
            "total_quiz_attempts": total_quiz_attempts,
            "active_students": active_students,
            "average_conversations_per_student": avg_per_student,
        }
