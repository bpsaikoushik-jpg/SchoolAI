from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.school import School
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile
from app.models.tracking import Result
from app.services.principal_analytics_service import PrincipalAnalyticsService
from app.services.principal_service import PrincipalService


class FounderAnalyticsService:
    """Organization-wide analytics for the Founder Portal. Reuses
    PrincipalAnalyticsService / PrincipalService per-school and aggregates
    the results across every active school, rather than reimplementing
    school-scoped queries that already exist for the Principal Portal."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.principal_analytics = PrincipalAnalyticsService(db)
        self.principal_service = PrincipalService(db)

    async def _active_schools(self) -> List[School]:
        return (await self.db.execute(
            select(School).where(School.deleted_at.is_(None)).order_by(School.name)
        )).scalars().all()

    # -----------------------------------------------------------------
    # Organization overview
    # -----------------------------------------------------------------
    async def org_overview(self) -> dict:
        total_schools = (await self.db.execute(select(func.count(School.id)))).scalar() or 0
        active_schools = (await self.db.execute(
            select(func.count(School.id)).where(School.deleted_at.is_(None))
        )).scalar() or 0

        async def count_role(role: UserRole) -> int:
            return (await self.db.execute(
                select(func.count(User.id)).where(User.role == role, User.deleted_at.is_(None))
            )).scalar() or 0

        total_students = await count_role(UserRole.STUDENT)
        total_teachers = await count_role(UserRole.TEACHER)
        total_parents = await count_role(UserRole.PARENT)
        principals = await count_role(UserRole.PRINCIPAL)
        admins = await count_role(UserRole.ADMIN)

        avg_score_val = (await self.db.execute(
            select(func.avg(Result.score)).where(Result.deleted_at.is_(None))
        )).scalar()

        return {
            "total_schools": total_schools,
            "active_schools": active_schools,
            "inactive_schools": total_schools - active_schools,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_parents": total_parents,
            "total_staff": principals + admins,
            "average_score": round(float(avg_score_val), 2) if avg_score_val is not None else None,
        }

    async def role_breakdown(self) -> List[dict]:
        rows = (await self.db.execute(
            select(User.role, func.count(User.id)).where(User.deleted_at.is_(None)).group_by(User.role)
        )).all()
        return [{"role": role.value, "count": count} for role, count in rows]

    # -----------------------------------------------------------------
    # Multi-school performance comparison
    # -----------------------------------------------------------------
    async def school_performance(self) -> List[dict]:
        schools = await self._active_schools()
        results = []
        for school in schools:
            perf = await self.principal_analytics.school_performance(school.id)
            results.append({
                "school_id": perf["school_id"],
                "school_name": perf["school_name"],
                "is_active": True,
                "average_score": perf["average_score"],
                "total_students": perf["total_students"],
                "total_teachers": perf["total_teachers"],
                "total_classes": perf["total_classes"],
            })
        return results

    # -----------------------------------------------------------------
    # Org-wide attendance
    # -----------------------------------------------------------------
    async def attendance_overview(self, on_date: Optional[date] = None) -> dict:
        schools = await self._active_schools()
        target_date = on_date or datetime.now(timezone.utc).date()

        by_school: List[dict] = []
        present = absent = late = 0
        for school in schools:
            overview = await self.principal_service.attendance_overview(school.id, on_date)
            by_school.append({
                "school_id": school.id,
                "school_name": school.name,
                "present": overview["present"],
                "absent": overview["absent"],
                "late": overview["late"],
                "total_marked": overview["total_marked"],
            })
            present += overview["present"]
            absent += overview["absent"]
            late += overview["late"]

        return {
            "date": target_date,
            "present": present,
            "absent": absent,
            "late": late,
            "total_marked": present + absent + late,
            "by_school": by_school,
        }

    # -----------------------------------------------------------------
    # Org-wide homework
    # -----------------------------------------------------------------
    async def homework_overview(self) -> List[dict]:
        schools = await self._active_schools()
        results = []
        for school in schools:
            items = await self.principal_service.homework_overview(school.id)
            total_assigned = len(items)
            total_submitted = sum(i["submitted"] for i in items)
            total_students_covered = sum(i["total_students"] for i in items)
            completion_rate = (
                round(total_submitted / total_students_covered * 100, 1) if total_students_covered else None
            )
            results.append({
                "school_id": school.id,
                "school_name": school.name,
                "total_assigned": total_assigned,
                "total_submitted": total_submitted,
                "total_students_covered": total_students_covered,
                "completion_rate": completion_rate,
            })
        return results

    # -----------------------------------------------------------------
    # Org-wide exams / results (one shape backs both analytics pages)
    # -----------------------------------------------------------------
    async def exam_overview(self) -> List[dict]:
        schools = await self._active_schools()
        results = []
        for school in schools:
            items = await self.principal_service.exams_overview(school.id)
            graded = [i for i in items if i["average_score"] is not None]
            avg_score = round(sum(i["average_score"] for i in graded) / len(graded), 2) if graded else None
            results.append({
                "school_id": school.id,
                "school_name": school.name,
                "total_exams": len(items),
                "results_recorded": sum(i["results_recorded"] for i in items),
                "average_score": avg_score,
            })
        return results

    # -----------------------------------------------------------------
    # Org-wide student / teacher analytics
    # -----------------------------------------------------------------
    async def student_analytics(self) -> dict:
        schools = await self._active_schools()
        by_school = []
        for school in schools:
            perf = await self.principal_analytics.school_performance(school.id)
            by_school.append({
                "school_id": school.id,
                "school_name": school.name,
                "student_count": perf["total_students"],
                "average_score": perf["average_score"],
            })

        grade_rows = (await self.db.execute(
            select(StudentProfile.grade_level, func.count(StudentProfile.id))
            .join(User, StudentProfile.user_id == User.id)
            .where(User.deleted_at.is_(None), User.role == UserRole.STUDENT)
            .group_by(StudentProfile.grade_level)
        )).all()
        by_grade = [{"grade_level": g, "count": c} for g, c in grade_rows]
        by_grade.sort(key=lambda r: (r["grade_level"] is None, r["grade_level"] or 0))

        return {"by_school": by_school, "by_grade": by_grade}

    async def teacher_analytics(self) -> dict:
        schools = await self._active_schools()
        by_school = []
        top_teachers: List[dict] = []
        for school in schools:
            perf = await self.principal_analytics.school_performance(school.id)
            by_school.append({
                "school_id": school.id,
                "school_name": school.name,
                "teacher_count": perf["total_teachers"],
            })

            teachers = await self.principal_analytics.teacher_performance(school.id)
            for t in teachers:
                top_teachers.append({
                    "teacher_id": t["teacher_id"],
                    "full_name": t["full_name"],
                    "school_name": school.name,
                    "subjects_taught": t["subjects_taught"],
                    "average_student_score": t["average_student_score"],
                })

        top_teachers = [t for t in top_teachers if t["average_student_score"] is not None]
        top_teachers.sort(key=lambda t: t["average_student_score"], reverse=True)

        return {"by_school": by_school, "top_teachers": top_teachers[:10]}
