from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import IRepository, ORMRepository
from src.tasks.exceptions import TaskNotFound
from src.tasks.models import Task


class ITaskRepository(IRepository[Task], ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> Task | None: ...


class TaskRepository(ORMRepository[Task], ITaskRepository):
    model = Task

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_name(self, name: str) -> Task | None:
        stmt = select(Task).where(Task.name == name)
        task = await self.session.scalar(stmt)
        return task


TaskRepositoryDep = Annotated[ITaskRepository, Depends(TaskRepository)]
