from fastapi import APIRouter
from starlette import status

from src.users.dependencies import CurrentUserDep, UserServiceDep
from src.users.profile.schemas import (
    PasswordUpdate,
    PasswordUpdateResponse,
    UserCreate,
    UserDb,
    UserUpdate,
    UserDeleteResponse,
    UserDelete,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserDb)
async def get_current_user(service: UserServiceDep, current_user: CurrentUserDep) -> UserDb:
    return await service.get_current_user(current_user)


@router.post("/register", response_model=UserDb, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, service: UserServiceDep) -> UserDb:
    return await service.create_user(body)


@router.post("/register-superuser", response_model=UserDb, status_code=status.HTTP_201_CREATED)
async def create_superuser(body: UserCreate, service: UserServiceDep) -> UserDb:
    return await service.create_superuser(body)


@router.put("/update", response_model=UserDb)
async def update_profile(
    body: UserUpdate, service: UserServiceDep, current_user: CurrentUserDep
) -> UserDb:
    return await service.update_user(current_user.id, body)


@router.patch("/change-password", response_model=PasswordUpdateResponse)
async def change_password(
    body: PasswordUpdate, service: UserServiceDep, current_user: CurrentUserDep
) -> PasswordUpdateResponse:
    await service.change_password(body, current_user)
    return PasswordUpdateResponse()


@router.delete("/delete", response_model=UserDeleteResponse)
async def delete_profile(
    body: UserDelete, service: UserServiceDep, current_user: CurrentUserDep
) -> UserDeleteResponse:
    await service.delete_user(body, current_user)
    return UserDeleteResponse()


@router.post("/send_email")
async def send_email(username: str, email: str, service: UserServiceDep):
    await service.mail_client.send_welcome_email(username, email)
    return {"status": status.HTTP_200_OK, "detail": "Email successfully send"}
