from fastapi import APIRouter, status

from src.tasks.dependencies import TaskServiceDep
from src.tasks.schemas import TaskCreate, TaskDb, TaskDeleteResponse
from src.users.dependencies import CurrentUserDep

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskDb])
async def get_all_tasks(service: TaskServiceDep) -> list[TaskDb]:
    return await service.get_all()


@router.post("/", response_model=TaskDb, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate, service: TaskServiceDep, current_user: CurrentUserDep
) -> TaskDb:
    return await service.create(body, current_user)


@router.get("/{task_id}", response_model=TaskDb)
async def get_one_task(task_id: int, service: TaskServiceDep) -> TaskDb:
    return await service.get_by_id(task_id)


@router.put("/{task_id}", response_model=TaskDb)
async def update_task(
    task_id: int, body: TaskCreate, service: TaskServiceDep, current_user: CurrentUserDep
) -> TaskDb:
    return await service.update_by_id(task_id, body, current_user)


@router.delete("/{task_id}", response_model=TaskDeleteResponse)
async def delete_task(
    task_id: int, service: TaskServiceDep, current_user: CurrentUserDep
) -> TaskDeleteResponse:
    await service.delete_by_id(task_id, current_user)
    return TaskDeleteResponse()


@router.get("/category/{cat_id}", response_model=list[TaskDb])
async def get_tasks_by_category(cat_id: int, service: TaskServiceDep) -> list[TaskDb]:
    return await service.get_tasks_by_category(cat_id)
