from abc import ABC, abstractmethod
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base
from src.core.log_config import logger


class IRepository[T: Base](ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> T | None: ...

    @abstractmethod
    async def get_by_id_or_404(self, item_id: int) -> T: ...

    @abstractmethod
    async def list(self) -> Sequence[T]: ...

    @abstractmethod
    async def add(self, item: T) -> T: ...

    @abstractmethod
    async def update(self, item: T) -> T: ...

    @abstractmethod
    async def delete(self, item: T) -> None: ...


class ORMRepository[T: Base](IRepository[T]):
    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: int) -> T | None:
        stmt = select(self.model).where(self.model.id == item_id)
        item = await self.session.scalar(stmt)
        return item

    async def get_by_id_or_404(self, item_id: int) -> T:
        item = await self.get_by_id(item_id)
        if item is None:
            logger.warning("%s with id %s not found", self.model.__name__.lower(), item_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no {self.model.__name__.lower()} with requested id",
            )
        return item

    async def list(self) -> Sequence[T]:
        stmt = select(self.model)
        items = await self.session.scalars(stmt)
        return items.all()

    async def add(self, item: T) -> T:
        self.session.add(item)
        return item

    async def update(self, item: T) -> T:
        self.session.add(item)
        return item

    async def delete(self, item: T) -> None:
        await self.session.delete(item)
