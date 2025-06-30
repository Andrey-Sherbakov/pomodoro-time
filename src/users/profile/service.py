import datetime
from dataclasses import dataclass

from slugify import slugify

from src.core import SessionServiceBase, logger
from src.users.auth.exceptions import ProviderError
from src.users.auth.schemas import (
    GoogleUserData,
    Provider,
    UserData,
    UserPayload,
    YandexUserData,
)
from src.users.auth.services.security import SecurityService, TokenBlacklistService
from src.users.profile.clients import MailClient
from src.users.profile.exceptions import (
    EmailAlreadyExists,
    InvalidPassword,
    UsernameAlreadyExists,
)
from src.users.profile.models import User
from src.users.profile.repository import UserRepository
from src.users.profile.schemas import (
    PasswordUpdate,
    UserCreate,
    UserDb,
    UserToDb,
    UserUpdate,
    UserDelete,
)


@dataclass
class UserService(SessionServiceBase):
    user_repo: UserRepository
    token_bl: TokenBlacklistService
    security: SecurityService
    mail_client: MailClient

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

        logger.info(f"User created: username={user.username}, email={user.email}")

        await self.mail_client.send_welcome_email(username=user.username, email=user.email)

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

        logger.info(f"Superuser created: username={user.username}, email={user.email}")

        await self.mail_client.send_welcome_email(username=user.username, email=user.email)

        return UserDb.model_validate(user)

    async def update_user(self, user_id: int, body: UserUpdate) -> UserDb:
        user = await self.user_repo.get_by_id_or_404(user_id)

        if body.username:
            await self._validate_username(body.username)

        if body.email:
            await self._validate_email(str(body.email))

        for key, value in body.model_dump().items():
            if value:
                setattr(user, key, value)

        await self.commit()

        logger.info(f"User updated: username={user.username}")

        return UserDb.model_validate(user)

    async def change_password(self, body: PasswordUpdate, current_user: UserPayload) -> None:
        user = await self.user_repo.get_by_id_or_404(current_user.id)
        if not self.security.verify_password(body.old_password, user.hashed_password):
            logger.info(
                f"Password change failed: username={user.username}, reason=Invalid old password"
            )
            raise InvalidPassword
        user.hashed_password = self.security.hash_password(body.new_password)

        await self.commit()

        logger.info(f"Password changed: username={user.username}")

        await self.token_bl.set_logout_timestamp(user.id)
        await self.mail_client.send_password_change_email(username=user.username, email=user.email)

    async def delete_user(self, body: UserDelete, current_user: UserPayload) -> None:
        user = await self.user_repo.get_by_id_or_404(current_user.id)

        if not self.security.verify_password(body.password, user.hashed_password):
            logger.info(f"User delete failure: username={user.username}, reason: Invalid password")
            raise InvalidPassword

        await self.user_repo.delete(user)
        await self.commit()

        logger.info(f"User deleted: username={current_user.username}")

        await self.token_bl.set_logout_timestamp(user.id)
        await self.mail_client.send_goodbye_email(username=user.username, email=user.email)

    async def get_create_user_from_oauth[T: UserData](
        self, user_data: T, provider: Provider
    ) -> User:
        if user := await self.user_repo.get_by_email(email=str(user_data.email)):
            logger.info(f"OAuth user exists: username={user.username}, provider={provider.value}")
            return user

        if provider == provider.google:
            user_to_db = await self._user_from_google_to_db(user_data)
        elif provider == provider.yandex:
            user_to_db = await self._user_from_yandex_to_db(user_data)
        else:
            logger.error(f"Unsupported provider: {provider}")
            raise ProviderError

        user = await self.user_repo.add(User(**user_to_db.model_dump()))
        await self.commit()

        logger.info(
            f"Created new user from OAuth: username={user.username}, provider={provider.value}"
        )

        await self.mail_client.send_welcome_email(username=user.username, email=user.email)

        return user

    async def _user_from_google_to_db(self, user_data: GoogleUserData) -> UserToDb:
        username = password = slugify(user_data.name)
        try:
            await self._validate_username(username)
        except UsernameAlreadyExists:
            username = slugify(user_data.name + user_data.sub)

        return UserToDb(
            username=username,
            hashed_password=self.security.hash_password(password),
            email=user_data.email,
            full_name=user_data.name,
        )

    async def _user_from_yandex_to_db(self, user_data: YandexUserData) -> UserToDb:
        username = password = slugify(user_data.login)
        try:
            await self._validate_username(username)
        except UsernameAlreadyExists:
            username = slugify(user_data.name + user_data.id)

        return UserToDb(
            username=username,
            hashed_password=self.security.hash_password(password),
            email=user_data.email,
            full_name=user_data.real_name,
            age=self._calculate_age_from_birthday(user_data.birthday),
        )

    async def _validate_username(self, username: str) -> None:
        if await self.user_repo.get_by_username(username):
            raise UsernameAlreadyExists

    async def _validate_email(self, email: str) -> None:
        if await self.user_repo.get_by_email(email):
            raise EmailAlreadyExists

    async def _validate_username_email(self, username: str, email: str) -> None:
        await self._validate_username(username)
        await self._validate_email(email)

    @staticmethod
    def _calculate_age_from_birthday(birthday: str) -> int:
        birthdate = datetime.datetime.strptime(birthday, "%Y-%m-%d").date()
        today = datetime.date.today()
        age = (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )
        return age
