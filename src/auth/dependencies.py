from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth import UserService
from src.auth.repository import UserRepository
from src.auth.schemas import Payload, TokenType
from src.auth.services import AuthService
from src.auth.services.auth import SecurityService, TokenBlacklistService
from src.core import SessionDep
from src.core.database import RedisBlacklistDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_token_bl_service(redis_bl: RedisBlacklistDep) -> TokenBlacklistService:
    return TokenBlacklistService(redis_bl=redis_bl)


async def get_security_service(
    token_bl_service: Annotated[TokenBlacklistService, Depends(get_token_bl_service)],
) -> SecurityService:
    return SecurityService(token_bl_service=token_bl_service)


async def get_auth_service(
    session: SessionDep,
    security: Annotated[SecurityService, Depends(get_security_service)],
) -> AuthService:
    return AuthService(
        session=session, user_repo=UserRepository(session=session), security=security
    )


async def get_user_service(session: SessionDep) -> UserService:
    return UserService(session=session, user_repo=UserRepository(session=session))


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    security: Annotated[SecurityService, Depends(get_security_service)],
) -> Payload:
    payload = await security.validate_token(token, TokenType.access_token)
    return payload
