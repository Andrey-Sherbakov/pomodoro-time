from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


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
    sub: str  # user id in JWT format
    jti: str  # unique id for one token pair
    iat: int  # when token created
    exp: int  # when token expire
    type: TokenType


class AccessTokenPayload(RefreshTokenPayload, Payload):
    pass


class LogoutResponse(BaseModel):
    detail: str = "Successfully logged out"


class UserLogin(BaseModel):
    username: str
    password: str
