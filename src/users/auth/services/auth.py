from dataclasses import dataclass

from src.core import SessionServiceBase, logger
from src.core.config import AuthSettings
from src.users.auth.clients import BaseClient, GoogleClient, YandexClient
from src.users.auth.exceptions import (
    AuthenticationError,
    TokenError,
)
from src.users.auth.schemas import (
    Provider,
    RefreshToken,
    RefreshTokenPayload,
    Tokens,
    TokenType,
    UserLogin,
    UserPayload,
)
from src.users.auth.services import SecurityService, TokenBlacklistService
from src.users.profile.repository import UserRepository
from src.users.profile.service import UserService


@dataclass
class AuthService(SessionServiceBase):
    user_repo: UserRepository
    token_bl: TokenBlacklistService
    security: SecurityService

    async def login(self, body: UserLogin) -> Tokens:
        user = await self.user_repo.get_by_username(body.username)
        if not user or not self.security.verify_password(body.password, str(user.hashed_password)):
            logger.info(
                "Failed login: username=%s, reason=Invalid username or password", body.username
            )
            raise AuthenticationError

        tokens = self.security.create_tokens(UserPayload.model_validate(user))

        logger.info("User logged in: username=%s", user.username)

        return tokens

    async def refresh(self, body: RefreshToken) -> Tokens:
        payload: RefreshTokenPayload = await self.security.decode_validate_token(
            body.refresh_token, TokenType.refresh
        )
        user = await self.user_repo.get_by_id(int(payload.sub))
        if not user:
            logger.warning("Failed token refresh: user not found (sub=%s)", payload.sub)
            raise TokenError

        new_tokens = self.security.create_tokens(UserPayload.model_validate(user))

        logger.info("Tokens updated: username=%s", user.username)

        return new_tokens

    async def logout(self, current_user: UserPayload) -> None:
        await self.token_bl.blacklist_tokens(current_user.jti)
        logger.info("User logged out: username=%s", current_user.username)

    async def logout_all(self, current_user: UserPayload) -> None:
        await self.token_bl.set_logout_timestamp(current_user.id)
        logger.info("User logged out from all devices: username=%s", current_user.username)


@dataclass
class OAuthService:
    client: BaseClient
    provider: Provider
    user_service: UserService
    security: SecurityService
    auth_settings: AuthSettings

    async def auth(self, code: str) -> Tokens:
        user_data = await self.client.get_user_info(code)

        user = await self.user_service.get_create_user_from_oauth(user_data, self.provider)

        tokens = self.security.create_tokens(UserPayload.model_validate(user))
        return tokens

    def get_redirect_url(self) -> str:
        redirect_url = getattr(self.auth_settings, f"{self.provider.value}_REDIRECT_URL")
        logger.info("OAuth redirect URL for %s: %s", self.provider.value, redirect_url)
        return redirect_url


class GoogleService(OAuthService):
    client: GoogleClient


class YandexService(OAuthService):
    client: YandexClient
