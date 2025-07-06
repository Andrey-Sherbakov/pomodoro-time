from fastapi import APIRouter
from sqlalchemy import text

from src.core import SessionDep, RedisCacheDep, RedisBlacklistDep, AsyncClientDep, BrokerClientDep

router = APIRouter(prefix="/ping", tags=["ping"])


@router.get("/app")
async def ping_app() -> dict:
    return {"status": "ok", "component": "app"}


@router.get("/db")
async def ping_db(session: SessionDep) -> dict:
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "component": "database"}
    except Exception as e:
        return {"status": "error", "component": "database", "detail": repr(e)}


@router.get("/redis-cache")
async def ping_redis_cache(redis_cache: RedisCacheDep) -> dict:
    try:
        pong = await redis_cache.ping()
        if pong:
            return {"status": "ok", "component": "redis cache"}
        else:
            return {"status": "error", "component": "redis cache", "detail": "no pong"}
    except Exception as e:
        return {"status": "error", "component": "redis cache", "detail": repr(e)}


@router.get("/redis-blacklist")
async def ping_redis_blacklist(redis_bl: RedisBlacklistDep) -> dict:
    try:
        pong = await redis_bl.ping()
        if pong:
            return {"status": "ok", "component": "redis blacklist"}
        else:
            return {"status": "error", "component": "redis blacklist", "detail": "no pong"}
    except Exception as e:
        return {"status": "error", "component": "redis blacklist", "detail": repr(e)}


@router.get("/httpx-client")
async def ping_httpx_client(client: AsyncClientDep) -> dict:
    try:
        response = await client.get("https://www.google.com")
        response.raise_for_status()
        return {"status": "ok", "component": "httpx client"}
    except Exception as e:
        return {"status": "error", "component": "httpx client", "detail": repr(e)}


@router.get("/broker")
async def ping_broker(broker: BrokerClientDep) -> dict:
    try:
        await broker.ping()
        return {"status": "ok", "component": "message broker"}
    except Exception as e:
        return {"status": "error", "component": "message broker", "detail": repr(e)}
