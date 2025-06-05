from dataclasses import dataclass

from httpx import AsyncClient

from src.core.config import AuthSettings
from src.users.auth.schemas import GoogleUserData, Provider, UserDataType, YandexUserData


@dataclass
class BaseClient:
    client: AsyncClient
    provider: Provider
    auth_settings: AuthSettings

    async def get_user_info(self, code: str) -> UserDataType:
        raise NotImplementedError()

    async def _get_user_access_token(self, code: str, provider: Provider) -> str:
        data = {
            "code": code,
            "client_id": getattr(self.auth_settings, f"{provider.value}_CLIENT_ID"),
            "client_secret": getattr(self.auth_settings, f"{provider.value}_CLIENT_SECRET"),
            "redirect_uri": getattr(self.auth_settings, f"{provider.value}_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }
        response = await self.client.post(
            url=getattr(self.auth_settings, f"{provider.value}_TOKEN_URL"), data=data
        )
        return response.json()["access_token"]


class GoogleClient(BaseClient):
    async def get_user_info(self, code: str) -> GoogleUserData:
        access_token = await self._get_user_access_token(code, self.provider)
        user_info = await self.client.get(
            self.auth_settings.GOOGLE_USER_INFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return GoogleUserData(**user_info.json())


class YandexClient(BaseClient):
    async def get_user_info(self, code: str) -> YandexUserData:
        access_token = await self._get_user_access_token(code, self.provider)
        user_info = await self.client.get(
            self.auth_settings.YANDEX_USER_INFO_ENDPOINT,
            headers={"Authorization": f"OAuth {access_token}"},
        )
        return YandexUserData(**user_info.json())
