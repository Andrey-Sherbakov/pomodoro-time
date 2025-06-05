import os
from functools import lru_cache

from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Auth settings
    PWD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # postgresql connection settings
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # redis connection settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_BLACKLIST_DB: int
    DEFAULT_CACHE_SECONDS: int

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(extra="allow")


class AuthSettings(BaseSettings):
    FRONTEND_URL: str

    # google
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_TOKEN_URL: str = "https://accounts.google.com/o/oauth2/token"
    GOOGLE_USER_INFO_ENDPOINT: str = "https://www.googleapis.com/oauth2/v3/userinfo"

    @property
    def GOOGLE_REDIRECT_URL(self) -> str:
        return (
            f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id="
            f"{self.GOOGLE_CLIENT_ID}&redirect_uri={self.GOOGLE_REDIRECT_URI}&scope="
            f"openid%20profile%20email&access_type=offline"
        )

    # yandex
    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_REDIRECT_URI: str
    YANDEX_TOKEN_URL: str = "https://oauth.yandex.ru/token"
    YANDEX_USER_INFO_ENDPOINT: str = "https://login.yandex.ru/info?format=json"

    @property
    def YANDEX_REDIRECT_URL(self) -> str:
        return (
            f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self.YANDEX_CLIENT_ID}"
            f"&redirect_uri={self.YANDEX_REDIRECT_URI}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache
def get_settings() -> Settings:
    environment = os.environ.get("ENVIRONMENT", "dev")
    env_file = f".{environment.lower()}.env"
    return Settings(_env_file=env_file)


@lru_cache
def get_auth_settings() -> AuthSettings:
    environment = os.environ.get("ENVIRONMENT", "dev")
    env_file = f".{environment.lower()}.env"
    return AuthSettings(_env_file=env_file)