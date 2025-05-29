from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import Tokens, UserCreate, UserDb
from src.auth.schemas.auth import RefreshToken
from src.auth import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Tokens)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep
) -> Tokens:
    return await service.login(form)


@router.post("/refresh", response_model=Tokens)
async def refresh(token: RefreshToken, service: AuthServiceDep) -> Tokens:
    return await service.refresh(token)


@router.post("/register", response_model=UserDb)
async def register(new_user: UserCreate, service: AuthServiceDep) -> UserDb:
    return await service.register(new_user)


@router.post("/register-superuser")
async def register_superuser(new_user: UserCreate, service: AuthServiceDep) -> UserDb:
    return await service.register_superuser(new_user)
