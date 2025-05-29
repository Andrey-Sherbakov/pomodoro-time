import json

from redis.asyncio import Redis

from src.core.config import settings
from src.tasks.schemas import DbTask


class TaskCache:
    def __init__(self, redis_connection: Redis) -> None:
        self.redis = redis_connection

    async def get_all_tasks(self, key: str = "all_tasks") -> list[DbTask] | None:
        if tasks_json := await self.redis.get(key):
            tasks = [DbTask.model_validate(task) for task in json.loads(tasks_json)]
            return tasks
        return None

    async def set_all_tasks(
        self, tasks: list[DbTask], key: str = "all_tasks", ex: int = settings.DEFAULT_CACHE_SECONDS
    ) -> None:
        tasks_json = json.dumps([task.model_dump() for task in tasks], ensure_ascii=False)
        await self.redis.set(key, tasks_json, ex=ex)

    async def delete_all_tasks(self, key: str = "all_tasks") -> None:
        await self.redis.delete(key)
