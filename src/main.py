from fastapi import FastAPI, APIRouter

from src.core import lifespan
from src.ping import router as ping_router
from src.tasks.routers import task_router, category_router
from src.users.auth.routers import auth_router
from src.users.profile.router import router as profile_router

app = FastAPI(lifespan=lifespan)


router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(task_router)
router.include_router(category_router)
router.include_router(ping_router)


app.include_router(router)
