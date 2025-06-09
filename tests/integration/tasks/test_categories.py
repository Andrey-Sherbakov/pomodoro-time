from httpx import AsyncClient
from starlette import status

from src.tasks.models import Category
from src.tasks.schemas import CategoryCreate, CategoryDb


class TestGetAll:
    async def test_success(
        self, ac: AsyncClient, test_category, category_create, category_repository
    ):
        response = await ac.get("/api/categories/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

        await category_repository.add(Category(name=category_create.name))
        await category_repository.session.commit()

        second_response = await ac.get("/api/categories/")
        assert second_response.status_code == status.HTTP_200_OK
        assert isinstance(second_response.json(), list)
        assert len(second_response.json()) == 2


class TestCreate:
    async def test_success(
        self, ac: AsyncClient, category_create, category_repository, admin_bearer
    ):
        response = await ac.post(
            "/api/categories/", json=category_create.model_dump(), headers=admin_bearer
        )
        assert response.status_code == status.HTTP_201_CREATED

        category_resp = CategoryDb(**response.json())
        category_from_db = await category_repository.get_by_id(category_resp.id)

        assert category_from_db
        assert category_from_db.id == category_resp.id
        assert category_from_db.name == category_resp.name == category_create.name

    async def test_exists(self, ac: AsyncClient, test_category, admin_bearer):
        category_data = CategoryCreate(name=test_category.name)
        response = await ac.post(
            "/api/categories/", json=category_data.model_dump(), headers=admin_bearer
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Category with this name already exists"


class TestGetOne:
    async def test_success(self, ac: AsyncClient, test_category):
        response = await ac.get(f"/api/categories/{test_category.id}")
        assert response.status_code == status.HTTP_200_OK

        category_resp = CategoryDb(**response.json())
        assert category_resp.id == test_category.id
        assert category_resp.name == test_category.name

    async def test_fail(self, ac: AsyncClient, category_random: Category):
        response = await ac.get(f"/api/categories/{category_random.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (
            response.json()["detail"]
            == f"There is no {Category.__name__.lower()} with requested id"
        )


class TestUpdate:
    async def test_success(
        self, ac: AsyncClient, category_create, test_category, category_repository, admin_bearer
    ):
        response = await ac.put(
            f"/api/categories/{test_category.id}",
            json=category_create.model_dump(),
            headers=admin_bearer,
        )
        assert response.status_code == status.HTTP_200_OK

        category_resp = CategoryDb(**response.json())
        category_from_db = await category_repository.get_by_id(test_category.id)

        assert category_resp.name == category_from_db.name == category_create.name
        assert category_from_db.id == test_category.id

    async def test_fail(
        self, ac: AsyncClient, category_random: Category, category_create, admin_bearer
    ):
        response = await ac.put(
            f"/api/categories/{category_random.id}",
            json=category_create.model_dump(),
            headers=admin_bearer,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (
            response.json()["detail"]
            == f"There is no {Category.__name__.lower()} with requested id"
        )


class TestDelete:
    async def test_success(self, ac: AsyncClient, test_category, category_repository, admin_bearer):
        response = await ac.delete(f"/api/categories/{test_category.id}", headers=admin_bearer)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "Category successfully deleted"

        deleted_category = await category_repository.get_by_id(test_category.id)
        assert deleted_category is None