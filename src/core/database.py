from typing import AsyncGenerator, Annotated

import redis.asyncio as redis
from fastapi import Depends
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


# redis connection
async def get_redis_connection() -> AsyncGenerator[redis.Redis, None]:
    redis_connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
    try:
        yield redis_connection
    finally:
        await redis_connection.aclose()


# tokens blacklist redis connection
async def get_blacklist_connection() -> AsyncGenerator[redis.Redis, None]:
    blacklist_connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_BLACKLIST_DB,
        decode_responses=True,
    )
    try:
        yield blacklist_connection
    finally:
        await blacklist_connection.aclose()


# dependencies
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
RedisCacheDep = Annotated[redis.Redis, Depends(get_redis_connection)]
RedisBlacklistDep = Annotated[redis.Redis, Depends(get_blacklist_connection)]
