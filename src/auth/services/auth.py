import datetime
import uuid
from dataclasses import dataclass

import jwt
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis

from src.auth.exceptions import (
    AuthenticationError,
    InvalidTokenType,
    TokenExpired,
    TokenError,
    TokenRevoked,
)
from src.auth.repository import UserRepository
from src.auth.schemas import (
    Tokens,
    TokenType,
    RefreshToken,
    UserPayload,
    AccessTokenPayload,
    RefreshTokenPayload,
)
from src.core import settings, SessionServiceBase


@dataclass
class AuthService(SessionServiceBase):
    user_repo: UserRepository
    token_bl: "TokenBlacklistService"
    security: "SecurityService"

    async def login(self, form: OAuth2PasswordRequestForm) -> Tokens:
        user = await self.user_repo.get_by_username(form.username)
        if not user or not self.security.verify_password(form.password, str(user.hashed_password)):
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
class TokenBlacklistService:
    redis_bl: Redis

    # blacklist single jwt pair for logout scenario
    async def blacklist_tokens(
        self, jti: str, ex_seconds: int = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    ) -> None:
        await self.redis_bl.set(f"revoked:{jti}", "1", ex=ex_seconds)

    async def is_blacklisted(self, jti: str) -> bool:
        return await self.redis_bl.exists(f"revoked:{jti}") == 1

    # blacklist all jwt pairs given to user for logout all scenario
    async def set_logout_timestamp(
        self, user_id: int, ex_seconds: int = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    ) -> None:
        now_ts = int(datetime.datetime.now(datetime.UTC).timestamp())
        await self.redis_bl.set(f"logout_ts:{user_id}", str(now_ts), ex=ex_seconds)

    async def get_logout_timestamp(self, user_id: str) -> int | None:
        ts = await self.redis_bl.get(f"logout_ts:{user_id}")
        return int(ts) if ts else None


@dataclass
class SecurityService:
    token_bl: TokenBlacklistService

    @staticmethod
    def hash_password(password: str) -> str:
        return settings.PWD_CONTEXT.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return settings.PWD_CONTEXT.verify(password, hashed_password)

    @staticmethod
    def get_token_expiration(token_type: TokenType) -> datetime:
        if token_type == TokenType.access:
            return (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            ).timestamp()
        return (
            datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ).timestamp()

    @classmethod
    def create_token(cls, payload: UserPayload, token_type: TokenType, jti: str) -> str:
        exp = int(cls.get_token_expiration(token_type))
        iat = int(datetime.datetime.now(datetime.UTC).timestamp())

        if token_type == TokenType.access:
            token_payload = AccessTokenPayload(
                sub=str(payload.id),
                exp=exp,
                iat=iat,
                jti=jti,
                type=token_type,
                username=payload.username,
                email=payload.email,
                is_admin=payload.is_admin,
            )
        else:
            token_payload = RefreshTokenPayload(
                sub=str(payload.id),
                exp=exp,
                iat=iat,
                jti=jti,
                type=token_type,
            )

        encoded_jwt = jwt.encode(
            token_payload.model_dump(),
            key=settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        return encoded_jwt

    @classmethod
    def create_tokens(cls, payload: UserPayload) -> Tokens:
        jti = str(uuid.uuid4())

        access_token = cls.create_token(payload, TokenType.access, jti)
        refresh_token = cls.create_token(payload, TokenType.refresh, jti)

        return Tokens(access_token=access_token, refresh_token=refresh_token)

    async def decode_validate_token(
        self, token: str, token_type: TokenType
    ) -> AccessTokenPayload | RefreshTokenPayload:
        try:
            payload = jwt.decode(
                token, key=settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            if payload["type"] != token_type.value:
                raise InvalidTokenType

            if token_type == TokenType.access:
                token_payload = AccessTokenPayload(**payload)
            else:
                token_payload = RefreshTokenPayload(**payload)

            if await self.token_bl.is_blacklisted(token_payload.jti):
                raise TokenRevoked

            logout_ts = await self.token_bl.get_logout_timestamp(token_payload.sub)
            if logout_ts and logout_ts >= int(token_payload.iat):
                raise TokenRevoked

            return token_payload

        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpired
        except jwt.exceptions.InvalidTokenError:
            raise TokenError
