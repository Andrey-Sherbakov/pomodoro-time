from fastapi import APIRouter

from src.users.auth.schemas import LogoutResponse, RefreshToken, Tokens, UserLogin
from src.users.dependencies import AuthServiceDep, CurrentUserDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Tokens)
async def login(body: UserLogin, service: AuthServiceDep) -> Tokens:
    return await service.login(body)


@router.post("/refresh", response_model=Tokens)
async def refresh(body: RefreshToken, service: AuthServiceDep) -> Tokens:
    return await service.refresh(body)


@router.post("/logout", response_model=LogoutResponse)
async def logout(service: AuthServiceDep, current_user: CurrentUserDep) -> LogoutResponse:
    await service.logout(current_user)
    return LogoutResponse()


@router.post("/logout-all", response_model=LogoutResponse)
async def logout_all(service: AuthServiceDep, current_user: CurrentUserDep) -> LogoutResponse:
    await service.logout_all(current_user)
    return LogoutResponse()
