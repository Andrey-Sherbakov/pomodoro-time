from fastapi import HTTPException, status


class TaskNotFound(HTTPException):
    def __init__(self, detail: str = "There is no task with requested id"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)
