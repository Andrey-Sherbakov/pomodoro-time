from abc import abstractmethod, ABC
from dataclasses import dataclass

from httpx import AsyncClient

from src.auth.schemas import GoogleUserData, YandexUserData, UserDataType
from src.core import auth_settings


@dataclass
class BaseClient(ABC):
    client: AsyncClient

    @abstractmethod
    async def get_user_info(self, code: str) -> UserDataType: ...

    @abstractmethod
    async def _get_user_access_token(self, code: str) -> str: ...


class GoogleClient(BaseClient):
    async def get_user_info(self, code: str) -> GoogleUserData:
        access_token = await self._get_user_access_token(code)
        user_info = await self.client.get(
            auth_settings.GOOGLE_USER_INFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return GoogleUserData(**user_info.json())

    async def _get_user_access_token(self, code: str) -> str:
        data = {
            "code": code,
            "client_id": auth_settings.GOOGLE_CLIENT_ID,
            "client_secret": auth_settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": auth_settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        response = await self.client.post(url=auth_settings.GOOGLE_TOKEN_URL, data=data)
        return response.json()["access_token"]


class YandexClient(BaseClient):
    async def get_user_info(self, code: str) -> YandexUserData:
        access_token = await self._get_user_access_token(code)
        user_info = await self.client.get(
            auth_settings.YANDEX_USER_INFO_ENDPOINT,
            headers={"Authorization": f"OAuth {access_token}"},
        )
        return YandexUserData(**user_info.json())

    async def _get_user_access_token(self, code: str) -> str:
        data = {
            "code": code,
            "client_id": auth_settings.YANDEX_CLIENT_ID,
            "client_secret": auth_settings.YANDEX_CLIENT_SECRET,
            "redirect_uri": auth_settings.YANDEX_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        response = await self.client.post(url=auth_settings.YANDEX_TOKEN_URL, data=data)
        return response.json()["access_token"]
