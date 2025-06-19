import pytest

from src.tasks.repository import TaskRepository, CategoryRepository


@pytest.fixture
def task_repository(session) -> TaskRepository:
    return TaskRepository(session=session)


@pytest.fixture
def category_repository(session) -> CategoryRepository:
    return CategoryRepository(session=session)
