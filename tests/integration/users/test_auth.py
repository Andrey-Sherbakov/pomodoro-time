import jwt
from fastapi import status
from httpx import AsyncClient

from src.core.config import Settings
from src.users.auth.schemas import (
    AccessTokenPayload,
    RefreshToken,
    RefreshTokenPayload,
    Tokens,
    UserLogin,
)


class TestLogin:
    async def test_success(self, ac: AsyncClient, settings: Settings, test_user):
        body = UserLogin(username=test_user.username, password=test_user.password)
        response = await ac.post("/api/auth/token", json=body.model_dump())
        assert response.status_code == status.HTTP_200_OK

        tokens = Tokens.model_validate(response.json())
        assert tokens.access_token
        assert tokens.refresh_token

        decoded_access = AccessTokenPayload.model_validate(
            jwt.decode(
                tokens.access_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        )
        decoded_refresh = RefreshTokenPayload.model_validate(
            jwt.decode(
                tokens.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        )

        assert decoded_access.username == test_user.username
        assert decoded_access.email == test_user.email
        assert decoded_access.sub == str(test_user.id)
        assert decoded_refresh.sub == str(test_user.id)

    async def test_fail(self, ac: AsyncClient, settings: Settings, test_user):
        body = UserLogin(username=test_user.username, password="wrong_password")

        response = await ac.post("/api/auth/token", json=body.model_dump())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid username or password"


class TestRefresh:
    async def test_success(self, ac: AsyncClient, settings: Settings, test_tokens):
        body = RefreshToken(refresh_token=test_tokens.refresh_token)

        response = await ac.post("/api/auth/refresh", json=body.model_dump())
        assert response.status_code == status.HTTP_200_OK

        tokens = Tokens.model_validate(response.json())
        assert tokens.access_token
        assert tokens.refresh_token

    async def test_fail(self, ac: AsyncClient, settings: Settings, test_tokens):
        body = RefreshToken(refresh_token=test_tokens.refresh_token_exp)

        response = await ac.post("/api/auth/refresh", json=body.model_dump())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Token expired"


class TestLogout:
    async def test_success(self, ac: AsyncClient, bearer, another_bearer):
        response = await ac.post("/api/auth/logout", headers=bearer)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "Successfully logged out"

        second_response = await ac.post("/api/auth/logout", headers=bearer)
        assert second_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert second_response.json()["detail"] == "Authorization required"

        third_response = await ac.post("/api/auth/logout", headers=another_bearer)
        assert third_response.status_code == status.HTTP_200_OK
        assert third_response.json()["detail"] == "Successfully logged out"


class TestLogoutAll:
    async def test_success(self, ac: AsyncClient, bearer, another_bearer):
        response = await ac.post("/api/auth/logout-all", headers=bearer)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "Successfully logged out"

        second_response = await ac.post("/api/auth/logout-all", headers=bearer)
        assert second_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert second_response.json()["detail"] == "Authorization required"

        third_response = await ac.post("/api/auth/logout", headers=another_bearer)
        assert third_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert third_response.json()["detail"] == "Authorization required"