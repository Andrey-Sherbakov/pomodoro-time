from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class Provider(str, Enum):
    google = "GOOGLE"
    yandex = "YANDEX"


class UserData(BaseModel):
    email: EmailStr


class GoogleUserData(UserData):
    sub: str
    name: str


class YandexUserData(UserData):
    id: str
    login: str
    email: EmailStr = Field(alias="default_email")
    real_name: str
    birthday: str
