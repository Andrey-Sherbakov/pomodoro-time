from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.auth.dependencies import GoogleServiceDep, YandexServiceDep
from src.auth.schemas import Tokens

router = APIRouter(tags=["socials"])


@router.get("/login/google", response_class=RedirectResponse)
async def google_login(service: GoogleServiceDep) -> RedirectResponse:
    redirect_url = await service.get_redirect_url()
    return RedirectResponse(url=redirect_url)


@router.get("/google", response_model=Tokens, include_in_schema=False)
async def google_auth(service: GoogleServiceDep, code: str) -> Tokens:
    return await service.auth(code)


@router.get("/login/yandex", response_class=RedirectResponse)
async def yandex_login(service: YandexServiceDep) -> RedirectResponse:
    redirect_url = await service.get_redirect_url()
    return RedirectResponse(url=redirect_url)


@router.get("/yandex", response_model=Tokens, include_in_schema=False)
async def yandex_auth(service: YandexServiceDep, code: str) -> Tokens:
    return await service.auth(code)
