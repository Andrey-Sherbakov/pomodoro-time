from typing import Annotated

from fastapi import Depends

from src.tasks.services.categories import CategoryService
from src.tasks.services.tasks import TaskService

TaskServiceDep = Annotated[TaskService, Depends(TaskService)]
CategoryServiceDep = Annotated[CategoryService, Depends(CategoryService)]
