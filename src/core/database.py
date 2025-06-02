from contextlib import asynccontextmanager
from typing import AsyncGenerator, Annotated

from aiohttp import ClientSession
from fastapi import FastAPI, Depends, Request
from redis.asyncio import Redis, ConnectionError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core import settings


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


# postgresql connection
engine = create_async_engine(url=settings.DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# async client session
def client_session_init() -> ClientSession:
    return ClientSession()


# redis connection management
def redis_cache_init() -> Redis:
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


def redis_blacklist_init() -> Redis:
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_BLACKLIST_DB,
        decode_responses=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client_session = client_session_init()
    app.state.redis_cache = redis_cache_init()
    app.state.redis_blacklist = redis_blacklist_init()

    try:
        await app.state.redis_cache.ping()
    except ConnectionError:
        raise RuntimeError("Redis cache connection error")

    try:
        await app.state.redis_blacklist.ping()
    except ConnectionError:
        raise RuntimeError("Redis blacklist connection error")

    yield

    await app.state.client_session.close()
    await app.state.redis_cache.aclose()
    await app.state.redis_blacklist.aclose()
