from src.users.auth.routers.auth import router as auth_router
from src.users.auth.routers.socials import router as socials_router

auth_router.include_router(socials_router)


__all__ = [auth_router, socials_router]