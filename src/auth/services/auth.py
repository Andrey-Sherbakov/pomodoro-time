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
from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.schemas import Payload, RefreshToken, Tokens, TokenType, UserCreate, UserDb
from src.core import settings
from src.core.service import SessionService


@dataclass
class AuthService(SessionService):
    user_repo: UserRepository
    security: "SecurityService"

    async def login(self, form: OAuth2PasswordRequestForm) -> Tokens:
        user = await self.user_repo.get_by_username(form.username)
        if not user or not self.security.verify_password(form.password, str(user.password)):
            raise AuthenticationError

        tokens = self.security.create_tokens(Payload.model_validate(user))

        return tokens

    async def refresh(self, token: RefreshToken) -> Tokens:
        payload = await self.security.validate_token(token.refresh_token, TokenType.refresh_token)
        new_tokens = self.security.create_tokens(payload)

        return new_tokens

    async def register(self, new_user: UserCreate) -> UserDb:
        new_user.password = self.security.hash_password(new_user.password)
        user = await self.user_repo.add(User(**new_user.model_dump()))

        await self.commit()

        return UserDb.model_validate(user)

    async def register_superuser(self, new_user: UserCreate) -> UserDb:
        new_user.password = self.security.hash_password(new_user.password)
        user = await self.user_repo.add(User(**new_user.model_dump()))
        user.is_admin = True

        await self.session.commit()

        return UserDb.model_validate(user)


@dataclass
class TokenBlacklistService:
    redis_bl: Redis

    # blacklist for logout scenario
    async def blacklist_tokens(self, jti: str, ex_seconds: int) -> None:
        await self.redis_bl.set(f"revoked:{jti}", 1, ex=ex_seconds)

    async def is_blacklisted(self, jti: str) -> bool:
        return await self.redis_bl.exists(f"revoked:{jti}") == 1

    # blacklist for logout all scenario
    async def set_logout_timestamp(
        self, user_id: str, ex_seconds: int = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    ) -> None:
        now_ts = int(datetime.datetime.now(datetime.UTC).timestamp())
        await self.redis_bl.set(f"logout_ts:{user_id}", now_ts, ex=ex_seconds)

    async def get_logout_timestamp(self, user_id: str) -> int | None:
        ts = await self.redis_bl.get(f"logout_ts:{user_id}")
        return ts


@dataclass
class SecurityService:
    token_bl_service: TokenBlacklistService

    @staticmethod
    def hash_password(password: str) -> str:
        return settings.PWD_CONTEXT.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return settings.PWD_CONTEXT.verify(password, hashed_password)

    @staticmethod
    def get_token_expiration(token_type: TokenType) -> datetime.datetime:
        if token_type == TokenType.access_token:
            return datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        return datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    @classmethod
    def create_token(cls, payload: Payload, token_type: TokenType, jti: str) -> str:
        exp = cls.get_token_expiration(token_type)
        iat = datetime.datetime.now(datetime.UTC)

        payload = payload.model_dump()
        payload.update({"exp": exp, "iat": iat, "jti": jti, "type": token_type.value})

        encoded_jwt = jwt.encode(payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return encoded_jwt

    @classmethod
    def create_tokens(cls, payload: Payload) -> Tokens:
        jti = str(uuid.uuid4())

        access_token = cls.create_token(payload, TokenType.access_token, jti)
        refresh_token = cls.create_token(payload, TokenType.refresh_token, jti)

        return Tokens(access_token=access_token, refresh_token=refresh_token)

    async def validate_token(self, token: str, token_type: TokenType) -> Payload:
        try:
            payload = jwt.decode(
                token, key=settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            if payload["type"] != token_type.value:
                raise InvalidTokenType

            if await self.token_bl_service.is_blacklisted(payload["jti"]):
                raise TokenRevoked

            logout_ts = await self.token_bl_service.get_logout_timestamp(payload["id"])
            if logout_ts and logout_ts >= payload["iat"]:
                raise TokenRevoked

            return Payload.model_validate(payload)

        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpired
        except jwt.exceptions.InvalidTokenError:
            raise TokenError
