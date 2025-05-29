from abc import ABC

from src.auth.models import User
from src.core.repository import IRepository, ORMRepository


class IUserRepository(IRepository[User], ABC): ...


class UserRepository(ORMRepository[User], IUserRepository):
    model = User
