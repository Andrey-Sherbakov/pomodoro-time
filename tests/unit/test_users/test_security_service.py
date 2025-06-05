import datetime

import jwt

from src.core.config import get_settings
from src.users.auth.schemas import (
    AccessTokenPayload,
    RefreshTokenPayload,
    Tokens,
    TokenType,
    UserPayload,
)
from src.users.auth.services import SecurityService


class TestSecurityService:
    settings = get_settings()
    test_password: str = "test_password"
    test_user_payload: UserPayload = UserPayload(
        username="test", email="test@email.com", is_admin=False, id=1
    )
    test_access_token: AccessTokenPayload = AccessTokenPayload(
        sub="1",
        exp=int(
            (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            ).timestamp()
        ),
        iat=int(datetime.datetime.now(datetime.UTC).timestamp()),
        jti="test_jti",
        type=TokenType.access,
        username="test",
        email="test@email.com",
        is_admin=False,
    )
    test_refresh_token: RefreshTokenPayload = RefreshTokenPayload(
        sub="1",
        exp=int(
            (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            ).timestamp()
        ),
        iat=int(datetime.datetime.now(datetime.UTC).timestamp()),
        jti="test_jti",
        type=TokenType.refresh,
    )

    def test_hash_password(self, test_security_service: SecurityService) -> None:
        hashed_password = test_security_service.hash_password(self.test_password)
        assert isinstance(hashed_password, str)
        assert hashed_password != self.test_password
        assert self.settings.PWD_CONTEXT.verify(self.test_password, hashed_password)

    def test_verify_password(self, test_security_service: SecurityService) -> None:
        hashed_password = self.settings.PWD_CONTEXT.hash(self.test_password)
        assert test_security_service.verify_password(self.test_password, hashed_password)
        assert not test_security_service.verify_password("wrong_password", hashed_password)

    def test_get_token_expiration(self, test_security_service: SecurityService) -> None:
        access_token_expiration = (
            datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ).timestamp()

        refresh_token_expiration = (
            datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ).timestamp()

        assert int(test_security_service.get_token_expiration(TokenType.access)) == int(
            access_token_expiration
        )
        assert int(test_security_service.get_token_expiration(TokenType.refresh)) == int(
            refresh_token_expiration
        )
        assert refresh_token_expiration != access_token_expiration

    def test_create_token(self, test_security_service: SecurityService) -> None:
        jti = "test_jti"
        iat = int(datetime.datetime.now(datetime.UTC).timestamp())

        fake_access_token = test_security_service.create_token(
            self.test_user_payload, TokenType.access, jti
        )
        fake_refresh_token = test_security_service.create_token(
            self.test_user_payload, TokenType.refresh, jti
        )

        decoded_access_token = jwt.decode(
            fake_access_token, self.settings.JWT_SECRET_KEY, algorithms=["HS256"]
        )
        decoded_refresh_token = jwt.decode(
            fake_refresh_token, self.settings.JWT_SECRET_KEY, algorithms=["HS256"]
        )

        assert fake_access_token != fake_refresh_token

        assert (
            decoded_access_token["sub"]
            == decoded_refresh_token["sub"]
            == str(self.test_user_payload.id)
        )
        assert decoded_access_token["jti"] == decoded_refresh_token["jti"] == jti
        assert decoded_access_token["iat"] == decoded_refresh_token["iat"] == iat

        assert decoded_access_token["username"] == self.test_user_payload.username
        assert decoded_access_token["email"] == self.test_user_payload.email
        assert decoded_access_token["type"] == "access_token"
        assert decoded_access_token["is_admin"] == self.test_user_payload.is_admin

        assert decoded_refresh_token["type"] == "refresh_token"

    def test_create_tokens(self, test_security_service) -> None:
        tokens = test_security_service.create_tokens(self.test_user_payload)

        assert isinstance(tokens, Tokens)
        assert tokens.access_token
        assert tokens.refresh_token
        assert tokens.token_type == "bearer"

    async def test_decode_validate_token(self, test_security_service: SecurityService) -> None:
        access_token = jwt.encode(
            self.test_access_token.model_dump(), self.settings.JWT_SECRET_KEY, algorithm="HS256"
        )
        refresh_token = jwt.encode(
            self.test_refresh_token.model_dump(), self.settings.JWT_SECRET_KEY, algorithm="HS256"
        )

        decoded_access_token = await test_security_service.decode_validate_token(
            access_token, TokenType.access
        )
        decoded_refresh_token = await test_security_service.decode_validate_token(
            refresh_token, TokenType.refresh
        )

        assert self.test_access_token == decoded_access_token
        assert self.test_refresh_token == decoded_refresh_token

