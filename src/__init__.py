from fastapi import APIRouter

from src.ping import router as ping_router
from src.tasks import tasks_router
from src.users.auth import auth_router
from src.users.profile.router import router as profile_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(tasks_router)
router.include_router(ping_router)
