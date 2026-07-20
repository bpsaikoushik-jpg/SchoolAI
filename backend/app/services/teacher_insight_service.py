from uuid import UUID
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import Enrollment, Class, Subject
from app.models.tracking import Result, Exam, Attendance, Homework, AssignmentSubmission
from app.models.profiles import StudentProfile
from app.models.user import User
from app.models.memory import QuizAttempt, LearningProfile, WeaknessProfile


class TeacherInsightService:
    """Class-level analytics for teachers, built purely from existing
    tracking/academic data plus the memory engine's learning/weakness profiles."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _class_student_ids(self, class_id: UUID) -> List[UUID]:
        query = select(Enrollment.student_id).where(Enrollment.class_id == class_id, Enrollment.deleted_at.is_(None))
        return [row[0] for row in (await self.db.execute(query)).all()]

    async def _avg_score_for_students(self, student_ids: List[UUID]) -> dict:
        if not student_ids:
            return {}
        query = select(Result.student_id, func.avg(Result.score)).where(
            Result.student_id.in_(student_ids), Result.deleted_at.is_(None)
        ).group_by(Result.student_id)
        return {row[0]: float(row[1]) for row in (await self.db.execute(query)).all() if row[1] is not None}

    async def weak_students(self, class_id: UUID, threshold: float = 60.0):
        student_ids = await self._class_student_ids(class_id)
        scores = await self._avg_score_for_students(student_ids)
        weak_ids = [sid for sid, score in scores.items() if score < threshold]
        return await self._build_summaries(weak_ids, scores)

    async def strong_students(self, class_id: UUID, threshold: float = 80.0):
        student_ids = await self._class_student_ids(class_id)
        scores = await self._avg_score_for_students(student_ids)
        strong_ids = [sid for sid, score in scores.items() if score >= threshold]
        return await self._build_summaries(strong_ids, scores)

    async def _build_summaries(self, student_ids: List[UUID], scores: dict):
        summaries = []
        for sid in student_ids:
            sp_query = select(StudentProfile, User).join(User, StudentProfile.user_id == User.id).where(StudentProfile.id == sid)
            row = (await self.db.execute(sp_query)).first()
            full_name = row.User.full_name if row else None

            lp_query = select(LearningProfile).where(LearningProfile.student_id == sid, LearningProfile.deleted_at.is_(None))
            lp = (await self.db.execute(lp_query)).scalars().first()

            summaries.append({
                "student_id": sid,
                "full_name": full_name,
                "average_score": round(scores.get(sid, 0), 2),
                "confidence_score": lp.confidence_score if lp else None,
                "weak_subjects": lp.weak_subjects if lp else [],
                "strong_subjects": lp.strong_subjects if lp else [],
            })
        return summaries

    async def topic_wise_performance(self, subject_id: UUID):
        query = select(
            QuizAttempt.topic, func.avg(QuizAttempt.score), func.count(QuizAttempt.id)
        ).where(
            QuizAttempt.subject_id == subject_id,
            QuizAttempt.deleted_at.is_(None),
            QuizAttempt.topic.is_not(None),
        ).group_by(QuizAttempt.topic)
        rows = (await self.db.execute(query)).all()
        return [
            {"topic": topic, "average_score": round(float(avg), 2), "attempts": count}
            for topic, avg, count in rows if avg is not None
        ]

    async def class_summary(self, class_id: UUID):
        class_row = (await self.db.execute(select(Class).where(Class.id == class_id))).scalars().first()
        student_ids = await self._class_student_ids(class_id)
        scores = await self._avg_score_for_students(student_ids)
        average_score = round(sum(scores.values()) / len(scores), 2) if scores else None

        homework_stats = await self.homework_completion(class_id)
        attendance_rate = await self._attendance_rate(student_ids)

        return {
            "class_id": class_id,
            "class_name": class_row.name if class_row else "",
            "student_count": len(student_ids),
            "average_score": average_score,
            "homework_completion_rate": homework_stats["completion_rate"],
            "attendance_rate": attendance_rate,
        }

    async def homework_completion(self, class_id: UUID):
        hw_query = select(Homework).where(Homework.class_id == class_id, Homework.deleted_at.is_(None))
        homeworks = (await self.db.execute(hw_query)).scalars().all()
        student_ids = await self._class_student_ids(class_id)

        total_expected = len(homeworks) * len(student_ids)
        homework_ids = [hw.id for hw in homeworks]

        total_actual = 0
        if homework_ids and student_ids:
            sub_query = select(func.count(AssignmentSubmission.id)).where(
                AssignmentSubmission.homework_id.in_(homework_ids),
                AssignmentSubmission.student_id.in_(student_ids),
                AssignmentSubmission.deleted_at.is_(None),
            )
            total_actual = (await self.db.execute(sub_query)).scalar() or 0

        completion_rate = round((total_actual / total_expected) * 100, 2) if total_expected else 0.0

        return {
            "class_id": class_id,
            "total_homework": len(homeworks),
            "total_expected_submissions": total_expected,
            "total_actual_submissions": total_actual,
            "completion_rate": completion_rate,
        }

    async def attendance_rate(self, student_ids: List[UUID]):
        """Public wrapper (used by Parent AI) around the internal attendance-rate calculation."""
        return await self._attendance_rate(student_ids)

    async def _attendance_rate(self, student_ids: List[UUID]) -> Optional[float]:
        if not student_ids:
            return None
        query = select(Attendance.status, func.count(Attendance.id)).where(
            Attendance.student_id.in_(student_ids), Attendance.deleted_at.is_(None)
        ).group_by(Attendance.status)
        rows = (await self.db.execute(query)).all()
        total = sum(count for _, count in rows)
        present = sum(count for status, count in rows if status == "present")
        return round((present / total) * 100, 2) if total else None

    async def attendance_correlation(self, class_id: UUID):
        student_ids = await self._class_student_ids(class_id)
        scores = await self._avg_score_for_students(student_ids)

        per_student_attendance = {}
        for sid in student_ids:
            rate = await self._attendance_rate([sid])
            if rate is not None:
                per_student_attendance[sid] = rate

        paired = [(per_student_attendance[sid], scores[sid]) for sid in student_ids if sid in per_student_attendance and sid in scores]

        coefficient = self._pearson(paired)
        if coefficient is None:
            interpretation = "Not enough data to determine a correlation."
        elif coefficient > 0.5:
            interpretation = "Strong positive correlation: better attendance tends to mean better scores."
        elif coefficient > 0.2:
            interpretation = "Mild positive correlation between attendance and scores."
        elif coefficient < -0.2:
            interpretation = "Negative correlation: higher attendance is associated with lower scores."
        else:
            interpretation = "No meaningful correlation detected."

        return {
            "class_id": class_id,
            "correlation_coefficient": coefficient,
            "sample_size": len(paired),
            "interpretation": interpretation,
        }

    async def my_classes(self, teacher_id: UUID):
        """One row per (subject, class) the teacher teaches, with live metrics -
        mirrors what the dashboard previously showed as mock 'TEACHER_CLASSES'."""
        subject_query = select(Subject).where(Subject.teacher_id == teacher_id, Subject.deleted_at.is_(None))
        subjects = (await self.db.execute(subject_query)).scalars().all()

        rows = []
        for subject in subjects:
            if subject.class_id is None:
                continue
            summary = await self.class_summary(subject.class_id)
            rows.append({
                "class_id": subject.class_id,
                "subject_id": subject.id,
                "name": f"{subject.name} — {summary['class_name']}",
                "students": summary["student_count"],
                "avg_score": summary["average_score"] or 0,
            })
        return rows

    async def my_class_ids(self, teacher_id: UUID) -> List[UUID]:
        subject_query = select(Subject.class_id).where(
            Subject.teacher_id == teacher_id, Subject.deleted_at.is_(None), Subject.class_id.is_not(None)
        )
        return list({row[0] for row in (await self.db.execute(subject_query)).all()})

    async def attendance_today(self, teacher_id: UUID):
        import datetime as _dt
        class_ids = await self.my_class_ids(teacher_id)
        student_ids: List[UUID] = []
        for cid in class_ids:
            student_ids.extend(await self._class_student_ids(cid))
        student_ids = list(set(student_ids))
        if not student_ids:
            return {"present": 0, "absent": 0, "late": 0}

        today = _dt.date.today()
        query = select(Attendance.status, func.count(Attendance.id)).where(
            Attendance.student_id.in_(student_ids),
            Attendance.deleted_at.is_(None),
            func.date(Attendance.date) == today,
        ).group_by(Attendance.status)
        rows = (await self.db.execute(query)).all()
        counts = {"present": 0, "absent": 0, "late": 0}
        for status_, count in rows:
            if status_ in counts:
                counts[status_] = count
        return counts

    async def homework_queue(self, teacher_id: UUID, limit: int = 10):
        class_ids = await self.my_class_ids(teacher_id)
        if not class_ids:
            return []

        hw_query = select(Homework, Class).join(Class, Homework.class_id == Class.id).where(
            Homework.class_id.in_(class_ids), Homework.deleted_at.is_(None)
        ).order_by(Homework.due_date.asc().nullslast())
        rows = (await self.db.execute(hw_query)).all()

        queue = []
        for hw, class_row in rows[:limit]:
            student_ids = await self._class_student_ids(hw.class_id)
            submitted = 0
            if student_ids:
                sub_query = select(func.count(AssignmentSubmission.id)).where(
                    AssignmentSubmission.homework_id == hw.id,
                    AssignmentSubmission.student_id.in_(student_ids),
                    AssignmentSubmission.deleted_at.is_(None),
                )
                submitted = (await self.db.execute(sub_query)).scalar() or 0
            queue.append({
                "id": hw.id,
                "title": hw.title,
                "class_name": class_row.name,
                "due_date": hw.due_date,
                "submitted": submitted,
                "total": len(student_ids),
            })
        return queue

    async def my_students(self, teacher_id: UUID):
        """Full roster across every class this teacher teaches, with current
        average score and attendance rate - backs the Students page (roster
        view), previously TEACHER_STUDENTS mock data."""
        class_ids = await self.my_class_ids(teacher_id)
        if not class_ids:
            return []

        class_rows = {c.id: c for c in (await self.db.execute(select(Class).where(Class.id.in_(class_ids)))).scalars().all()}

        rows = []
        seen: set = set()
        for class_id in class_ids:
            student_ids = await self._class_student_ids(class_id)
            scores = await self._avg_score_for_students(student_ids)
            for sid in student_ids:
                if sid in seen:
                    continue
                seen.add(sid)
                sp_query = select(StudentProfile, User).join(User, StudentProfile.user_id == User.id).where(StudentProfile.id == sid)
                row = (await self.db.execute(sp_query)).first()
                full_name = row.User.full_name if row else None
                attendance = await self._attendance_rate([sid])
                rows.append({
                    "student_id": sid,
                    "full_name": full_name,
                    "class_name": class_rows[class_id].name if class_id in class_rows else "",
                    "average_score": round(scores.get(sid, 0), 2),
                    "attendance_rate": attendance,
                })
        return rows

    @staticmethod
    def _pearson(pairs: List[tuple]):
        n = len(pairs)
        if n < 2:
            return None
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        cov = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
        var_x = sum((x - mean_x) ** 2 for x in xs)
        var_y = sum((y - mean_y) ** 2 for y in ys)
        denom = (var_x * var_y) ** 0.5
        if denom == 0:
            return None
        return round(cov / denom, 4)
