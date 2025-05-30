from fastapi import APIRouter

from src.auth.dependencies import CurrentUserDep, UserServiceDep
from src.auth.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserDb)
async def get_current_user(service: UserServiceDep, current_user: CurrentUserDep) -> UserDb:
    return await service.get_current_user(current_user)
