from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.broker import BrokerClient
from src.core.config import AuthSettings, Settings, get_auth_settings, get_settings
from src.core.database import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_async_client(request: Request) -> AsyncClient:
    client_session = request.app.state.async_client
    if client_session is None:
        raise RuntimeError("Redis cache client not initialized")
    return client_session


async def get_broker_client(request: Request) -> BrokerClient:
    broker_client = request.app.state.broker_client
    if broker_client is None:
        raise RuntimeError("Broker client not initialized")
    return broker_client


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
AsyncClientDep = Annotated[AsyncClient, Depends(get_async_client)]
BrokerClientDep = Annotated[BrokerClient, Depends(get_broker_client)]
RedisCacheDep = Annotated[Redis, Depends(get_redis_cache)]
RedisBlacklistDep = Annotated[Redis, Depends(get_redis_blacklist)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
AuthSettingsDep = Annotated[AuthSettings, Depends(get_auth_settings)]
