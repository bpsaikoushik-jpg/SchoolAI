from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email, self.model.deleted_at == None)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def email_exists(self, email: str) -> bool:
        query = select(self.model).where(self.model.email == email, self.model.deleted_at == None)
        result = await self.db.execute(query)
        return result.scalars().first() is not None
