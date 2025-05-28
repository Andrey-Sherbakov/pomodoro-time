from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # postgres params
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT params
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION: int
    REFRESH_TOKEN_EXPIRATION: int

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
