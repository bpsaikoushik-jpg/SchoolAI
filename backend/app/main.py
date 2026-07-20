from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.api.v1.api import api_router
from app.database.session import engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # Auth is via Bearer token (Authorization header), not cookies, so credentialed
    # CORS requests aren't needed. Keeping this False avoids the invalid/unsafe
    # combination of a wildcard origin with allow_credentials=True.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    """Liveness probe: process is up. Does not touch the database."""
    return {"status": "ok"}


@app.get("/ready")
async def readiness_check():
    """Readiness probe: process is up AND the database is reachable."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "unreachable", "detail": str(exc)},
        )
