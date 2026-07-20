from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, get_own_student_profile_id, resolve_target_student_id
from app.models.user import UserRole, User
from app.repositories.academic import ClassRepository, SubjectRepository, EnrollmentRepository
from app.schemas.academic import (
    ClassCreate, ClassUpdate, ClassOut,
    SubjectCreate, SubjectUpdate, SubjectOut,
    EnrollmentCreate, EnrollmentOut,
    TeacherContactOut,
)

router = APIRouter()

manage_roles = RoleChecker([UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
all_roles = RoleChecker([UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------
@router.post("/classes", response_model=ClassOut, status_code=status.HTTP_201_CREATED)
async def create_class(
    payload: ClassCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await ClassRepository(db).create(payload.model_dump())


@router.get("/classes/school/{school_id}", response_model=List[ClassOut])
async def list_classes_by_school(
    school_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    return await ClassRepository(db).get_by_school(school_id)


@router.get("/classes/{class_id}", response_model=ClassOut)
async def get_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    obj = await ClassRepository(db).get(class_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return obj


@router.patch("/classes/{class_id}", response_model=ClassOut)
async def update_class(
    class_id: UUID,
    payload: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    obj = await ClassRepository(db).update(class_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return obj


@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    await ClassRepository(db).delete(class_id)


# ---------------------------------------------------------------------------
# Subjects
# ---------------------------------------------------------------------------
@router.post("/subjects", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
async def create_subject(
    payload: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    return await SubjectRepository(db).create(payload.model_dump())


@router.get("/subjects/teacher/{teacher_id}", response_model=List[SubjectOut])
async def list_subjects_by_teacher(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    return await SubjectRepository(db).get_by_teacher(teacher_id)


@router.get("/subjects/class/{class_id}", response_model=List[SubjectOut])
async def list_subjects_by_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    return await SubjectRepository(db).get_by_class(class_id)


@router.get("/subjects/me", response_model=List[SubjectOut])
async def my_subjects(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker([UserRole.STUDENT])),
):
    """Resolves the current student's subjects via their class enrollments."""
    student_id = await get_own_student_profile_id(db, user)
    if not student_id:
        raise HTTPException(status_code=404, detail="No student profile found for this account")
    enrollments = await EnrollmentRepository(db).get_by_student(student_id)
    class_ids = [e.class_id for e in enrollments]
    return await SubjectRepository(db).get_by_classes(class_ids)


@router.get("/subjects/student", response_model=List[SubjectOut])
async def subjects_for_student(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Parent/staff-generalized version of /subjects/me. Ownership is
    enforced by resolve_target_student_id (parents may only pass a
    student_id that is linked to their own account)."""
    target_id = await resolve_target_student_id(student_id, db, user)
    enrollments = await EnrollmentRepository(db).get_by_student(target_id)
    class_ids = [e.class_id for e in enrollments]
    return await SubjectRepository(db).get_by_classes(class_ids)


@router.get("/subjects/{subject_id}", response_model=SubjectOut)
async def get_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    obj = await SubjectRepository(db).get(subject_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Subject not found")
    return obj


@router.patch("/subjects/{subject_id}", response_model=SubjectOut)
async def update_subject(
    subject_id: UUID,
    payload: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    obj = await SubjectRepository(db).update(subject_id, payload.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="Subject not found")
    return obj


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    await SubjectRepository(db).delete(subject_id)


# ---------------------------------------------------------------------------
# Enrollments
# ---------------------------------------------------------------------------
@router.post("/enrollments", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    repo = EnrollmentRepository(db)
    existing = await repo.get_existing(payload.student_id, payload.class_id)
    if existing:
        return existing
    return await repo.create(payload.model_dump())


@router.get("/enrollments/me", response_model=List[EnrollmentOut])
async def my_enrollments(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker([UserRole.STUDENT])),
):
    student_id = await get_own_student_profile_id(db, user)
    if not student_id:
        raise HTTPException(status_code=404, detail="No student profile found for this account")
    return await EnrollmentRepository(db).get_by_student(student_id)


@router.get("/enrollments/student", response_model=List[EnrollmentOut])
async def enrollments_for_student(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Parent/staff-generalized version of /enrollments/me."""
    target_id = await resolve_target_student_id(student_id, db, user)
    return await EnrollmentRepository(db).get_by_student(target_id)


@router.get("/teachers/student", response_model=List[TeacherContactOut])
async def teacher_directory_for_student(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(all_roles),
):
    """Read-only teacher directory for a student's current subjects.
    Powers the Parent Portal's Communication page."""
    from sqlalchemy import select
    from app.models.profiles import TeacherProfile
    from app.models.user import User as UserModel

    target_id = await resolve_target_student_id(student_id, db, user)
    enrollments = await EnrollmentRepository(db).get_by_student(target_id)
    class_ids = [e.class_id for e in enrollments]
    subjects = await SubjectRepository(db).get_by_classes(class_ids)

    contacts: List[TeacherContactOut] = []
    for subject in subjects:
        teacher_name = None
        specialization = None
        if subject.teacher_id is not None:
            row = (
                await db.execute(
                    select(UserModel.full_name, TeacherProfile.specialization)
                    .join(TeacherProfile, TeacherProfile.user_id == UserModel.id)
                    .where(TeacherProfile.id == subject.teacher_id)
                )
            ).first()
            if row:
                teacher_name, specialization = row
        contacts.append(
            TeacherContactOut(
                subject_id=subject.id,
                subject_name=subject.name,
                teacher_id=subject.teacher_id,
                teacher_name=teacher_name,
                specialization=specialization,
            )
        )
    return contacts


@router.get("/enrollments/class/{class_id}", response_model=List[EnrollmentOut])
async def enrollments_by_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])),
):
    return await EnrollmentRepository(db).get_by_class(class_id)


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(manage_roles),
):
    await EnrollmentRepository(db).delete(enrollment_id)
