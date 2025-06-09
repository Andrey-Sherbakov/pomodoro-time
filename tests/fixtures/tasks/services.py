import pytest

from src.tasks.services.cache import TaskCache


@pytest.fixture
def task_cache(redis_cache, settings):
    return TaskCache(redis=redis_cache, settings=settings)