from enum import Enum

from pydantic import BaseModel, EmailStr, ConfigDict


class TokenType(str, Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(RefreshToken):
    access_token: str
    token_type: str = "bearer"


class Payload(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
