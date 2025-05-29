from fastapi import APIRouter, Request

import src.auth.dependencies
from src.auth import CurrentUserDep, UserServiceDep
from src.auth.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserDb)
async def get_current_user(
    service: UserServiceDep, current_user: CurrentUserDep, request: Request
) -> UserDb:
    return await src.auth.dependencies.get_current_user(current_user)
