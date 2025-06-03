from fastapi import HTTPException, status

from src.users.auth.schemas import Provider


class TokenError(HTTPException):
    def __init__(
        self,
        detail: str = "Token validation error",
        status_code: status = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(detail=detail, status_code=status_code)


class TokenExpired(TokenError):
    def __init__(self, detail: str = "Token expired"):
        super().__init__(detail=detail)


class TokenRevoked(TokenError):
    def __init__(self, detail: str = "Token has been revoked"):
        super().__init__(detail=detail)


class InvalidTokenType(TokenError):
    def __init__(self, detail: str = "Invalid token type"):
        super().__init__(detail=detail)


class AuthenticationError(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid username or password",
        status_code: status = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(detail=detail, status_code=status_code)


class AuthorizationError(HTTPException):
    def __init__(
        self,
        detail: str = "Authorization required",
        status_code: status = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(detail=detail, status_code=status_code)


class AccessDenied(HTTPException):
    def __init__(
        self,
        detail: str = "You dont have permission for this action",
        status_code: status = status.HTTP_403_FORBIDDEN,
    ):
        super().__init__(detail=detail, status_code=status_code)


class ProviderError(HTTPException):
    def __init__(
        self,
        provider: Provider | None = None,
        detail: str = "Unsupported provider",
        status_code: status = status.HTTP_422_UNPROCESSABLE_ENTITY,
    ):
        if provider:
            detail += f": {provider.value}"
        super().__init__(detail=detail, status_code=status_code)
