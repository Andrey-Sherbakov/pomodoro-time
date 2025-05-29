from fastapi import APIRouter

from src.ping import router as ping_router
from src.tasks.routers import task_router
from src.tasks.routers import category_router

router = APIRouter()

router.include_router(ping_router)
router.include_router(task_router)
router.include_router(category_router)


# importing models for proper sqlalchemy relationship work
# from src.core.database import Base as _
# from src.categories.models import Category as _
# from src.tasks.models import Task as _
