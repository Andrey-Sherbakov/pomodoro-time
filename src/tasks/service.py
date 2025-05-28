from src.tasks.exceptions import TaskNotFound
from src.tasks.models import tasks as fixtures_tasks
from src.tasks.schemas import DbTask, CreateTask

ID = 4


class TaskService:
    async def get_all(self) -> list[DbTask]:
        tasks = [DbTask(**task) for task in fixtures_tasks]
        return tasks

    async def create(self, new_task: CreateTask) -> DbTask:
        global ID
        ID += 1

        task = DbTask(id=ID, **new_task.model_dump())
        fixtures_tasks.append(task.model_dump())

        return task

    async def get_by_id(self, task_id: int) -> dict:
        for task in fixtures_tasks:
            if task["id"] == task_id:
                return task
        raise TaskNotFound

    async def update_by_id(self, task_id: int, updated_task: CreateTask) -> dict:
        task = await self.get_by_id(task_id)
        task["name"] = updated_task.name
        task["pomodoro_count"] = updated_task.pomodoro_count
        task["category_id"] = updated_task.category_id
        return task

    async def delete_by_id(self, task_id: int) -> dict:
        for i, task in enumerate(fixtures_tasks):
            if task["id"] == task_id:
                deleted_task = task
                del fixtures_tasks[i]
                return deleted_task
        raise TaskNotFound
