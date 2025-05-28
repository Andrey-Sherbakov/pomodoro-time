from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(prefix="/ping", tags=["ping"])


@router.get("/db")
async def ping_database() -> dict:
    return {"message": "database is working"}


@router.get("/app")
async def ping_app() -> dict:
    return {"message": settings.DATABASE_URL}
