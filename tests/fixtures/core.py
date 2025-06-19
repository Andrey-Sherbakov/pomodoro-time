from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core import Base
from src.core.config import get_auth_settings, get_settings
from src.core.dependencies import (
    get_async_session,
    get_redis_blacklist,
    get_redis_cache,
    get_broker_client,
)
from src.main import app
from src.tasks.models import Category, Task
from src.users.profile.models import User
from tests.fixtures.broker import fake_broker_client


# test settings setup
@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def auth_settings():
    return get_auth_settings()


test_settings = get_settings()


# test database setup
engine_test = create_async_engine(test_settings.DATABASE_URL, poolclass=NullPool)
test_async_session_maker = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True)
async def prepare_database(test_user, test_task, test_category):
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_maker() as session:
        user = User(
            username=test_user.username,
            hashed_password=test_user.hashed_password,
            email=test_user.email,
        )
        session.add(user)

        category = Category(name=test_category.name)
        session.add(category)

        task = Task(
            name=test_task.name,
            pomodoro_count=test_task.pomodoro_count,
            category_id=test_task.category_id,
            creator_id=test_task.creator_id,
        )
        session.add(task)

        await session.commit()

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_async_session_test() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as test_session:
        yield test_session


@pytest.fixture
async def session():
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


@pytest.fixture
def redis_cache():
    return REDIS_CACHE


@pytest.fixture
def redis_bl():
    return REDIS_BLACKLIST


# broker setup
# BROKER_CLIENT: BrokerClient | None = None
#
#
# @pytest.fixture(autouse=True)
# async def prepare_broker():
#     global BROKER_CLIENT
#
#     BROKER_CLIENT = BrokerClient(settings=test_settings)
#     await BROKER_CLIENT.start()
#
#     yield
#
#     await BROKER_CLIENT.stop()
#
#
# async def get_broker_client_test() -> BrokerClient:
#     if BROKER_CLIENT is None:
#         raise RuntimeError("Test broker client not initialized")
#     return BROKER_CLIENT
#
#
# @pytest.fixture
# def broker_client():
#     return BROKER_CLIENT


# overriding all dependencies
@pytest.fixture(autouse=True, scope="session")
def override_dependencies():
    app.dependency_overrides[get_async_session] = get_async_session_test
    app.dependency_overrides[get_redis_cache] = get_redis_cache_test
    app.dependency_overrides[get_redis_blacklist] = get_redis_blacklist_test
    app.dependency_overrides[get_broker_client] = fake_broker_client
