from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker, resolve_target_student_id, get_own_parent_profile_id
from app.models.user import UserRole, User
from app.services.parent_ai_service import ParentAIService
from app.schemas.mentor import AISummaryResponse, ChildSummary
from app.schemas.memory import ParentStudentLinkCreate, ParentStudentLinkOut
from app.repositories.family import ParentStudentLinkRepository

router = APIRouter()

parent_and_staff = RoleChecker([UserRole.PARENT, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])
staff_roles = RoleChecker([UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


@router.post("/links", response_model=ParentStudentLinkOut)
async def link_parent_to_student(payload: ParentStudentLinkCreate, db: AsyncSession = Depends(get_db), user: User = Depends(staff_roles)):
    """Staff-only: register that a parent is the guardian of a student.
    Needed once per parent/child pair before /parent/ai-summary works for them."""
    return await ParentStudentLinkRepository(db).link(payload.parent_id, payload.student_id, payload.relationship_type)


@router.get("/children", response_model=list[ChildSummary])
async def list_children(db: AsyncSession = Depends(get_db), user: User = Depends(RoleChecker([UserRole.PARENT]))):
    parent_id = await get_own_parent_profile_id(db, user)
    if parent_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No parent profile found for this account")
    return await ParentAIService(db).get_children(parent_id)


@router.get("/ai-summary", response_model=AISummaryResponse)
async def parent_ai_summary(
    student_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(parent_and_staff),
):
    target = await resolve_target_student_id(student_id, db, user)
    return await ParentAIService(db).full_summary(target)
