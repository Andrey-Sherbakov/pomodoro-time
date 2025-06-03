from fastapi import HTTPException, status


class UsernameAlreadyExists(HTTPException):
    def __init__(
        self,
        detail: str = "User with this username already exists",
        status_code: status = status.HTTP_409_CONFLICT,
    ):
        super().__init__(detail=detail, status_code=status_code)


class EmailAlreadyExists(HTTPException):
    def __init__(
        self,
        detail: str = "User with this email already exists",
        status_code: status = status.HTTP_409_CONFLICT,
    ):
        super().__init__(detail=detail, status_code=status_code)


class InvalidPassword(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid old password",
        status_code: status = status.HTTP_422_UNPROCESSABLE_ENTITY,
    ):
        super().__init__(detail=detail, status_code=status_code)
