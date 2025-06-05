from fastapi import APIRouter

from src.ping import router as ping_router
from src.tasks.routers import task_router, category_router
from src.users.auth.routers import auth_router
from src.users.profile.router import router as profile_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(task_router)
router.include_router(category_router)
router.include_router(ping_router)
