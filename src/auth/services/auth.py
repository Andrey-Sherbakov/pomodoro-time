from dataclasses import dataclass

from src.auth.clients import GoogleClient, YandexClient, BaseClient
from src.auth.exceptions import (
    AuthenticationError,
    TokenError,
)
from src.auth.repository import UserRepository
from src.auth.schemas import (
    Tokens,
    TokenType,
    RefreshToken,
    UserPayload,
    RefreshTokenPayload,
    UserLogin,
    Provider,
)
from src.auth.services.security import TokenBlacklistService, SecurityService
from src.auth.services.users import UserService
from src.core import SessionServiceBase, auth_settings


@dataclass
class AuthService(SessionServiceBase):
    user_repo: UserRepository
    token_bl: TokenBlacklistService
    security: SecurityService

    async def login(self, body: UserLogin) -> Tokens:
        user = await self.user_repo.get_by_username(body.username)
        if not user or not self.security.verify_password(body.password, str(user.hashed_password)):
            raise AuthenticationError

        tokens = self.security.create_tokens(UserPayload.model_validate(user))

        return tokens

    async def refresh(self, form: RefreshToken) -> Tokens:
        payload: RefreshTokenPayload = await self.security.decode_validate_token(
            form.refresh_token, TokenType.refresh
        )
        user = await self.user_repo.get_by_id(int(payload.sub))
        if not user:
            raise TokenError

        new_tokens = self.security.create_tokens(UserPayload.model_validate(user))

        return new_tokens

    async def logout(self, current_user: UserPayload) -> None:
        await self.token_bl.blacklist_tokens(current_user.jti)

    async def logout_all(self, current_user: UserPayload) -> None:
        await self.token_bl.set_logout_timestamp(current_user.id)


@dataclass
class OAuthService:
    client: BaseClient
    provider: Provider
    user_service: UserService
    security: SecurityService

    async def auth(self, code: str) -> Tokens:
        user_data = await self.client.get_user_info(code)

        user = await self.user_service.create_user_from_oauth(user_data, Provider.google)

        tokens = self.security.create_tokens(UserPayload.model_validate(user))
        return tokens

    def get_redirect_url(self) -> str:
        redirect_url = getattr(auth_settings, f"{self.provider.value}_REDIRECT_URL")
        return redirect_url


class GoogleService(OAuthService):
    client: GoogleClient
    provider: Provider.google


class YandexService(OAuthService):
    client: YandexClient
    provider: Provider.yandex
