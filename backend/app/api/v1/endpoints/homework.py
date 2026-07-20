from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, get_own_student_profile_id, resolve_target_student_id
from app.models.user import UserRole, User
from app.repositories.academic import EnrollmentRepository
from app.repositories.tracking import HomeworkRepository, AssignmentSubmissionRepository
from app.repositories.communication import NotificationRepository
from app.schemas.tracking import (
    HomeworkCreate, HomeworkUpdate, HomeworkOut,
    SubmissionCreate, SubmissionGrade, SubmissionOut,
)

router = APIRouter()

teacher_roles = RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
student_role = RoleChecker([UserRole.STUDENT])


async def _notify_class_students(db: AsyncSession, class_id: UUID, title: str, message: str, type_: str):
    enrollments = await EnrollmentRepository(db).get_by_class(class_id)
    if not enrollments:
        return
    from app.models.profiles import StudentProfile
    from sqlalchemy import select
    student_ids = [e.student_id for e in enrollments]
    result = await db.execute(select(StudentProfile.user_id).where(StudentProfile.id.in_(student_ids)))
    user_ids = [row[0] for row in result.all()]
    if user_ids:
        await NotificationRepository(db).notify_many(user_ids, title, message, type_)


@router.post("", response_model=HomeworkOut, status_code=status.HTTP_201_CREATED)
async def create_homework(
    payload: HomeworkCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    homework = await HomeworkRepository(db).create(payload.model_dump())
    await _notify_class_students(
        db, payload.class_id, "New Homework Assigned",
        f"New homework '{payload.title}' has been assigned.", "academic",
    )
    return homework


@router.get("/class/{class_id}", response_model=List[HomeworkOut])
async def list_homework_by_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    return await HomeworkRepository(db).get_by_class(class_id)


@router.get("/me", response_model=List[HomeworkOut])
async def my_homework(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(student_role),
):
    student_id = await get_own_student_profile_id(db, user)
    if not student_id:
        raise HTTPException(status_code=404, detail="No student profile found for this account")
    class_ids = [e.class_id for e in await EnrollmentRepository(db).get_by_student(student_id)]
    return await HomeworkRepository(db).get_by_classes(class_ids)


@router.get("/student", response_model=List[HomeworkOut])
async def homework_for_student(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Same resolution as /me, but generalized so Parents (and staff) can pass
    student_id explicitly. Ownership is enforced by resolve_target_student_id."""
    target_id = await resolve_target_student_id(student_id, db, user)
    class_ids = [e.class_id for e in await EnrollmentRepository(db).get_by_student(target_id)]
    return await HomeworkRepository(db).get_by_classes(class_ids)


@router.patch("/{homework_id}", response_model=HomeworkOut)
async def update_homework(
    homework_id: UUID,
    payload: HomeworkUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    obj = await HomeworkRepository(db).update(homework_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="Homework not found")
    return obj


@router.delete("/{homework_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_homework(
    homework_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    await HomeworkRepository(db).delete(homework_id)


# ---------------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------------
@router.post("/submissions", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_homework(
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(student_role),
):
    own_id = await get_own_student_profile_id(db, user)
    if own_id != payload.student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students may only submit their own work")
    repo = AssignmentSubmissionRepository(db)
    existing = await repo.get_existing(payload.homework_id, payload.student_id)
    if existing:
        existing.content = payload.content
        await db.commit()
        await db.refresh(existing)
        return existing
    return await repo.create(payload.model_dump())


@router.get("/submissions/homework/{homework_id}", response_model=List[SubmissionOut])
async def submissions_for_homework(
    homework_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    return await AssignmentSubmissionRepository(db).get_by_homework(homework_id)


@router.get("/submissions/me", response_model=List[SubmissionOut])
async def my_submissions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(student_role),
):
    student_id = await get_own_student_profile_id(db, user)
    if not student_id:
        raise HTTPException(status_code=404, detail="No student profile found for this account")
    return await AssignmentSubmissionRepository(db).get_by_student(student_id)


@router.get("/submissions/student", response_model=List[SubmissionOut])
async def submissions_for_student(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Parent/staff-generalized version of /submissions/me."""
    target_id = await resolve_target_student_id(student_id, db, user)
    return await AssignmentSubmissionRepository(db).get_by_student(target_id)


@router.patch("/submissions/{submission_id}/grade", response_model=SubmissionOut)
async def grade_submission(
    submission_id: UUID,
    payload: SubmissionGrade,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    obj = await AssignmentSubmissionRepository(db).update(submission_id, {"grade": payload.grade})
    if not obj:
        raise HTTPException(status_code=404, detail="Submission not found")
    from app.models.profiles import StudentProfile
    from sqlalchemy import select
    result = await db.execute(select(StudentProfile.user_id).where(StudentProfile.id == obj.student_id))
    row = result.first()
    if row:
        await NotificationRepository(db).notify(
            row[0], "Homework Graded", "Your homework submission has been graded.", "academic",
        )
    return obj
