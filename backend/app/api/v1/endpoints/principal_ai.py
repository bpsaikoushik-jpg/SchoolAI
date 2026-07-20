from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.principal_ai_service import PrincipalAIService
from app.schemas.mentor import AISummaryResponse

router = APIRouter()

principal_roles = RoleChecker([UserRole.PRINCIPAL, UserRole.ADMIN, UserRole.FOUNDER])


@router.get("/analytics", response_model=AISummaryResponse)
async def principal_analytics(school_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(principal_roles)):
    return await PrincipalAIService(db).full_analytics(school_id)
