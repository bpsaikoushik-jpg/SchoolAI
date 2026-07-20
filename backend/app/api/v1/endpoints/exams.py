from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, get_own_student_profile_id, resolve_target_student_id
from app.models.user import UserRole, User
from app.repositories.tracking import ExamRepository, ResultRepository
from app.repositories.academic import EnrollmentRepository, SubjectRepository
from app.repositories.communication import NotificationRepository
from app.schemas.tracking import (
    ExamCreate, ExamUpdate, ExamOut,
    ResultCreate, ResultUpdate, ResultOut, ResultDetailOut,
)

router = APIRouter()

teacher_roles = RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


async def _resolve_upcoming_exams(db: AsyncSession, student_id: UUID) -> List:
    enrollments = await EnrollmentRepository(db).get_by_student(student_id)
    class_ids = [e.class_id for e in enrollments]
    subjects = await SubjectRepository(db).get_by_classes(class_ids)
    subject_ids = [s.id for s in subjects]
    exams = await ExamRepository(db).get_by_subjects(subject_ids)
    now = datetime.now(timezone.utc)
    upcoming = [e for e in exams if e.date is not None and e.date.replace(tzinfo=timezone.utc) >= now]
    upcoming.sort(key=lambda e: e.date)
    return upcoming


@router.get("/me/upcoming", response_model=List[ExamOut])
async def my_upcoming_exams(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker([UserRole.STUDENT])),
):
    """Resolves upcoming exams for the current student via their class
    enrollments -> subjects -> exams, filtered to today or later."""
    student_id = await get_own_student_profile_id(db, user)
    if not student_id:
        raise HTTPException(status_code=404, detail="No student profile found for this account")
    return await _resolve_upcoming_exams(db, student_id)


@router.get("/student/upcoming", response_model=List[ExamOut])
async def upcoming_exams_for_student(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Parent/staff-generalized version of /me/upcoming."""
    target_id = await resolve_target_student_id(student_id, db, user)
    return await _resolve_upcoming_exams(db, target_id)


@router.post("", response_model=ExamOut, status_code=status.HTTP_201_CREATED)
async def create_exam(
    payload: ExamCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    return await ExamRepository(db).create(payload.model_dump())


@router.get("/subject/{subject_id}", response_model=List[ExamOut])
async def list_exams_by_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    return await ExamRepository(db).get_by_subject(subject_id)


@router.patch("/{exam_id}", response_model=ExamOut)
async def update_exam(
    exam_id: UUID,
    payload: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    obj = await ExamRepository(db).update(exam_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="Exam not found")
    return obj


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    await ExamRepository(db).delete(exam_id)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
@router.post("/results", response_model=ResultOut, status_code=status.HTTP_201_CREATED)
async def record_result(
    payload: ResultCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    repo = ResultRepository(db)
    existing = await repo.get_existing(payload.exam_id, payload.student_id)
    if existing:
        existing.score = payload.score
        existing.remarks = payload.remarks
        await db.commit()
        await db.refresh(existing)
        result = existing
    else:
        result = await repo.create(payload.model_dump())

    from app.models.profiles import StudentProfile
    from sqlalchemy import select
    row = (await db.execute(select(StudentProfile.user_id).where(StudentProfile.id == payload.student_id))).first()
    if row:
        await NotificationRepository(db).notify(
            row[0], "Exam Result Published", "A new exam result has been published.", "academic",
        )
    return result


@router.get("/results/student", response_model=List[ResultOut])
async def student_results(
    student_id: UUID = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    target_id = await resolve_target_student_id(student_id, db, user)
    return await ResultRepository(db).get_by_student(target_id)


@router.get("/results/student/detailed", response_model=List[ResultDetailOut])
async def student_results_detailed(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Same data as /results/student, enriched with exam title/date and
    subject name so the Parent Portal can render Results/Performance
    without a separate round trip per exam."""
    target_id = await resolve_target_student_id(student_id, db, user)
    results = await ResultRepository(db).get_by_student(target_id)
    if not results:
        return []

    exam_ids = list({r.exam_id for r in results})
    exams = {e.id: e for e in await ExamRepository(db).get_by_ids(exam_ids)}
    subject_ids = list({e.subject_id for e in exams.values()})
    subjects = {s.id: s for s in await SubjectRepository(db).get_by_ids(subject_ids)}

    detailed: List[ResultDetailOut] = []
    for r in results:
        exam = exams.get(r.exam_id)
        if not exam:
            continue
        subject = subjects.get(exam.subject_id)
        detailed.append(
            ResultDetailOut(
                id=r.id,
                exam_id=r.exam_id,
                student_id=r.student_id,
                score=r.score,
                remarks=r.remarks,
                exam_title=exam.title,
                exam_date=exam.date,
                subject_id=exam.subject_id,
                subject_name=subject.name if subject else "Unknown subject",
                created_at=r.created_at,
            )
        )
    detailed.sort(key=lambda d: d.exam_date or d.created_at, reverse=True)
    return detailed


@router.get("/results/exam/{exam_id}", response_model=List[ResultOut])
async def results_for_exam(
    exam_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    return await ResultRepository(db).get_by_exam(exam_id)


@router.patch("/results/{result_id}", response_model=ResultOut)
async def update_result(
    result_id: UUID,
    payload: ResultUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(teacher_roles),
):
    obj = await ResultRepository(db).update(result_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="Result not found")
    return obj
