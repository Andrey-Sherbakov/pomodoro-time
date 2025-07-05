from dataclasses import dataclass

from src.core import SessionServiceBase, logger
from src.tasks.services.cache import TaskCacheService
from src.tasks.exceptions import TaskNameAlreadyExists
from src.tasks.models import Task
from src.tasks.repository import CategoryRepository, TaskRepository
from src.tasks.schemas import TaskCreate, TaskDb
from src.users.auth.exceptions import AccessDenied
from src.users.auth.schemas import UserPayload


@dataclass
class TaskService(SessionServiceBase):
    task_repo: TaskRepository
    task_cache: TaskCacheService
    cat_repo: CategoryRepository

    async def get_all(self) -> list[TaskDb]:
        cached_tasks = await self.task_cache.get_all_tasks()
        if cached_tasks is not None:
            logger.debug("Using cache")
            return cached_tasks

        tasks_from_db = await self.task_repo.list()
        tasks = [TaskDb.model_validate(task) for task in tasks_from_db]
        await self.task_cache.set_all_tasks(tasks)

        return tasks

    async def create(self, new_task: TaskCreate, current_user: UserPayload) -> TaskDb:
        await self._validate_name(new_task.name)

        task = await self.task_repo.add(Task(creator_id=current_user.id, **new_task.model_dump()))

        await self.session.commit()
        await self.task_cache.delete_all_tasks()

        logger.info("Task created: id=%s, name=%s", task.id, task.name)

        return TaskDb.model_validate(task)

    async def get_by_id(self, task_id: int) -> TaskDb:
        task = await self.task_repo.get_by_id_or_404(task_id)
        return TaskDb.model_validate(task)

    async def update_by_id(
        self, task_id: int, updated_task: TaskCreate, current_user: UserPayload
    ) -> TaskDb:
        task = await self.task_repo.get_by_id_or_404(task_id)

        if not (current_user.is_admin or current_user.id == task.creator_id):
            logger.info(
                "Failed to update task: id=%s, reason=user %s is not creator or admin",
                task.id,
                current_user.username,
            )
            raise AccessDenied

        for key, value in updated_task.model_dump().items():
            setattr(task, key, value)

        task = await self.task_repo.update(task)
        await self.session.commit()
        await self.task_cache.delete_all_tasks()

        logger.info("Task updated: id=%s", task.id)

        return TaskDb.model_validate(task)

    async def delete_by_id(self, task_id: int, current_user: UserPayload) -> None:
        task = await self.task_repo.get_by_id_or_404(task_id)

        if not (current_user.is_admin or current_user.id == task.creator_id):
            logger.info(
                "Failed to delete task: id=%s, reason=user %s is not creator or admin",
                task_id,
                current_user.username,
            )
            raise AccessDenied

        await self.task_repo.delete(task)
        await self.session.commit()
        await self.task_cache.delete_all_tasks()

        logger.info("Task deleted: id=%s", task.id)

    async def get_tasks_by_category(self, cat_id: int) -> list[TaskDb]:
        category = await self.cat_repo.get_by_id_or_404(cat_id)

        tasks = await self.task_repo.get_by_category_id(category.id)

        return [TaskDb.model_validate(task) for task in tasks]

    async def _validate_name(self, name: str) -> None:
        if await self.task_repo.get_by_name(name):
            raise TaskNameAlreadyExists
