from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import Tokens, UserCreate, UserDb, RefreshToken
from src.auth.dependencies import AuthServiceDep, CurrentUserDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Tokens)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep
) -> Tokens:
    return await service.login(form)


@router.post("/refresh", response_model=Tokens)
async def refresh(form: RefreshToken, service: AuthServiceDep) -> Tokens:
    return await service.refresh(form)


@router.post("/register", response_model=UserDb)
async def register(new_user: UserCreate, service: AuthServiceDep) -> UserDb:
    return await service.register(new_user)


@router.post("/register-superuser")
async def register_superuser(new_user: UserCreate, service: AuthServiceDep) -> UserDb:
    return await service.register_superuser(new_user)


@router.post("/logout")
async def logout(service: AuthServiceDep, current_user: CurrentUserDep) -> dict:
    await service.logout(current_user)
    return {"message": "Logged out"}


@router.post("/logout_all")
async def logout_all(service: AuthServiceDep, current_user: CurrentUserDep) -> dict:
    await service.logout_all(current_user)
    return {"message": "Logged out from all devices"}
