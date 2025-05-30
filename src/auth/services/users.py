from dataclasses import dataclass

from src.auth.repository import UserRepository
from src.auth.schemas import UserPayload, UserDb
from src.core.service import SessionService


@dataclass
class UserService(SessionService):
    user_repo: UserRepository

    async def get_current_user(self, current_user: UserPayload) -> UserDb:
        user = await self.user_repo.get_by_username(current_user.username)

        return UserDb.model_validate(user)
