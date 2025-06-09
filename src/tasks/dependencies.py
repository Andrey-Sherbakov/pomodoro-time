from typing import Annotated

from fastapi import Depends

from src.core import RedisCacheDep, SessionDep, SettingsDep
from src.tasks.repository import CategoryRepository, TaskRepository
from src.tasks.services import CategoryService, TaskService, TaskCacheService, CategoryCacheService


async def get_tasks_cache_service(
    redis_cache: RedisCacheDep, settings: SettingsDep
) -> TaskCacheService:
    return TaskCacheService(redis=redis_cache, settings=settings)


TaskCacheDep = Annotated[TaskCacheService, Depends(get_tasks_cache_service)]


async def get_cat_cache_service(
    redis_cache: RedisCacheDep, settings: SettingsDep
) -> CategoryCacheService:
    return CategoryCacheService(redis=redis_cache, settings=settings)


CatCacheDep = Annotated[CategoryCacheService, Depends(get_cat_cache_service)]


async def get_category_service(session: SessionDep, cat_cache: CatCacheDep) -> CategoryService:
    return CategoryService(
        session=session,
        cat_repo=CategoryRepository(session=session),
        cat_cache=cat_cache,
    )


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


async def get_tasks_service(session: SessionDep, task_cache: TaskCacheDep) -> TaskService:
    return TaskService(
        session=session,
        task_repo=TaskRepository(session=session),
        cat_repo=CategoryRepository(session=session),
        task_cache=task_cache,
    )


TaskServiceDep = Annotated[TaskService, Depends(get_tasks_service)]
