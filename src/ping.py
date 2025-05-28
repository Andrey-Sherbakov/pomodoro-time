from fastapi import APIRouter

router = APIRouter(prefix="/ping", tags=["ping"])


@router.get("/db")
async def ping_database() -> dict:
    return {"message": "database is working"}


@router.get("/app")
async def ping_app() -> dict:
    return {"message": "app is working"}
