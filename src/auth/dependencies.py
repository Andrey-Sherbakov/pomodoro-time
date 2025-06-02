from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.clients import GoogleClient, YandexClient
from src.auth.exceptions import TokenError, AuthorizationError
from src.auth.repository import UserRepository
from src.auth.schemas import UserPayload, TokenType, AccessTokenPayload, Provider
from src.auth.services import (
    AuthService,
    UserService,
    SecurityService,
    TokenBlacklistService,
    GoogleService,
    YandexService,
)
from src.core import RedisBlacklistDep, SessionDep, ClientSessionDep


# security services


async def get_token_bl_service(redis_bl: RedisBlacklistDep) -> TokenBlacklistService:
    return TokenBlacklistService(redis_bl=redis_bl)


TokenBLServiceDep = Annotated[TokenBlacklistService, Depends(get_token_bl_service)]


async def get_security_service(
    token_bl: TokenBLServiceDep,
) -> SecurityService:
    return SecurityService(token_bl=token_bl)


SecurityServiceDep = Annotated[SecurityService, Depends(get_security_service)]


# main auth/user services


async def get_user_service(
    session: SessionDep, security: SecurityServiceDep, token_bl: TokenBLServiceDep
) -> UserService:
    return UserService(
        session=session,
        user_repo=UserRepository(session=session),
        token_bl=token_bl,
        security=security,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


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


# OAuth2 clients


async def get_google_client(client_session: ClientSessionDep) -> GoogleClient:
    return GoogleClient(client_session=client_session, provider=Provider.google)


GoogleClientDep = Annotated[GoogleClient, Depends(get_google_client)]


async def get_yandex_client(client_session: ClientSessionDep) -> YandexClient:
    return YandexClient(client_session=client_session, provider=Provider.yandex)


YandexClientDep = Annotated[YandexClient, Depends(get_yandex_client)]


# OAuth2 services


async def get_google_service(
    user_service: UserServiceDep, security: SecurityServiceDep, client: GoogleClientDep
) -> GoogleService:
    return GoogleService(
        user_service=user_service,
        security=security,
        client=client,
        provider=Provider.google,
    )


GoogleServiceDep = Annotated[GoogleService, Depends(get_google_service)]


async def get_yandex_service(
    user_service: UserServiceDep, security: SecurityServiceDep, client: YandexClientDep
) -> YandexService:
    return YandexService(
        user_service=user_service,
        security=security,
        client=client,
        provider=Provider.yandex,
    )


YandexServiceDep = Annotated[YandexService, Depends(get_yandex_service)]

# token dependency
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
