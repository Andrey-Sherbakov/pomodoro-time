from fastapi import APIRouter
from starlette import status

from src.tasks.dependencies import CategoryServiceDep
from src.tasks.schemas import CategoryCreate, CategoryDb
from src.tasks.schemas.categories import CategoryDeleteResponse
from src.users.dependencies import CurrentUserDep

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryDb])
async def get_all_categories(service: CategoryServiceDep) -> list[CategoryDb]:
    return await service.get_all()


@router.post("/", response_model=CategoryDb, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CategoryCreate, service: CategoryServiceDep, current_user: CurrentUserDep
) -> CategoryDb:
    return await service.create(body, current_user)


@router.get("/{cat_id}", response_model=CategoryDb)
async def get_one_category(cat_id: int, service: CategoryServiceDep) -> CategoryDb:
    return await service.get_by_id(cat_id)


@router.put("/{cat_id}", response_model=CategoryDb)
async def update_category(
    cat_id: int, body: CategoryCreate, service: CategoryServiceDep, current_user: CurrentUserDep
) -> CategoryDb:
    return await service.update_by_id(cat_id, body, current_user)


@router.delete("/{cat_id}", response_model=CategoryDeleteResponse)
async def delete_category(
    cat_id: int, service: CategoryServiceDep, current_user: CurrentUserDep
) -> CategoryDeleteResponse:
    await service.delete_by_id(cat_id, current_user)
    return CategoryDeleteResponse()
