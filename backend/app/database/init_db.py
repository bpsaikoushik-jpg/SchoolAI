import asyncio
from app.database.session import engine
from app.models import Base  # Imports app.models package, which registers all models with Base.metadata

async def init_db():
    async with engine.begin() as conn:
        # For development, we can create tables directly. 
        # In production, use Alembic.
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
