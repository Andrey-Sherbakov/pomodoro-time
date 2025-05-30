from typing import Annotated

from fastapi import Depends

from src.core import SessionDep, RedisCacheDep
from src.tasks.services import CategoryService, TaskService
from src.tasks.cache import TaskCache
from src.tasks.repository import CategoryRepository, TaskRepository


async def get_category_service(session: SessionDep) -> CategoryService:
    return CategoryService(session=session, cat_repo=CategoryRepository(session=session))


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


async def get_tasks_service(session: SessionDep, redis_cache: RedisCacheDep) -> TaskService:
    return TaskService(
        session=session,
        task_repo=TaskRepository(session=session),
        cat_repo=CategoryRepository(session=session),
        task_cache=TaskCache(redis_connection=redis_cache),
    )


TaskServiceDep = Annotated[TaskService, Depends(get_tasks_service)]
