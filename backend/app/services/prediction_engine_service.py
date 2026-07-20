"""Prediction Engine.

IMPORTANT (be transparent about this in the API docs / UI, not just here):
there is no trained ML model or historical-snapshot warehouse in this
codebase. Every "prediction" below is a statistically-grounded estimate
computed from trend extrapolation and rule-based scoring over the same
tracking/memory data the rest of the AI Intelligence Engine uses - not the
output of a trained predictive model. Each result includes a `confidence`
field ("low"/"medium"/"high") driven by how much data backed the estimate,
and a `basis` string explaining how it was derived, so callers never
mistake a rough heuristic for a certainty.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tracking import Result, Exam, Attendance, Homework, AssignmentSubmission
from app.models.academic import Enrollment, Class, Subject
from app.models.memory import QuizAttempt, ConversationMemory
from app.models.profiles import StudentProfile, TeacherProfile
from app.models.school import School
from app.models.user import User, UserRole


def _confidence(n: int, low: int = 3, high: int = 10) -> str:
    if n >= high:
        return "high"
    if n >= low:
        return "medium"
    return "low"


def _linear_trend(values: List[float]) -> float:
    """Simple slope of a sequence via least squares; positive = improving."""
    n = len(values)
    if n < 2:
        return 0.0
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    return cov / var_x if var_x else 0.0


class PredictionEngineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -- student-level ----------------------------------------------------
    async def _quiz_scores(self, student_id: UUID) -> List[float]:
        query = (
            select(QuizAttempt.score)
            .where(QuizAttempt.student_id == student_id, QuizAttempt.deleted_at.is_(None))
            .order_by(QuizAttempt.created_at)
        )
        return [row[0] for row in (await self.db.execute(query)).all()]

    async def _exam_scores(self, student_id: UUID) -> List[float]:
        query = (
            select(Result.score)
            .where(Result.student_id == student_id, Result.deleted_at.is_(None), Result.score.is_not(None))
            .order_by(Result.created_at)
        )
        return [row[0] for row in (await self.db.execute(query)).all()]

    async def predict_exam_score(self, student_id: UUID, subject_id: Optional[UUID] = None) -> dict:
        exam_scores = await self._exam_scores(student_id)
        quiz_scores = await self._quiz_scores(student_id)
        combined = exam_scores + quiz_scores
        if not combined:
            return {"predicted_score": None, "confidence": "low", "basis": "No exam or quiz history available yet."}

        recent = combined[-8:]
        avg = sum(recent) / len(recent)
        slope = _linear_trend(recent)
        predicted = max(0.0, min(100.0, avg + slope * 2))
        return {
            "predicted_score": round(predicted, 1),
            "confidence": _confidence(len(combined)),
            "basis": f"Weighted average + trend across the last {len(recent)} exam/quiz results (avg={round(avg, 1)}, trend/attempt={round(slope, 2)}).",
        }

    async def predict_attendance_risk(self, student_id: UUID) -> dict:
        query = select(Attendance.status).where(Attendance.student_id == student_id, Attendance.deleted_at.is_(None))
        rows = [row[0] for row in (await self.db.execute(query)).all()]
        if not rows:
            return {"risk_level": "unknown", "confidence": "low", "basis": "No attendance records yet."}

        present = sum(1 for s in rows if s == "present")
        rate = present / len(rows)
        if rate >= 0.9:
            risk = "low"
        elif rate >= 0.75:
            risk = "medium"
        else:
            risk = "high"
        return {
            "risk_level": risk,
            "attendance_rate": round(rate * 100, 1),
            "confidence": _confidence(len(rows)),
            "basis": f"Attendance rate over {len(rows)} recorded days.",
        }

    async def predict_homework_completion(self, student_id: UUID) -> dict:
        enroll_query = select(Enrollment.class_id).where(Enrollment.student_id == student_id, Enrollment.deleted_at.is_(None))
        class_ids = [row[0] for row in (await self.db.execute(enroll_query)).all()]
        if not class_ids:
            return {"predicted_completion_rate": None, "confidence": "low", "basis": "Student isn't enrolled in any class."}

        hw_query = select(func.count(Homework.id)).where(Homework.class_id.in_(class_ids), Homework.deleted_at.is_(None))
        total_homework = (await self.db.execute(hw_query)).scalar() or 0

        sub_query = select(func.count(AssignmentSubmission.id)).where(
            AssignmentSubmission.student_id == student_id, AssignmentSubmission.deleted_at.is_(None)
        )
        submitted = (await self.db.execute(sub_query)).scalar() or 0

        if total_homework == 0:
            return {"predicted_completion_rate": None, "confidence": "low", "basis": "No homework assigned yet."}

        rate = min(1.0, submitted / total_homework)
        return {
            "predicted_completion_rate": round(rate * 100, 1),
            "confidence": _confidence(total_homework),
            "basis": f"{submitted}/{total_homework} homework items submitted historically, projected forward.",
        }

    async def predict_performance_trend(self, student_id: UUID) -> dict:
        combined = (await self._exam_scores(student_id)) + (await self._quiz_scores(student_id))
        if len(combined) < 2:
            return {"trend": "insufficient_data", "confidence": "low", "basis": "Fewer than 2 scored assessments."}
        slope = _linear_trend(combined[-10:])
        if slope >= 2:
            trend = "improving"
        elif slope <= -2:
            trend = "declining"
        else:
            trend = "stable"
        return {"trend": trend, "slope_per_attempt": round(slope, 2), "confidence": _confidence(len(combined)), "basis": f"Trend across last {min(len(combined), 10)} scored attempts."}

    async def predict_failure_risk(self, student_id: UUID) -> dict:
        exam_prediction = await self.predict_exam_score(student_id)
        attendance = await self.predict_attendance_risk(student_id)

        score = exam_prediction.get("predicted_score")
        risk_points = 0
        reasons = []
        if score is not None and score < 40:
            risk_points += 2
            reasons.append(f"predicted score {score} is below passing range")
        elif score is not None and score < 55:
            risk_points += 1
            reasons.append(f"predicted score {score} is borderline")
        if attendance.get("risk_level") == "high":
            risk_points += 2
            reasons.append("attendance risk is high")
        elif attendance.get("risk_level") == "medium":
            risk_points += 1
            reasons.append("attendance risk is medium")

        risk_level = "high" if risk_points >= 3 else "medium" if risk_points >= 1 else "low"
        return {
            "risk_level": risk_level,
            "confidence": "low" if (score is None or attendance.get("confidence") == "low") else "medium",
            "basis": "; ".join(reasons) or "No strong risk signals detected in available data.",
        }

    async def predict_dropout_risk(self, student_id: UUID) -> dict:
        failure_risk = await self.predict_failure_risk(student_id)
        since = datetime.now(timezone.utc) - timedelta(days=30)
        convo_query = select(func.count(ConversationMemory.id)).where(
            ConversationMemory.student_id == student_id, ConversationMemory.created_at >= since, ConversationMemory.deleted_at.is_(None)
        )
        engagement = (await self.db.execute(convo_query)).scalar() or 0

        risk_points = {"low": 0, "medium": 1, "high": 2}[failure_risk["risk_level"]]
        if engagement == 0:
            risk_points += 1
            engagement_note = "no AI Mentor engagement in the last 30 days"
        else:
            engagement_note = f"{engagement} AI Mentor interactions in the last 30 days"

        risk_level = "high" if risk_points >= 3 else "medium" if risk_points >= 1 else "low"
        return {
            "risk_level": risk_level,
            "confidence": "low",
            "basis": f"Derived from academic failure risk ({failure_risk['risk_level']}) and engagement signal ({engagement_note}). "
                     f"Treat as an early-warning heuristic, not a certainty.",
        }

    async def predict_subject_improvement(self, student_id: UUID, subject_id: UUID) -> dict:
        query = (
            select(QuizAttempt.score)
            .where(QuizAttempt.student_id == student_id, QuizAttempt.subject_id == subject_id, QuizAttempt.deleted_at.is_(None))
            .order_by(QuizAttempt.created_at)
        )
        scores = [row[0] for row in (await self.db.execute(query)).all()]
        if len(scores) < 2:
            return {"trend": "insufficient_data", "confidence": "low", "basis": "Fewer than 2 quiz attempts in this subject."}
        slope = _linear_trend(scores)
        return {
            "trend": "improving" if slope > 1 else "declining" if slope < -1 else "stable",
            "slope_per_attempt": round(slope, 2),
            "confidence": _confidence(len(scores)),
            "basis": f"Trend across {len(scores)} quiz attempts in this subject.",
        }

    async def predict_learning_growth(self, student_id: UUID) -> dict:
        scores = await self._quiz_scores(student_id)
        if len(scores) < 3:
            return {"growth_rate": None, "confidence": "low", "basis": "Fewer than 3 quiz attempts on record."}
        first_third = scores[: max(1, len(scores) // 3)]
        last_third = scores[-max(1, len(scores) // 3):]
        growth = (sum(last_third) / len(last_third)) - (sum(first_third) / len(first_third))
        return {
            "growth_rate": round(growth, 1),
            "confidence": _confidence(len(scores)),
            "basis": f"Change in average score between earliest and most recent attempts (n={len(scores)}).",
        }

    async def predict_class_rank_trend(self, class_id: UUID, student_id: UUID) -> dict:
        student_ids_query = select(Enrollment.student_id).where(Enrollment.class_id == class_id, Enrollment.deleted_at.is_(None))
        student_ids = [row[0] for row in (await self.db.execute(student_ids_query)).all()]
        if student_id not in student_ids or len(student_ids) < 2:
            return {"rank": None, "class_size": len(student_ids), "confidence": "low", "basis": "Not enough classmates with data to rank."}

        avg_query = select(Result.student_id, func.avg(Result.score)).where(
            Result.student_id.in_(student_ids), Result.deleted_at.is_(None)
        ).group_by(Result.student_id)
        averages = {row[0]: float(row[1]) for row in (await self.db.execute(avg_query)).all() if row[1] is not None}

        if student_id not in averages:
            return {"rank": None, "class_size": len(student_ids), "confidence": "low", "basis": "Student has no scored results yet."}

        ranked = sorted(averages.items(), key=lambda kv: -kv[1])
        rank = next(i for i, (sid, _) in enumerate(ranked, start=1) if sid == student_id)
        return {
            "rank": rank,
            "class_size": len(student_ids),
            "percentile": round((1 - (rank - 1) / max(1, len(ranked) - 1)) * 100, 1) if len(ranked) > 1 else 100.0,
            "confidence": _confidence(len(averages)),
            "basis": f"Ranked by average exam score among {len(averages)} classmates with results.",
        }

    # -- teacher / school level --------------------------------------------
    async def predict_teacher_effectiveness(self, teacher_id: UUID) -> dict:
        subjects = (await self.db.execute(
            select(Subject).where(Subject.teacher_id == teacher_id, Subject.deleted_at.is_(None))
        )).scalars().all()
        if not subjects:
            return {"effectiveness_score": None, "confidence": "low", "basis": "Teacher has no assigned subjects."}

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

        if not scores:
            return {"effectiveness_score": None, "confidence": "low", "basis": "No exam results yet for this teacher's subjects."}

        avg = sum(scores) / len(scores)
        return {
            "effectiveness_score": round(avg, 1),
            "confidence": _confidence(len(scores)),
            "basis": f"Average student exam score across {len(scores)} subject(s) taught, used as a proxy for effectiveness.",
        }

    async def predict_school_performance(self, school_id: UUID) -> dict:
        student_ids_query = (
            select(StudentProfile.id)
            .join(User, StudentProfile.user_id == User.id)
            .where(User.school_id == school_id, User.deleted_at.is_(None))
        )
        student_ids = [row[0] for row in (await self.db.execute(student_ids_query)).all()]
        if not student_ids:
            return {"predicted_average_score": None, "confidence": "low", "basis": "No students found for this school."}

        query = select(Result.score).where(Result.student_id.in_(student_ids), Result.deleted_at.is_(None), Result.score.is_not(None)).order_by(Result.created_at)
        scores = [row[0] for row in (await self.db.execute(query)).all()]
        if not scores:
            return {"predicted_average_score": None, "confidence": "low", "basis": "No exam results recorded for this school yet."}

        recent = scores[-30:]
        avg = sum(recent) / len(recent)
        slope = _linear_trend(recent)
        predicted = max(0.0, min(100.0, avg + slope))
        return {
            "predicted_average_score": round(predicted, 1),
            "confidence": _confidence(len(scores), low=10, high=50),
            "basis": f"Average + trend across the {len(recent)} most recent results school-wide. "
                     f"No historical per-term snapshots exist, so this reflects only current data, not seasonal effects.",
        }

    # -- bundle -------------------------------------------------------------
    async def student_prediction_bundle(self, student_id: UUID) -> dict:
        return {
            "exam_score": await self.predict_exam_score(student_id),
            "attendance_risk": await self.predict_attendance_risk(student_id),
            "homework_completion": await self.predict_homework_completion(student_id),
            "performance_trend": await self.predict_performance_trend(student_id),
            "failure_risk": await self.predict_failure_risk(student_id),
            "dropout_risk": await self.predict_dropout_risk(student_id),
            "learning_growth": await self.predict_learning_growth(student_id),
        }
