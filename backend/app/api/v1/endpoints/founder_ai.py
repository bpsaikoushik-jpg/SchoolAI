from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import RoleChecker
from app.models.user import UserRole, User
from app.services.founder_ai_service import FounderAIService
from app.schemas.mentor import AISummaryResponse

router = APIRouter()

founder_roles = RoleChecker([UserRole.FOUNDER, UserRole.ADMIN])


@router.get("/analytics", response_model=AISummaryResponse)
async def founder_analytics(db: AsyncSession = Depends(get_db), user: User = Depends(founder_roles)):
    return await FounderAIService(db).full_analytics()
