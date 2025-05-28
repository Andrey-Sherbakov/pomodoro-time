from typing import Annotated

from fastapi import Depends

from src.core.utils import UOWDep
from src.tasks.models import Task
from src.tasks.schemas import DbTask, CreateTask


class TaskService:
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def get_all(self) -> list[DbTask]:
        tasks = await self.uow.tasks.list()
        return [DbTask.model_validate(task) for task in tasks]

    async def create(self, new_task: CreateTask) -> DbTask:
        task = await self.uow.tasks.add(Task(**new_task.model_dump()))
        await self.uow.commit()
        return DbTask.model_validate(task)

    async def get_by_id(self, task_id: int) -> DbTask:
        task = await self.uow.tasks.get_by_id_or_404(task_id)
        return DbTask.model_validate(task)

    async def update_by_id(self, task_id: int, updated_task: CreateTask) -> DbTask:
        task = await self.uow.tasks.get_by_id_or_404(task_id)
        for key, value in updated_task.model_dump().items():
            setattr(task, key, value)
        task = await self.uow.tasks.update(task)
        await self.uow.commit()
        return DbTask.model_validate(task)

    async def delete_by_id(self, task_id: int) -> DbTask:
        task = await self.uow.tasks.get_by_id_or_404(task_id)
        deleted_task = DbTask.model_validate(task)
        await self.uow.tasks.delete(task)
        await self.uow.commit()
        return deleted_task


TaskServiceDep = Annotated[TaskService, Depends(TaskService)]
