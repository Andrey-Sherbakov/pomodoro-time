from dataclasses import dataclass

from src.core import SessionServiceBase, logger
from src.tasks.exceptions import CategoryNameAlreadyExists
from src.tasks.models import Category
from src.tasks.repository import CategoryRepository
from src.tasks.schemas import CategoryCreate, CategoryDb
from src.tasks.services.cache import CategoryCacheService
from src.users.auth.exceptions import AccessDenied
from src.users.auth.schemas import UserPayload


@dataclass
class CategoryService(SessionServiceBase):
    cat_repo: CategoryRepository
    cat_cache: CategoryCacheService

    async def get_all(self) -> list[CategoryDb]:
        if cached_categories := await self.cat_cache.get_all_categories():
            logger.debug("Using cache")
            return cached_categories

        categories_from_db = await self.cat_repo.list()
        categories = [CategoryDb.model_validate(category) for category in categories_from_db]
        await self.cat_cache.set_all_categories(categories)

        return categories

    async def create(self, new_category: CategoryCreate, current_user: UserPayload) -> CategoryDb:
        if not current_user.is_admin:
            logger.info(
                "Category create failed: name=%s, reason=user %s is not admin",
                new_category.name,
                current_user.username,
            )
            raise AccessDenied

        await self._validate_name(new_category.name)

        category = await self.cat_repo.add(Category(**new_category.model_dump()))
        await self.session.commit()
        await self.cat_cache.delete_all_categories()

        logger.info("Category created: id=%s, name=%s", category.id, category.name)

        return CategoryDb.model_validate(category)

    async def get_by_id(self, cat_id: int) -> CategoryDb:
        category = await self.cat_repo.get_by_id_or_404(cat_id)

        return CategoryDb.model_validate(category)

    async def update_by_id(
        self, cat_id: int, updated_category: CategoryCreate, current_user: UserPayload
    ) -> CategoryDb:
        if not current_user.is_admin:
            logger.info(
                "Category update failed: id=%s, reason=user %s is not admin",
                cat_id,
                current_user.username,
            )
            raise AccessDenied

        category = await self.cat_repo.get_by_id_or_404(cat_id)
        for key, value in updated_category.model_dump().items():
            setattr(category, key, value)

        category = await self.cat_repo.update(category)
        await self.session.commit()
        await self.cat_cache.delete_all_categories()

        logger.info("Category updated: id=%s", category.id)

        return CategoryDb.model_validate(category)

    async def delete_by_id(self, cat_id: int, current_user: UserPayload) -> None:
        if not current_user.is_admin:
            logger.info(
                "Category delete failed: id=%s, reason=user %s is not admin",
                cat_id,
                current_user.username,
            )
            raise AccessDenied

        category = await self.cat_repo.get_by_id_or_404(cat_id)

        await self.cat_repo.delete(category)
        await self.session.commit()
        await self.cat_cache.delete_all_categories()

        logger.info("Category deleted: id=%s", category.id)

    async def _validate_name(self, name: str) -> None:
        if await self.cat_repo.get_by_name(name):
            raise CategoryNameAlreadyExists
