from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from src.core import get_settings, logger
from src.core.broker import broker_startup, broker_shutdown
from src.core.database import (
    redis_startup,
    redis_shutdown,
    async_client_startup,
    async_client_shutdown,
)
from src.tasks.routers import task_router, category_router
from src.users.auth.routers import auth_router
from src.users.profile.router import router as profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    await async_client_startup(app=app)
    await broker_startup(app=app, settings=settings)
    await redis_startup(app=app)

    yield

    await async_client_shutdown(app=app)
    await broker_shutdown(app=app)
    await redis_shutdown(app=app)


app = FastAPI(lifespan=lifespan)


router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(task_router)
router.include_router(category_router)

app.include_router(router)

logger.info("App started")
