from httpx import AsyncClient
from starlette import status

from src.users.profile.schemas import UserDb, UserCreate


class TestProfile:
    async def test_success(self, ac: AsyncClient, bearer, test_user):
        response = await ac.get("/api/users/profile", headers=bearer)
        assert response.status_code == 200

        user = UserDb(**response.json())
        assert user.id == test_user.id
        assert user.username == test_user.username
        assert user.email == test_user.email

    async def test_fail(self, ac: AsyncClient):
        response = await ac.get("/api/users/profile")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Not authenticated"


class TestRegister:
    async def test_success(self, ac: AsyncClient, user_create, user_repository):
        response = await ac.post("/api/users/register", json=user_create.model_dump())
        assert response.status_code == status.HTTP_201_CREATED

        user = UserDb(**response.json())
        user_from_db = await user_repository.get_by_id(user.id)

        assert user.username == user_create.username == user_from_db.username
        assert user.email == user_create.email == user_from_db.email
        assert user.full_name == user_create.full_name == user_from_db.full_name
        assert user.age == user_create.age == user_from_db.age
        assert (not user.is_admin) and (not user_from_db.is_admin)

    async def test_fail(self, ac: AsyncClient, user_create):
        user_create.password_confirm = "wrong_password"
        response = await ac.post("/api/users/register", json=user_create.model_dump())
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"][0]["msg"] == "Value error, Passwords do not match"

    async def test_exists(self, ac: AsyncClient, test_user):
        user = UserCreate(**test_user.model_dump(), password_confirm=test_user.password)
        user.email = "another@email.com"
        response = await ac.post("/api/users/register", json=user.model_dump())
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "User with this username already exists"

        user = UserCreate(**test_user.model_dump(), password_confirm=test_user.password)
        user.username = "another_username"
        response = await ac.post("/api/users/register", json=user.model_dump())
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "User with this email already exists"


class TestRegisterSuperuser:
    async def test_success(self, ac: AsyncClient, user_create, user_repository):
        response = await ac.post("/api/users/register-superuser", json=user_create.model_dump())
        assert response.status_code == status.HTTP_201_CREATED

        user = UserDb(**response.json())
        user_from_db = await user_repository.get_by_id(user.id)

        assert user.username == user_create.username == user_from_db.username
        assert user.email == user_create.email == user_from_db.email
        assert user.full_name == user_create.full_name == user_from_db.full_name
        assert user.age == user_create.age == user_from_db.age
        assert user.is_admin and user_from_db.is_admin

    async def test_fail(self, ac: AsyncClient, user_create):
        user_create.password_confirm = "wrong_password"
        response = await ac.post("/api/users/register-superuser", json=user_create.model_dump())
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"][0]["msg"] == "Value error, Passwords do not match"

    async def test_exists(self, ac: AsyncClient, test_user):
        user = UserCreate(**test_user.model_dump(), password_confirm=test_user.password)
        user.email = "another@email.com"
        response = await ac.post("/api/users/register-superuser", json=user.model_dump())
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "User with this username already exists"

        user = UserCreate(**test_user.model_dump(), password_confirm=test_user.password)
        user.username = "another_username"
        response = await ac.post("/api/users/register-superuser", json=user.model_dump())
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "User with this email already exists"


class TestUpdate:
    async def test_success(self, ac: AsyncClient, user_update, user_repository, bearer):
        response = await ac.put("/api/users/update", json=user_update.model_dump(), headers=bearer)
        assert response.status_code == status.HTTP_200_OK

        user = UserDb(**response.json())
        user_from_db = await user_repository.get_by_id(user.id)

        assert user.username == user_update.username == user_from_db.username
        assert user.email == user_update.email == user_from_db.email
        assert user.full_name == user_update.full_name == user_from_db.full_name
        assert user.age == user_update.age == user_from_db.age

    async def test_fail(self, ac: AsyncClient, user_update, bearer):
        response = await ac.put("/api/users/update", json={}, headers=bearer)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            response.json()["detail"][0]["msg"]
            == "Value error, At least one field must be provided"
        )


class TestChangePassword:
    async def test_success(self, ac: AsyncClient, password_update, bearer):
        response = await ac.patch(
            "/api/users/change-password", json=password_update.model_dump(), headers=bearer
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "Password successfully updated, please login again"

        second_response = await ac.patch(
            "/api/users/change-password", json=password_update.model_dump(), headers=bearer
        )
        assert second_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert second_response.json()["detail"] == "Authorization required"

    async def test_fail(self, ac: AsyncClient, password_update, bearer):
        password_update.new_password_confirm = "wrong_password"
        response = await ac.patch(
            "/api/users/change-password", json=password_update.model_dump(), headers=bearer
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"][0]["msg"] == "Value error, Passwords do not match"


class TestDelete:
    async def test_success(self, ac: AsyncClient, bearer):
        response = await ac.delete("/api/users/delete", headers=bearer)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "User successfully deleted"

        second_response = await ac.delete("/api/users/delete", headers=bearer)
        assert second_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert second_response.json()["detail"] == "Authorization required"