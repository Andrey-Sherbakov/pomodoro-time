from dataclasses import dataclass

from aiohttp import ClientSession

from src.users.auth.schemas import GoogleUserData, YandexUserData, UserDataType, Provider
from src.core import auth_settings


@dataclass
class BaseClient:
    client_session: ClientSession
    provider: Provider

    async def get_user_info(self, code: str) -> UserDataType:
        raise NotImplementedError()

    async def _get_user_access_token(self, code: str, provider: Provider) -> str:
        data = {
            "code": code,
            "client_id": getattr(auth_settings, f"{provider.value}_CLIENT_ID"),
            "client_secret": getattr(auth_settings, f"{provider.value}_CLIENT_SECRET"),
            "redirect_uri": getattr(auth_settings, f"{provider.value}_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }
        response = await self.client_session.post(
            url=getattr(auth_settings, f"{provider.value}_TOKEN_URL"), data=data
        )
        response_json = await response.json()
        return response_json["access_token"]


class GoogleClient(BaseClient):
    async def get_user_info(self, code: str) -> GoogleUserData:
        access_token = await self._get_user_access_token(code, self.provider)
        user_info = await self.client_session.get(
            auth_settings.GOOGLE_USER_INFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return GoogleUserData(**await user_info.json())


class YandexClient(BaseClient):
    async def get_user_info(self, code: str) -> YandexUserData:
        access_token = await self._get_user_access_token(code, self.provider)
        user_info = await self.client_session.get(
            auth_settings.YANDEX_USER_INFO_ENDPOINT,
            headers={"Authorization": f"OAuth {access_token}"},
        )
        return YandexUserData(**await user_info.json())
