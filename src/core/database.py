from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


# postgresql connection
engine = create_async_engine(url=settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# async client session
async def async_client_startup(app: FastAPI) -> None:
    app.state.async_client = AsyncClient()


async def async_client_shutdown(app: FastAPI) -> None:
    await app.state.async_client.aclose()


# redis connection management
def redis_cache_init() -> Redis:
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )


def redis_blacklist_init() -> Redis:
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_BLACKLIST_DB,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )


async def redis_startup(app: FastAPI):
    app.state.redis_cache = redis_cache_init()
    app.state.redis_blacklist = redis_blacklist_init()


async def redis_shutdown(app: FastAPI):
    await app.state.redis_cache.aclose()
    await app.state.redis_blacklist.aclose()
