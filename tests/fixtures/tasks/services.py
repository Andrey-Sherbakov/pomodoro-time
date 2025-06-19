import pytest

from src.tasks.services import TaskCacheService, CategoryCacheService


@pytest.fixture
def task_cache(redis_cache, settings):
    return TaskCacheService(redis=redis_cache, settings=settings)


@pytest.fixture
def category_cache(redis_cache, settings):
    return CategoryCacheService(redis=redis_cache, settings=settings)