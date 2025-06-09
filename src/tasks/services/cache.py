import json


from src.core import RedisServiceBase
from src.tasks.schemas import TaskDb, CategoryDb


class TaskCacheService(RedisServiceBase):
    async def get_all_tasks(self, key: str = "tasks:all") -> list[TaskDb] | None:
        if tasks_json := await self.redis.get(key):
            tasks = [TaskDb.model_validate(task) for task in json.loads(tasks_json)]
            return tasks
        return None

    async def set_all_tasks(
        self, tasks: list[TaskDb], key: str = "tasks:all", ex: int | None = None
    ) -> None:
        if ex is None:
            ex = self.settings.DEFAULT_CACHE_SECONDS

        tasks_json = json.dumps([task.model_dump() for task in tasks], ensure_ascii=False)
        await self.redis.set(key, tasks_json, ex=ex)

    async def delete_all_tasks(self, key: str = "tasks:all") -> None:
        await self.redis.delete(key)


class CategoryCacheService(RedisServiceBase):
    async def get_all_categories(self, key: str = "categories:all") -> list[CategoryDb] | None:
        if categories_json := await self.redis.get(key):
            categories = [
                CategoryDb.model_validate(category) for category in json.loads(categories_json)
            ]
            return categories
        return None

    async def set_all_categories(
        self, categories: list[CategoryDb], key: str = "categories:all", ex: int | None = None
    ) -> None:
        if ex is None:
            ex = self.settings.DEFAULT_CACHE_SECONDS

        categories_json = json.dumps(
            [category.model_dump() for category in categories], ensure_ascii=False
        )
        await self.redis.set(key, categories_json, ex=ex)

    async def delete_all_categories(self, key: str = "categories:all") -> None:
        await self.redis.delete(key)