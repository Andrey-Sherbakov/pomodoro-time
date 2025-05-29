from typing import Annotated

from fastapi import Depends

from src.auth.services import AuthService, UserService
from src.auth.schemas import Payload as PayloadSchema
from src.auth.dependencies import get_current_user, get_auth_service, get_user_service
from src.auth.services import AuthService, UserService

CurrentUserDep = Annotated[PayloadSchema, Depends(get_current_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
