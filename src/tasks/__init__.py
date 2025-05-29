from typing import Annotated

from fastapi import Depends

from src.tasks.dependencies import get_category_service, get_tasks_service
from src.tasks.services import CategoryService, TaskService

CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_tasks_service)]
