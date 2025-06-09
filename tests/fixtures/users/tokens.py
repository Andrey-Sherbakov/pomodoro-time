import datetime

import jwt
import pytest
from pydantic import BaseModel

from src.core.config import Settings
from src.users.auth.schemas import AccessTokenPayload, RefreshTokenPayload, TokenType


def encode(payload: dict, settings: Settings) -> str:
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class TestTokens(BaseModel):
    access_token: str
    access_token_exp: str
    admin_access_token: str
    refresh_token: str
    refresh_token_exp: str


@pytest.fixture
def test_tokens(test_user, settings) -> TestTokens:
    refresh_payload = RefreshTokenPayload(
        sub=str(test_user.id),
        exp=int((datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)).timestamp()),
        iat=int(datetime.datetime.now(datetime.UTC).timestamp()),
        jti=test_user.jti,
        type=TokenType.refresh,
    )

    refresh_payload_exp = refresh_payload.model_copy()
    refresh_payload_exp.exp = int(datetime.datetime.now(datetime.UTC).timestamp())

    access_payload = AccessTokenPayload(
        username=test_user.username,
        email=test_user.email,
        is_admin=test_user.is_admin,
        **refresh_payload.model_dump(),
    )
    access_payload.type = TokenType.access

    access_payload_exp = access_payload.model_copy()
    access_payload_exp.exp = int(datetime.datetime.now(datetime.UTC).timestamp())

    admin_access_payload = access_payload.model_copy()
    admin_access_payload.is_admin = True
    admin_access_payload.jti = "backup_test_jti"

    return TestTokens(
        access_token=encode(access_payload.model_dump(), settings),
        access_token_exp=encode(access_payload_exp.model_dump(), settings),
        admin_access_token=encode(admin_access_payload.model_dump(), settings),
        refresh_token=encode(refresh_payload.model_dump(), settings),
        refresh_token_exp=encode(refresh_payload_exp.model_dump(), settings),
    )


# HTTPBearer token
@pytest.fixture
def bearer(test_tokens):
    return {"Authorization": f"Bearer {test_tokens.access_token}"}


@pytest.fixture
def admin_bearer(test_tokens):
    return {"Authorization": f"Bearer {test_tokens.admin_access_token}"}