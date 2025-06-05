import json
from dataclasses import dataclass

from redis.asyncio import Redis

from src.core.config import Settings
from src.tasks.schemas import TaskDb


@dataclass
class TaskCache:
    redis: Redis
    settings: Settings

    async def get_all_tasks(self, key: str = "all_tasks") -> list[TaskDb] | None:
        if tasks_json := await self.redis.get(key):
            tasks = [TaskDb.model_validate(task) for task in json.loads(tasks_json)]
            return tasks
        return None

    async def set_all_tasks(
        self, tasks: list[TaskDb], key: str = "all_tasks", ex: int | None = None
    ) -> None:
        if ex is None:
            ex = self.settings.DEFAULT_CACHE_SECONDS

        tasks_json = json.dumps([task.model_dump() for task in tasks], ensure_ascii=False)
        await self.redis.set(key, tasks_json, ex=ex)

    async def delete_all_tasks(self, key: str = "all_tasks") -> None:
        await self.redis.delete(key)
