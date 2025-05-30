import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, ConfigDict


class TokenType(str, Enum):
    access = "access_token"
    refresh = "refresh_token"


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(RefreshToken):
    access_token: str | None = None
    token_type: str = "bearer"


class Payload(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool


class UserPayload(Payload):
    id: int
    jti: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenPayload(BaseModel):
    sub: str
    jti: str
    iat: int
    exp: int
    type: TokenType


class AccessTokenPayload(RefreshTokenPayload, Payload):
    pass
