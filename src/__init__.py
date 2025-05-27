from fastapi import APIRouter

from src.ping import router as ping_router
from src.tasks.router import router as tasks_router

router = APIRouter()

router.include_router(ping_router)
router.include_router(tasks_router)
