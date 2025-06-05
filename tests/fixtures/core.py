from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_settings import SettingsConfigDict
from redis.asyncio import Redis
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core import Base
from src.core.config import AuthSettings, Settings, get_settings, get_auth_settings
from src.core.dependencies import get_async_session, get_redis_cache, get_redis_blacklist
from src.main import app
from src.users.profile.models import User


# test settings setup
class TestSettings(Settings):
    model_config = SettingsConfigDict(env_file=".test.env", extra="allow")


class TestAuthSettings(AuthSettings):
    model_config = SettingsConfigDict(env_file=".test.env", extra="allow")


def get_settings_test():
    return TestSettings()


def get_auth_settings_test():
    return TestAuthSettings()


@pytest.fixture
def settings():
    return get_settings_test()


@pytest.fixture
def auth_settings():
    return get_auth_settings_test()


test_settings = get_settings_test()


# test database setup
engine_test = create_async_engine(test_settings.DATABASE_URL, poolclass=NullPool)
test_async_session_maker = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True)
async def prepare_database(test_user):
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_maker() as session:
        user = User(
            username=test_user.username,
            hashed_password=test_user.hashed_password,
            email=test_user.email,
        )
        session.add(user)
        await session.commit()

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_async_session_test() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as test_session:
        yield test_session


# async client for testing
@pytest.fixture
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        yield ac


# test redis clients setup
REDIS_CACHE: Redis | None = None
REDIS_BLACKLIST: Redis | None = None


@pytest.fixture(autouse=True)
async def prepare_redis():
    global REDIS_CACHE
    global REDIS_BLACKLIST

    REDIS_CACHE = Redis(
        host=test_settings.REDIS_HOST,
        port=test_settings.REDIS_PORT,
        db=test_settings.REDIS_DB,
        decode_responses=True,
    )

    REDIS_BLACKLIST = Redis(
        host=test_settings.REDIS_HOST,
        port=test_settings.REDIS_PORT,
        db=test_settings.REDIS_BLACKLIST_DB,
        decode_responses=True,
    )

    try:
        await REDIS_CACHE.ping()
    except ConnectionError:
        raise RuntimeError("Redis test cache connection error")

    try:
        await REDIS_BLACKLIST.ping()
    except ConnectionError:
        raise RuntimeError("Redis test blacklist connection error")

    yield

    await REDIS_CACHE.flushdb()
    await REDIS_BLACKLIST.flushdb()

    await REDIS_CACHE.aclose()
    await REDIS_BLACKLIST.aclose()


async def get_redis_cache_test() -> Redis:
    if REDIS_CACHE is None:
        raise RuntimeError("Test redis cache client not initialized")
    return REDIS_CACHE


async def get_redis_blacklist_test() -> Redis:
    if REDIS_BLACKLIST is None:
        raise RuntimeError("Test redis blacklist client not initialized")
    return REDIS_BLACKLIST


@pytest.fixture(autouse=True, scope="session")
def override_dependencies():
    app.dependency_overrides[get_settings] = get_settings_test
    app.dependency_overrides[get_auth_settings] = get_auth_settings_test
    app.dependency_overrides[get_async_session] = get_async_session_test
    app.dependency_overrides[get_redis_cache] = get_redis_cache_test
    app.dependency_overrides[get_redis_blacklist] = get_redis_blacklist_test