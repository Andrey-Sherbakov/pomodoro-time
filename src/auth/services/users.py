from dataclasses import dataclass

from src.auth.exceptions import UsernameAlreadyExists, EmailAlreadyExists, InvalidPassword
from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.schemas import UserPayload, UserDb, UserToDb, UserCreate, UserUpdate, PasswordUpdate
from src.auth.services import SecurityService, TokenBlacklistService
from src.core import SessionServiceBase


@dataclass
class UserService(SessionServiceBase):
    user_repo: UserRepository
    token_bl: TokenBlacklistService
    security: SecurityService

    async def get_current_user(self, current_user: UserPayload) -> UserDb:
        user = await self.user_repo.get_by_id_or_404(current_user.id)

        return UserDb.model_validate(user)

    async def create_user(self, body: UserCreate) -> UserDb:
        await self._validate_username_email(body.username, str(body.email))

        user_to_db = UserToDb(
            hashed_password=self.security.hash_password(body.password),
            **body.model_dump(),
        )
        user = await self.user_repo.add(User(**user_to_db.model_dump()))

        await self.commit()

        return UserDb.model_validate(user)

    async def create_superuser(self, body: UserCreate) -> UserDb:
        await self._validate_username_email(body.username, str(body.email))

        user_to_db = UserToDb(
            hashed_password=self.security.hash_password(body.password),
            is_admin=True,
            **body.model_dump(),
        )
        user = await self.user_repo.add(User(**user_to_db.model_dump()))

        await self.commit()

        return UserDb.model_validate(user)

    async def update_user(self, user_id: int, body: UserUpdate) -> UserDb:
        user = await self.user_repo.get_by_id_or_404(user_id)

        if body.username:
            await self._validate_username(body.username)

        if body.email:
            await self._validate_email(str(body.email))

        for key, value in body.model_dump().items():
            setattr(user, key, value)

        await self.commit()

        return UserDb.model_validate(user)

    async def change_password(self, body: PasswordUpdate, current_user: UserPayload) -> None:
        user = await self.user_repo.get_by_id_or_404(current_user.id)
        if not self.security.verify_password(body.old_password, user.password):
            raise InvalidPassword
        user.password = self.security.hash_password(body.new_password)

        await self.commit()
        await self.token_bl.set_logout_timestamp(user.id)

    async def delete_user(self, user_id: int) -> UserDb:
        user = await self.user_repo.get_by_id_or_404(user_id)
        deleted_user = UserDb.model_validate(user)

        await self.user_repo.delete(user)
        await self.commit()
        await self.token_bl.set_logout_timestamp(user.id)

        return deleted_user

    async def _validate_username(self, username: str) -> None:
        if await self.user_repo.get_by_username(username):
            raise UsernameAlreadyExists

    async def _validate_email(self, email: str) -> None:
        if await self.user_repo.get_by_email(email):
            raise EmailAlreadyExists

    async def _validate_username_email(self, username: str, email: str) -> None:
        await self._validate_username(username)
        await self._validate_email(email)
