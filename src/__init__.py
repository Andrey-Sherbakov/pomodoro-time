from fastapi import APIRouter

from src.ping import router as ping_router
from src.auth.routers import router as auth_router
from src.tasks.routers import category_router
from src.tasks.routers import task_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(ping_router)
router.include_router(task_router)
router.include_router(category_router)
