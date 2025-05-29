from typing import Annotated

from fastapi import Depends

from src.core.database import SessionDep, RedisDep
from src.tasks.cache import TaskCache
from src.tasks.repository import TaskRepository, CategoryRepository
from src.tasks.services import TaskService, CategoryService


async def get_task_service(session: SessionDep, redis: RedisDep):
    return TaskService(
        session=session,
        redis=redis,
        task_repo=TaskRepository(session=session),
        cat_repo=CategoryRepository(session=session),
        task_cache=TaskCache(redis_connection=redis),
    )


async def get_category_service(session: SessionDep, redis: RedisDep):
    return CategoryService(
        session=session,
        redis=redis,
        task_repo=TaskRepository(session=session),
        cat_repo=CategoryRepository(session=session),
        task_cache=TaskCache(redis_connection=redis),
    )


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
