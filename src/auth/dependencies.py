from typing import Annotated

from fastapi import Depends

from src.auth.repository import UserRepository
from src.auth.schemas import Payload, TokenType
from src.auth.services import AuthService, UserService
from src.auth.services.auth import SecurityService, TokenBlacklistService
from src.core import RedisBlacklistDep, SessionDep, settings


async def get_token_bl_service(redis_bl: RedisBlacklistDep) -> TokenBlacklistService:
    return TokenBlacklistService(redis_bl=redis_bl)


TokenBLServiceDep = Annotated[TokenBlacklistService, Depends(get_token_bl_service)]


async def get_security_service(
    token_bl_service: TokenBLServiceDep,
) -> SecurityService:
    return SecurityService(token_bl_service=token_bl_service)


SecurityServiceDep = Annotated[SecurityService, Depends(get_security_service)]


async def get_auth_service(
    session: SessionDep, security: Annotated[SecurityService, Depends(get_security_service)]
) -> AuthService:
    return AuthService(
        session=session, user_repo=UserRepository(session=session), security=security
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_user_service(session: SessionDep) -> UserService:
    return UserService(session=session, user_repo=UserRepository(session=session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: Annotated[str, Depends(settings.OAUTH2_SCHEME)], security: SecurityServiceDep
) -> Payload:
    payload = await security.validate_token(token, TokenType.access_token)
    return payload


CurrentUserDep = Annotated[Payload, Depends(get_current_user)]
