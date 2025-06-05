import factory
import pytest
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from src.tasks.models import Task, Category
from src.tasks.schemas import TaskCreate, TaskDb, CategoryDb, CategoryCreate

faker = FakerFactory.create()


@register(_name="task_random")
class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    id = factory.LazyFunction(lambda: faker.random_int(min=2))
    name = factory.LazyFunction(lambda: faker.catch_phrase())
    pomodoro_count = factory.LazyFunction(lambda: faker.random_int(min=1, max=100))
    category_id = 1
    creator_id = 1


@register(_name="category_random")
class CategoryFactory(factory.Factory):
    class Meta:
        model = Category

    id = factory.LazyFunction(lambda: faker.random_int(min=2))
    name = factory.LazyFunction(lambda: faker.word().capitalize())


@pytest.fixture
def test_task() -> TaskDb:
    return TaskDb(
        id=1,
        name="test task",
        pomodoro_count=10,
        category_id=1,
        creator_id=1,
    )


@pytest.fixture
def test_category() -> CategoryDb:
    return CategoryDb(
        id=1,
        name="test category",
    )


@pytest.fixture
def task_create(task_random: Task) -> TaskCreate:
    return TaskCreate(
        name=task_random.name,
        pomodoro_count=task_random.pomodoro_count,
        category_id=task_random.category_id,
    )


@pytest.fixture
def category_create(category_random: Category) -> CategoryCreate:
    return CategoryCreate(name=category_random.name)