from abc import ABC, abstractmethod
from typing import Sequence

from sqlalchemy import select

from src.core.repository import IRepository, ORMRepository
from src.tasks.models import Category, Task


class ITaskRepository(IRepository[Task], ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> Task | None: ...

    @abstractmethod
    async def get_by_category_id(self, category_id: int) -> list[Task]: ...


class ICategoryRepository(IRepository[Category], ABC): ...


class TaskRepository(ORMRepository[Task], ITaskRepository):
    model = Task

    async def get_by_name(self, name: str) -> Task | None:
        stmt = select(Task).where(Task.name == name)
        task = await self.session.scalar(stmt)
        return task

    async def get_by_category_id(self, category_id: int) -> Sequence[Task]:
        stmt = select(Task).where(Task.category_id == category_id)
        tasks = await self.session.scalars(stmt)
        return tasks.all()


class CategoryRepository(ORMRepository[Category], ICategoryRepository):
    model = Category
