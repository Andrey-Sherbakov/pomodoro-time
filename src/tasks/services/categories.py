from dataclasses import dataclass

from src.core import SessionServiceBase
from src.tasks.models import Category
from src.tasks.repository import CategoryRepository
from src.tasks.schemas import CategoryDb, CategoryCreate


@dataclass
class CategoryService(SessionServiceBase):
    cat_repo: CategoryRepository

    async def get_all(self) -> list[CategoryDb]:
        categories = await self.cat_repo.list()

        return [CategoryDb.model_validate(category) for category in categories]

    async def create(self, new_category: CategoryCreate) -> CategoryDb:
        category = await self.cat_repo.add(Category(**new_category.model_dump()))
        await self.session.commit()

        return CategoryDb.model_validate(category)

    async def get_by_id(self, cat_id: int) -> CategoryDb:
        category = await self.cat_repo.get_by_id_or_404(cat_id)

        return CategoryDb.model_validate(category)

    async def update_by_id(self, cat_id: int, updated_category: CategoryCreate) -> CategoryDb:
        category = await self.cat_repo.get_by_id_or_404(cat_id)
        for key, value in updated_category.model_dump().items():
            setattr(category, key, value)

        category = await self.cat_repo.update(category)
        await self.session.commit()

        return CategoryDb.model_validate(category)

    async def delete_by_id(self, cat_id: int) -> CategoryDb:
        category = await self.cat_repo.get_by_id_or_404(cat_id)
        deleted_category = CategoryDb.model_validate(category)

        await self.cat_repo.delete(category)
        await self.session.commit()

        return deleted_category
