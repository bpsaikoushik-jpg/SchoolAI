from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.school import School
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile, TeacherProfile
from app.models.academic import Class, Subject, Enrollment
from app.models.tracking import Attendance, Homework, AssignmentSubmission, Exam, Result
from app.repositories.academic import ClassRepository, EnrollmentRepository
from app.repositories.tracking import HomeworkRepository, ExamRepository


class PrincipalService:
    """Backs the Principal Portal's school-scoped management and
    monitoring pages: student/teacher roster management plus school-wide
    attendance, homework, and exam/results overviews. Reuses the same
    models/repositories already relied on by the academic, attendance,
    homework, exams, and principal-analytics modules."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -----------------------------------------------------------------
    # School
    # -----------------------------------------------------------------
    async def get_school(self, school_id: UUID) -> School:
        school = (await self.db.execute(select(School).where(School.id == school_id))).scalars().first()
        if not school:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
        return school

    # -----------------------------------------------------------------
    # Students
    # -----------------------------------------------------------------
    async def list_students(
        self, school_id: UUID, search: Optional[str] = None, class_id: Optional[UUID] = None,
        skip: int = 0, limit: int = 100,
    ) -> List[dict]:
        query = (
            select(User, StudentProfile)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .where(User.school_id == school_id, User.role == UserRole.STUDENT, User.deleted_at.is_(None))
        )
        if search:
            like = f"%{search.lower()}%"
            query = query.where(func.lower(User.full_name).like(like) | func.lower(User.email).like(like))
        query = query.order_by(User.full_name).offset(skip).limit(limit)
        rows = (await self.db.execute(query)).all()

        student_ids = [sp.id for _, sp in rows]
        enrollments = {}
        if student_ids:
            enroll_rows = (await self.db.execute(
                select(Enrollment).where(Enrollment.student_id.in_(student_ids), Enrollment.deleted_at.is_(None))
            )).scalars().all()
            for e in enroll_rows:
                enrollments.setdefault(e.student_id, e)

        class_ids = [e.class_id for e in enrollments.values()]
        classes = {}
        if class_ids:
            class_rows = (await self.db.execute(
                select(Class).where(Class.id.in_(class_ids))
            )).scalars().all()
            classes = {c.id: c for c in class_rows}

        results = []
        for user, sp in rows:
            enrollment = enrollments.get(sp.id)
            klass = classes.get(enrollment.class_id) if enrollment else None
            if class_id and (not enrollment or enrollment.class_id != class_id):
                continue
            results.append({
                "user_id": user.id,
                "student_id": sp.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "student_id_number": sp.student_id_number,
                "grade_level": sp.grade_level,
                "class_id": klass.id if klass else None,
                "class_name": klass.name if klass else None,
            })
        return results

    async def create_student(self, school_id: UUID, payload) -> dict:
        existing = (await self.db.execute(select(User).where(User.email == payload.email))).scalars().first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists")

        user = User(
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            full_name=payload.full_name,
            role=UserRole.STUDENT,
            school_id=school_id,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        profile = StudentProfile(
            user_id=user.id,
            student_id_number=payload.student_id_number,
            grade_level=payload.grade_level,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        class_name = None
        if payload.class_id:
            klass = (await self.db.execute(select(Class).where(Class.id == payload.class_id))).scalars().first()
            if klass:
                self.db.add(Enrollment(student_id=profile.id, class_id=klass.id))
                await self.db.commit()
                class_name = klass.name

        return {
            "user_id": user.id,
            "student_id": profile.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "student_id_number": profile.student_id_number,
            "grade_level": profile.grade_level,
            "class_id": payload.class_id,
            "class_name": class_name,
        }

    async def update_student(self, school_id: UUID, user_id: UUID, payload) -> dict:
        user = await self._get_school_user(school_id, user_id, UserRole.STUDENT)
        profile = (await self.db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))).scalars().first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

        data = payload.model_dump(exclude_unset=True)
        if "full_name" in data:
            user.full_name = data["full_name"]
        if "is_active" in data:
            user.is_active = data["is_active"]
        if "student_id_number" in data:
            profile.student_id_number = data["student_id_number"]
        if "grade_level" in data:
            profile.grade_level = data["grade_level"]
        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(profile)

        enrollment = (await self.db.execute(
            select(Enrollment).where(Enrollment.student_id == profile.id, Enrollment.deleted_at.is_(None))
        )).scalars().first()
        klass = None
        if enrollment:
            klass = (await self.db.execute(select(Class).where(Class.id == enrollment.class_id))).scalars().first()

        return {
            "user_id": user.id,
            "student_id": profile.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "student_id_number": profile.student_id_number,
            "grade_level": profile.grade_level,
            "class_id": klass.id if klass else None,
            "class_name": klass.name if klass else None,
        }

    async def deactivate_student(self, school_id: UUID, user_id: UUID) -> None:
        user = await self._get_school_user(school_id, user_id, UserRole.STUDENT)
        user.is_active = False
        await self.db.commit()

    # -----------------------------------------------------------------
    # Teachers
    # -----------------------------------------------------------------
    async def list_teachers(
        self, school_id: UUID, search: Optional[str] = None, skip: int = 0, limit: int = 100,
    ) -> List[dict]:
        query = (
            select(User, TeacherProfile)
            .join(TeacherProfile, TeacherProfile.user_id == User.id)
            .where(User.school_id == school_id, User.role == UserRole.TEACHER, User.deleted_at.is_(None))
        )
        if search:
            like = f"%{search.lower()}%"
            query = query.where(func.lower(User.full_name).like(like) | func.lower(User.email).like(like))
        query = query.order_by(User.full_name).offset(skip).limit(limit)
        rows = (await self.db.execute(query)).all()

        teacher_ids = [tp.id for _, tp in rows]
        subject_counts = {}
        if teacher_ids:
            count_rows = (await self.db.execute(
                select(Subject.teacher_id, func.count(Subject.id))
                .where(Subject.teacher_id.in_(teacher_ids), Subject.deleted_at.is_(None))
                .group_by(Subject.teacher_id)
            )).all()
            subject_counts = {tid: count for tid, count in count_rows}

        return [
            {
                "user_id": user.id,
                "teacher_id": tp.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "employee_id": tp.employee_id,
                "specialization": tp.specialization,
                "subjects_count": subject_counts.get(tp.id, 0),
            }
            for user, tp in rows
        ]

    async def create_teacher(self, school_id: UUID, payload) -> dict:
        existing = (await self.db.execute(select(User).where(User.email == payload.email))).scalars().first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists")

        user = User(
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            full_name=payload.full_name,
            role=UserRole.TEACHER,
            school_id=school_id,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        profile = TeacherProfile(
            user_id=user.id,
            employee_id=payload.employee_id,
            specialization=payload.specialization,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        return {
            "user_id": user.id,
            "teacher_id": profile.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "employee_id": profile.employee_id,
            "specialization": profile.specialization,
            "subjects_count": 0,
        }

    async def update_teacher(self, school_id: UUID, user_id: UUID, payload) -> dict:
        user = await self._get_school_user(school_id, user_id, UserRole.TEACHER)
        profile = (await self.db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user.id))).scalars().first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher profile not found")

        data = payload.model_dump(exclude_unset=True)
        if "full_name" in data:
            user.full_name = data["full_name"]
        if "is_active" in data:
            user.is_active = data["is_active"]
        if "employee_id" in data:
            profile.employee_id = data["employee_id"]
        if "specialization" in data:
            profile.specialization = data["specialization"]
        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(profile)

        subjects_count = (await self.db.execute(
            select(func.count(Subject.id)).where(Subject.teacher_id == profile.id, Subject.deleted_at.is_(None))
        )).scalar() or 0

        return {
            "user_id": user.id,
            "teacher_id": profile.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "employee_id": profile.employee_id,
            "specialization": profile.specialization,
            "subjects_count": subjects_count,
        }

    async def deactivate_teacher(self, school_id: UUID, user_id: UUID) -> None:
        user = await self._get_school_user(school_id, user_id, UserRole.TEACHER)
        user.is_active = False
        await self.db.commit()

    async def _get_school_user(self, school_id: UUID, user_id: UUID, role: UserRole) -> User:
        user = (await self.db.execute(
            select(User).where(User.id == user_id, User.school_id == school_id, User.role == role, User.deleted_at.is_(None))
        )).scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{role.value.capitalize()} not found in this school")
        return user

    # -----------------------------------------------------------------
    # Attendance monitoring
    # -----------------------------------------------------------------
    async def attendance_overview(self, school_id: UUID, on_date: Optional[date] = None) -> dict:
        target_date = on_date or datetime.now(timezone.utc).date()
        classes = await ClassRepository(self.db).get_by_school(school_id)

        by_class: List[dict] = []
        present = absent = late = 0
        for klass in classes:
            enrollments = await EnrollmentRepository(self.db).get_by_class(klass.id)
            student_ids = [e.student_id for e in enrollments]
            c_present = c_absent = c_late = 0
            if student_ids:
                rows = (await self.db.execute(
                    select(Attendance.status).where(
                        Attendance.student_id.in_(student_ids), Attendance.deleted_at.is_(None)
                    )
                )).all()
                for (status_val,) in rows:
                    if status_val == "present":
                        c_present += 1
                    elif status_val == "absent":
                        c_absent += 1
                    elif status_val == "late":
                        c_late += 1
            present += c_present
            absent += c_absent
            late += c_late
            by_class.append({
                "class_id": klass.id,
                "class_name": klass.name,
                "present": c_present,
                "absent": c_absent,
                "late": c_late,
                "total_marked": c_present + c_absent + c_late,
            })

        return {
            "date": target_date,
            "present": present,
            "absent": absent,
            "late": late,
            "total_marked": present + absent + late,
            "by_class": by_class,
        }

    # -----------------------------------------------------------------
    # Homework monitoring
    # -----------------------------------------------------------------
    async def homework_overview(self, school_id: UUID) -> List[dict]:
        classes = await ClassRepository(self.db).get_by_school(school_id)
        class_ids = [c.id for c in classes]
        class_names = {c.id: c.name for c in classes}
        homeworks = await HomeworkRepository(self.db).get_by_classes(class_ids)

        items: List[dict] = []
        for hw in homeworks:
            enrollments = await EnrollmentRepository(self.db).get_by_class(hw.class_id)
            total_students = len(enrollments)
            submitted = (await self.db.execute(
                select(func.count(AssignmentSubmission.id)).where(
                    AssignmentSubmission.homework_id == hw.id, AssignmentSubmission.deleted_at.is_(None)
                )
            )).scalar() or 0
            items.append({
                "id": hw.id,
                "title": hw.title,
                "class_id": hw.class_id,
                "class_name": class_names.get(hw.class_id, "Unknown class"),
                "due_date": hw.due_date,
                "submitted": submitted,
                "total_students": total_students,
                "completion_rate": round(submitted / total_students * 100, 1) if total_students else None,
            })
        return items

    # -----------------------------------------------------------------
    # Exam / results monitoring
    # -----------------------------------------------------------------
    async def exams_overview(self, school_id: UUID) -> List[dict]:
        classes = await ClassRepository(self.db).get_by_school(school_id)
        class_names = {c.id: c.name for c in classes}

        # Subjects aren't always directly tied to a class in this schema, so
        # scope the same way PrincipalAnalyticsService.subject_performance
        # does: via the assigned teacher's school (falling back to any
        # class-linked subjects within this school too).
        class_ids = list(class_names.keys())
        scope_condition = (User.school_id == school_id)
        if class_ids:
            scope_condition = scope_condition | Subject.class_id.in_(class_ids)

        subject_rows = (await self.db.execute(
            select(Subject)
            .join(TeacherProfile, Subject.teacher_id == TeacherProfile.id, isouter=True)
            .join(User, TeacherProfile.user_id == User.id, isouter=True)
            .where(Subject.deleted_at.is_(None), scope_condition)
        )).scalars().unique().all()

        subjects = subject_rows
        subject_names = {s.id: s.name for s in subjects}
        subject_class = {s.id: s.class_id for s in subjects}
        subject_ids = [s.id for s in subjects]

        exams = await ExamRepository(self.db).get_by_subjects(subject_ids)

        items: List[dict] = []
        for exam in exams:
            rows = (await self.db.execute(
                select(Result.score).where(Result.exam_id == exam.id, Result.deleted_at.is_(None))
            )).all()
            scores = [s for (s,) in rows if s is not None]
            class_id = subject_class.get(exam.subject_id)
            items.append({
                "id": exam.id,
                "title": exam.title,
                "subject_id": exam.subject_id,
                "subject_name": subject_names.get(exam.subject_id, "Unknown subject"),
                "class_id": class_id,
                "class_name": class_names.get(class_id) if class_id else None,
                "date": exam.date,
                "results_recorded": len(scores),
                "average_score": round(sum(scores) / len(scores), 2) if scores else None,
            })
        items.sort(key=lambda i: i["date"] or datetime.min.replace(tzinfo=None), reverse=True)
        return items
