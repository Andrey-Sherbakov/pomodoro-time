from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings


@dataclass
class SessionServiceBase:
    session: AsyncSession

    async def commit(self):
        await self.session.commit()


@dataclass
class RedisServiceBase:
    redis: Redis
    settings: Settings