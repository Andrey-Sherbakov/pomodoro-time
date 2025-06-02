from fastapi import APIRouter

from src.auth.routers.auth import router as auth_router
from src.auth.routers.users import router as user_router
from src.auth.routers.socials import router as socials_router

auth_router.include_router(socials_router)

router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)
