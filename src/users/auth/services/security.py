import datetime
import uuid
from dataclasses import dataclass

import jwt
from redis.asyncio import Redis

from src.core import logger
from src.core.config import Settings
from src.users.auth.exceptions import InvalidTokenType, TokenError, TokenExpired, TokenRevoked
from src.users.auth.schemas import (
    AccessTokenPayload,
    RefreshTokenPayload,
    Tokens,
    TokenType,
    UserPayload,
)


@dataclass
class TokenBlacklistService:
    redis_bl: Redis
    settings: Settings

    # blacklist single jwt pair for logout scenario
    async def blacklist_tokens(self, jti: str, ex_seconds: int | None = None) -> None:
        if ex_seconds is None:
            ex_seconds = self.settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

        await self.redis_bl.set(f"revoked:{jti}", "1", ex=ex_seconds)

        logger.info("One pair of tokens revoked: jti=%s", jti)

    async def is_blacklisted(self, jti: str) -> bool:
        return await self.redis_bl.exists(f"revoked:{jti}") == 1

    # blacklist all jwt pairs given to user for logout-all scenario
    async def set_logout_timestamp(self, user_id: int, ex_seconds: int | None = None) -> None:
        if ex_seconds is None:
            ex_seconds = self.settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

        now_ts = int(datetime.datetime.now(datetime.UTC).timestamp())
        await self.redis_bl.set(f"logout_ts:{user_id}", str(now_ts), ex=ex_seconds)

        logger.info("All tokens revoked: user_id=%s", user_id)

    async def get_logout_timestamp(self, user_id: str) -> int | None:
        ts = await self.redis_bl.get(f"logout_ts:{user_id}")
        return int(ts) if ts else None


@dataclass
class SecurityService:
    token_bl: TokenBlacklistService
    settings: Settings

    def hash_password(self, password: str) -> str:
        return self.settings.PWD_CONTEXT.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.settings.PWD_CONTEXT.verify(password, hashed_password)

    def get_token_expiration(self, token_type: TokenType) -> datetime:
        expiration = datetime.datetime.now(datetime.UTC)
        if token_type == TokenType.access:
            expiration += datetime.timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TokenType.refresh:
            expiration += datetime.timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            logger.error("Invalid token type: %s", token_type)
            raise InvalidTokenType

        return expiration.timestamp()

    def create_token(self, payload: UserPayload, token_type: TokenType, jti: str) -> str:
        exp = int(self.get_token_expiration(token_type))
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
        elif token_type == TokenType.refresh:
            token_payload = RefreshTokenPayload(
                sub=str(payload.id),
                exp=exp,
                iat=iat,
                jti=jti,
                type=token_type,
            )
        else:
            logger.error("Invalid token type: %s", token_type)
            raise InvalidTokenType

        encoded_jwt = jwt.encode(
            token_payload.model_dump(),
            key=self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
        )

        return encoded_jwt

    def create_tokens(self, payload: UserPayload) -> Tokens:
        jti = str(uuid.uuid4())

        access_token = self.create_token(payload, TokenType.access, jti)
        refresh_token = self.create_token(payload, TokenType.refresh, jti)

        return Tokens(access_token=access_token, refresh_token=refresh_token)

    async def decode_validate_token(
        self, token: str, token_type: TokenType
    ) -> AccessTokenPayload | RefreshTokenPayload:
        try:
            payload = jwt.decode(
                token, key=self.settings.JWT_SECRET_KEY, algorithms=[self.settings.JWT_ALGORITHM]
            )

            if payload.get("type") != token_type.value:
                logger.error("Invalid token type: %s", payload.get("type"))
                raise InvalidTokenType

            if token_type == TokenType.access:
                token_payload = AccessTokenPayload(**payload)
            else:
                token_payload = RefreshTokenPayload(**payload)

            if await self.token_bl.is_blacklisted(token_payload.jti):
                logger.warning(
                    "Token has been revoked: sub=%s, type=%s", token_payload.sub, token_type.value
                )
                raise TokenRevoked

            logout_ts = await self.token_bl.get_logout_timestamp(token_payload.sub)
            if logout_ts and logout_ts >= int(token_payload.iat):
                logger.warning(
                    "Token has been revoked: sub=%s, type=%s", token_payload.sub, token_type.value
                )
                raise TokenRevoked

            return token_payload

        except jwt.exceptions.ExpiredSignatureError:
            logger.warning("Token expired")
            raise TokenExpired
        except jwt.exceptions.InvalidTokenError:
            logger.warning("Error while decoding token")
            raise TokenError
