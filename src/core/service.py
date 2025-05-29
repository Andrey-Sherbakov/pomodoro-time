from src.core import SessionDep, RedisDep
from src.tasks.cache import TaskCache
from src.tasks.repository import (
    TaskRepository,
    CategoryRepository,
)


class Service:
    def __init__(self, session: SessionDep, redis: RedisDep):
        self.session = session
        self.redis = redis

        self.task_repo = TaskRepository(session)
        self.cat_repo = CategoryRepository(session)

        self.task_cache = TaskCache(redis)
