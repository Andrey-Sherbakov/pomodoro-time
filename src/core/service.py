import dataclasses

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.tasks.cache import TaskCache
from src.tasks.repository import ITaskRepository, ICategoryRepository


@dataclasses.dataclass
class Service:
    session: AsyncSession
    redis: Redis

    task_repo: ITaskRepository
    cat_repo: ICategoryRepository

    task_cache: TaskCache
