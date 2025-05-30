from typing import Annotated

from fastapi import Depends

from src.auth.exceptions import TokenError, AuthorizationError
from src.auth.repository import UserRepository
from src.auth.schemas import UserPayload, TokenType, AccessTokenPayload
from src.auth.services import AuthService, UserService
from src.auth.services.auth import SecurityService, TokenBlacklistService
from src.core import RedisBlacklistDep, SessionDep, settings


async def get_token_bl_service(redis_bl: RedisBlacklistDep) -> TokenBlacklistService:
    return TokenBlacklistService(redis_bl=redis_bl)


TokenBLServiceDep = Annotated[TokenBlacklistService, Depends(get_token_bl_service)]


async def get_security_service(
    token_bl: TokenBLServiceDep,
) -> SecurityService:
    return SecurityService(token_bl=token_bl)


SecurityServiceDep = Annotated[SecurityService, Depends(get_security_service)]


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
    session: SessionDep, security: SecurityServiceDep, token_bl: TokenBLServiceDep
) -> UserService:
    return UserService(
        session=session,
        user_repo=UserRepository(session=session),
        token_bl=token_bl,
        security=security,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: Annotated[str, Depends(settings.OAUTH2_SCHEME)], security: SecurityServiceDep
) -> UserPayload:
    try:
        payload: AccessTokenPayload = await security.decode_validate_token(token, TokenType.access)
        return UserPayload(id=int(payload.sub), **payload.model_dump())
    except TokenError:
        raise AuthorizationError


CurrentUserDep = Annotated[UserPayload, Depends(get_current_user)]
