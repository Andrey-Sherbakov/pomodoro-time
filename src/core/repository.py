from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base

BaseType = TypeVar("BaseType", bound=Base)


class IRepository(Generic[BaseType], ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> BaseType | None: ...

    @abstractmethod
    async def get_by_id_or_404(self, item_id: int) -> BaseType: ...

    @abstractmethod
    async def list(self) -> Sequence[BaseType]: ...

    @abstractmethod
    async def add(self, item: BaseType) -> BaseType: ...

    @abstractmethod
    async def update(self, item: BaseType) -> BaseType: ...

    @abstractmethod
    async def delete(self, item: BaseType) -> None: ...


class ORMRepository(IRepository[BaseType]):
    model: BaseType

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: int) -> BaseType | None:
        stmt = select(self.model).where(self.model.id == item_id)
        item = await self.session.scalar(stmt)
        return item

    async def get_by_id_or_404(self, item_id: int) -> BaseType:
        item = await self.get_by_id(item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no {self.model.__name__.lower()} with requested id",
            )

    async def list(self) -> Sequence[BaseType]:
        stmt = select(self.model)
        items = await self.session.scalars(stmt)
        return items.all()

    async def add(self, item: BaseType) -> BaseType:
        self.session.add(item)
        return item

    async def update(self, item: BaseType) -> BaseType:
        self.session.add(item)
        return item

    async def delete(self, item: BaseType) -> None:
        await self.session.delete(item)
