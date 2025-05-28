from typing import Annotated

from fastapi import Depends

from src.tasks.service import TaskService

TaskServiceDep = Annotated[TaskService, Depends(TaskService)]
