from abc import ABC, abstractmethod

from sqlalchemy import select

from src.auth.models import User
from src.core.repository import IRepository, ORMRepository


class IUserRepository(IRepository[User], ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...


class UserRepository(ORMRepository[User], IUserRepository):
    model = User

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        user = await self.session.scalar(stmt)
        return user
