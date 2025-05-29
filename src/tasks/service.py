from typing import Annotated

from fastapi import Depends

from src.core.utils import UOWDep
from src.tasks.models import Task
from src.tasks.schemas import DbTask, CreateTask


class TaskService:
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def get_all(self) -> list[DbTask]:
        cached_tasks = await self.uow.tasks_cache.get_all_tasks()
        if cached_tasks is not None:
            return cached_tasks

        tasks_from_db = await self.uow.task_repo.list()
        tasks = [DbTask.model_validate(task) for task in tasks_from_db]
        await self.uow.tasks_cache.set_all_tasks(tasks)

        return tasks

    async def create(self, new_task: CreateTask) -> DbTask:
        task = await self.uow.task_repo.add(Task(**new_task.model_dump()))

        await self.uow.commit()
        await self.uow.tasks_cache.delete_all_tasks()

        return DbTask.model_validate(task)

    async def get_by_id(self, task_id: int) -> DbTask:
        task = await self.uow.task_repo.get_by_id_or_404(task_id)
        return DbTask.model_validate(task)

    async def update_by_id(self, task_id: int, updated_task: CreateTask) -> DbTask:
        task = await self.uow.task_repo.get_by_id_or_404(task_id)
        for key, value in updated_task.model_dump().items():
            setattr(task, key, value)
        task = await self.uow.task_repo.update(task)

        await self.uow.commit()
        await self.uow.tasks_cache.delete_all_tasks()

        return DbTask.model_validate(task)

    async def delete_by_id(self, task_id: int) -> DbTask:
        task = await self.uow.task_repo.get_by_id_or_404(task_id)
        deleted_task = DbTask.model_validate(task)

        await self.uow.task_repo.delete(task)
        await self.uow.commit()
        await self.uow.tasks_cache.delete_all_tasks()

        return deleted_task


TaskServiceDep = Annotated[TaskService, Depends(TaskService)]
