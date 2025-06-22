from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core import (
    AsyncClientDep,
    PublisherChannelDep,
    RedisBlacklistDep,
    SessionDep,
    SettingsDep,
    AuthSettingsDep,
)
from src.users.auth.clients import GoogleClient, YandexClient
from src.users.auth.exceptions import AuthorizationError, TokenError
from src.users.auth.schemas import AccessTokenPayload, Provider, TokenType, UserPayload
from src.users.auth.services import (
    AuthService,
    GoogleService,
    SecurityService,
    TokenBlacklistService,
    YandexService,
)
from src.users.profile.clients import MailClient
from src.users.profile.repository import UserRepository
from src.users.profile.service import UserService


# mail client dependency
async def get_mail_client(
    publisher_channel: PublisherChannelDep, settings: SettingsDep
) -> MailClient:
    return MailClient(channel=publisher_channel, settings=settings)

MailClientDep = Annotated[MailClient, Depends(get_mail_client)]


# security dependencies
async def get_token_bl_service(
    redis_bl: RedisBlacklistDep, settings: SettingsDep
) -> TokenBlacklistService:
    return TokenBlacklistService(redis_bl=redis_bl, settings=settings)


TokenBLServiceDep = Annotated[TokenBlacklistService, Depends(get_token_bl_service)]


async def get_security_service(
    token_bl: TokenBLServiceDep,
    settings: SettingsDep,
) -> SecurityService:
    return SecurityService(token_bl=token_bl, settings=settings)


SecurityServiceDep = Annotated[SecurityService, Depends(get_security_service)]


# main auth dependencies
async def get_auth_service(
    session: SessionDep, security: SecurityServiceDep, token_bl: TokenBLServiceDep
) -> AuthService:
    return AuthService(
        session=session,
        user_repo=UserRepository(session=session),
        token_bl=token_bl,
        security=security,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_user_service(
    session: SessionDep,
    security: SecurityServiceDep,
    token_bl: TokenBLServiceDep,
    mail_client: MailClientDep,
) -> UserService:
    return UserService(
        session=session,
        user_repo=UserRepository(session=session),
        token_bl=token_bl,
        security=security,
        mail_client=mail_client,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


# clients dependencies
async def get_google_client(
    client_session: AsyncClientDep, auth_settings: AuthSettingsDep
) -> GoogleClient:
    return GoogleClient(
        client=client_session, provider=Provider.google, auth_settings=auth_settings
    )


GoogleClientDep = Annotated[GoogleClient, Depends(get_google_client)]


async def get_yandex_client(
    client_session: AsyncClientDep, auth_settings: AuthSettingsDep
) -> YandexClient:
    return YandexClient(
        client=client_session, provider=Provider.yandex, auth_settings=auth_settings
    )


YandexClientDep = Annotated[YandexClient, Depends(get_yandex_client)]


# OAuth2 dependencies
async def get_google_service(
    user_service: UserServiceDep,
    security: SecurityServiceDep,
    client: GoogleClientDep,
    auth_settings: AuthSettingsDep,
) -> GoogleService:
    return GoogleService(
        user_service=user_service,
        security=security,
        client=client,
        provider=Provider.google,
        auth_settings=auth_settings,
    )


GoogleServiceDep = Annotated[GoogleService, Depends(get_google_service)]


async def get_yandex_service(
    user_service: UserServiceDep,
    security: SecurityServiceDep,
    client: YandexClientDep,
    auth_settings: AuthSettingsDep,
) -> YandexService:
    return YandexService(
        user_service=user_service,
        security=security,
        client=client,
        provider=Provider.yandex,
        auth_settings=auth_settings,
    )


YandexServiceDep = Annotated[YandexService, Depends(get_yandex_service)]

# bearer token dependency
oauth2_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    security: SecurityServiceDep,
) -> UserPayload:
    try:
        payload: AccessTokenPayload = await security.decode_validate_token(
            credentials.credentials, TokenType.access
        )
        return UserPayload(id=int(payload.sub), **payload.model_dump())
    except TokenError:
        raise AuthorizationError


CurrentUserDep = Annotated[UserPayload, Depends(get_current_user)]
