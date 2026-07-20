from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.teacher_ai_service import TeacherAIService
from app.schemas.mentor import AISummaryResponse

router = APIRouter()

teacher_roles = RoleChecker([UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


@router.get("/ai-summary", response_model=AISummaryResponse)
async def teacher_ai_summary(class_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(teacher_roles)):
    return await TeacherAIService(db).ai_summary(class_id)
