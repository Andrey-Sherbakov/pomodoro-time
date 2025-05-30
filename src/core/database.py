from contextlib import asynccontextmanager
from typing import AsyncGenerator, Annotated

import redis.asyncio as redis
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core import settings


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


# postgresql connection
engine = create_async_engine(url=settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# redis connection management
REDIS_CACHE: redis.Redis | None = None
REDIS_BLACKLIST: redis.Redis | None = None


def redis_cache_init():
    global REDIS_CACHE
    REDIS_CACHE = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


def redis_blacklist_init():
    global REDIS_BLACKLIST
    REDIS_BLACKLIST = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_BLACKLIST_DB,
        decode_responses=True,
    )


async def get_redis_cache() -> redis.Redis:
    if REDIS_CACHE is None:
        raise RuntimeError("Redis cache client not initialized")
    return REDIS_CACHE


async def get_redis_blacklist() -> redis.Redis:
    if REDIS_BLACKLIST is None:
        raise RuntimeError("Redis blacklist client not initialized")
    return REDIS_BLACKLIST


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cache_init()
    redis_blacklist_init()

    try:
        await REDIS_CACHE.ping()
    except redis.ConnectionError:
        raise RuntimeError("Redis cache connection error")

    try:
        await REDIS_BLACKLIST.ping()
    except redis.ConnectionError:
        raise RuntimeError("Redis blacklist connection error")

    yield

    await REDIS_CACHE.aclose()
    await REDIS_BLACKLIST.aclose()


# dependencies
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
RedisCacheDep = Annotated[redis.Redis, Depends(get_redis_cache)]
RedisBlacklistDep = Annotated[redis.Redis, Depends(get_redis_blacklist)]
