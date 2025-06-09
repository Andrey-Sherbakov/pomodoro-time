from httpx import AsyncClient
from starlette import status

from src.tasks.models import Category, Task
from src.tasks.schemas import TaskCreate, TaskDb


class TestGetAll:
    async def test_success(self, ac: AsyncClient, task_create, task_repository, task_cache):
        response = await ac.get("/api/tasks/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

    async def test_cache(
        self,
        ac: AsyncClient,
        task_create,
        test_user,
        task_repository,
        task_cache,
    ):
        response = await ac.get("/api/tasks/")
        assert response.status_code == 200

        random_task = Task(creator_id=test_user.id, **task_create.model_dump())
        await task_repository.add(random_task)
        await task_repository.session.commit()

        second_response = await ac.get("/api/tasks/")
        assert second_response.status_code == 200
        assert len(second_response.json()) == 1

        await task_cache.delete_all_tasks()

        third_response = await ac.get("/api/tasks/")
        assert third_response.status_code == 200
        assert len(third_response.json()) == 2


class TestCreate:
    async def test_success(self, ac: AsyncClient, task_create, task_repository, bearer):
        response = await ac.post("/api/tasks/", json=task_create.model_dump(), headers=bearer)
        assert response.status_code == status.HTTP_201_CREATED

        task = TaskDb(**response.json())
        task_from_db = await task_repository.get_by_id(task.id)

        assert task_from_db
        assert task_from_db.id == task.id
        assert task_from_db.name == task.name == task_create.name
        assert task_from_db.pomodoro_count == task.pomodoro_count == task_create.pomodoro_count
        assert task_from_db.category_id == task.category_id == task_create.category_id
        assert task_from_db.creator_id == task.creator_id

    async def test_exists(self, ac: AsyncClient, test_task, bearer):
        task = TaskCreate(**test_task.model_dump())
        response = await ac.post("/api/tasks/", json=task.model_dump(), headers=bearer)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Task with this name already exists"


class TestGetOne:
    async def test_success(self, ac: AsyncClient, test_task):
        response = await ac.get(f"/api/tasks/{test_task.id}")
        assert response.status_code == 200

        task = TaskDb(**response.json())
        assert task.id == test_task.id
        assert task.name == test_task.name
        assert task.pomodoro_count == test_task.pomodoro_count
        assert task.category_id == test_task.category_id
        assert task.creator_id == test_task.creator_id

    async def test_fail(self, ac: AsyncClient, task_random: Task):
        response = await ac.get(f"/api/tasks/{task_random.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == f"There is no {Task.__name__.lower()} with requested id"


class TestUpdate:
    async def test_success(self, ac: AsyncClient, task_create, test_task, task_repository, bearer):
        response = await ac.put(
            f"/api/tasks/{test_task.id}",
            json=task_create.model_dump(),
            headers=bearer,
        )
        assert response.status_code == status.HTTP_200_OK

        task = TaskDb(**response.json())
        task_from_db = await task_repository.get_by_id(test_task.id)

        assert task.name == task_from_db.name == task_create.name
        assert task.pomodoro_count == task_from_db.pomodoro_count == task_create.pomodoro_count
        assert task.category_id == task_from_db.category_id == task_create.category_id
        assert task.creator_id == task_from_db.creator_id

    async def test_fail(self, ac: AsyncClient, test_task, task_random: Task, task_create, bearer):
        response = await ac.put(
            f"/api/tasks/{task_random.id}", json=task_create.model_dump(), headers=bearer
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == f"There is no {Task.__name__.lower()} with requested id"


class TestDelete:
    async def test_success(self, ac: AsyncClient, test_task, task_repository):
        response = await ac.delete(f"/api/tasks/{test_task.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "Task successfully deleted"

        deleted_task = await task_repository.get_by_id(test_task.id)
        assert deleted_task is None


class TestGetByCategory:
    async def test_success(
        self, ac: AsyncClient, test_category, test_user, task_create, task_repository
    ):
        response = await ac.get(f"/api/tasks/category/{test_category.id}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

        await task_repository.add(Task(creator_id=test_user.id, **task_create.model_dump()))
        await task_repository.session.commit()

        second_response = await ac.get(f"/api/tasks/category/{test_category.id}")
        assert second_response.status_code == 200
        assert isinstance(second_response.json(), list)
        assert len(second_response.json()) == 2

    async def test_fail(self, ac: AsyncClient, category_random: Category):
        response = await ac.get(f"/api/tasks/category/{category_random.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (
            response.json()["detail"]
            == f"There is no {Category.__name__.lower()} with requested id"
        )
