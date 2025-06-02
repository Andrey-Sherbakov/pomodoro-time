from typing import AsyncGenerator, Annotated

from aiohttp import ClientSession
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_client_session(request: Request) -> ClientSession:
    client_session = request.app.state.client_session
    if client_session is None:
        raise RuntimeError("Redis cache client not initialized")
    return client_session


async def get_redis_cache(request: Request) -> Redis:
    redis_cache = request.app.state.redis_cache
    if redis_cache is None:
        raise RuntimeError("Redis cache client not initialized")
    return redis_cache


async def get_redis_blacklist(request: Request) -> Redis:
    redis_blacklist = request.app.state.redis_blacklist
    if redis_blacklist is None:
        raise RuntimeError("Redis blacklist client not initialized")
    return redis_blacklist


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
ClientSessionDep = Annotated[ClientSession, Depends(get_client_session)]
RedisCacheDep = Annotated[Redis, Depends(get_redis_cache)]
RedisBlacklistDep = Annotated[Redis, Depends(get_redis_blacklist)]
