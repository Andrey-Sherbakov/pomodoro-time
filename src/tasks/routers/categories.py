from fastapi import APIRouter

from src.tasks.dependencies import CategoryServiceDep
from src.tasks.schemas import CategoryCreate, CategoryDb

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryDb])
async def get_all_categories(service: CategoryServiceDep) -> list[CategoryDb]:
    return await service.get_all()


@router.post("/", response_model=CategoryDb)
async def create_category(body: CategoryCreate, service: CategoryServiceDep) -> CategoryDb:
    return await service.create(body)


@router.get("/{cat_id}", response_model=CategoryDb)
async def get_one_category(cat_id: int, service: CategoryServiceDep) -> CategoryDb:
    return await service.get_by_id(cat_id)


@router.put("/{cat_id}", response_model=CategoryDb)
async def update_category(
    cat_id: int, body: CategoryCreate, service: CategoryServiceDep
) -> CategoryDb:
    return await service.update_by_id(cat_id, body)


@router.delete("/{cat_id}", response_model=CategoryDb)
async def delete_category(cat_id: int, service: CategoryServiceDep) -> CategoryDb:
    return await service.delete_by_id(cat_id)
