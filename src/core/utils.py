from typing import Annotated

from fastapi import Depends

from src.core.database import SessionDep, RedisDep
from src.tasks.cache import TaskCache
from src.tasks.repository import TaskRepository


class UnitOfWork:
    def __init__(self, session: SessionDep, redis: RedisDep) -> None:
        self.session = session
        self.redis = redis

        self.task_repo = TaskRepository(session)
        self.tasks_cache = TaskCache(redis)

    async def commit(self) -> None:
        await self.session.commit()


UOWDep = Annotated[UnitOfWork, Depends(UnitOfWork)]
