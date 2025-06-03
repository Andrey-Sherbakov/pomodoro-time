from abc import ABC, abstractmethod

from sqlalchemy import select

from src.users.profile.models import User
from src.core.repository import IRepository, ORMRepository


class IUserRepository(IRepository[User], ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...


class UserRepository(ORMRepository[User], IUserRepository):
    model = User

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        user = await self.session.scalar(stmt)
        return user

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        user = await self.session.scalar(stmt)
        return user
