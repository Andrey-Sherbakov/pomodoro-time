from fastapi import HTTPException, status


class TaskNotFound(HTTPException):
    def __init__(self, detail: str = "There is no task with requested id"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class TaskNameAlreadyExists(HTTPException):
    def __init__(
        self,
        detail: str = "Task with this name already exists",
        status_code: status = status.HTTP_409_CONFLICT,
    ):
        super().__init__(detail=detail, status_code=status_code)


class CategoryNameAlreadyExists(HTTPException):
    def __init__(
        self,
        detail: str = "Category with this name already exists",
        status_code: status = status.HTTP_409_CONFLICT,
    ):
        super().__init__(detail=detail, status_code=status_code)
