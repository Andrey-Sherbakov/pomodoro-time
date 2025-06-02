from fastapi import APIRouter, status

from src.tasks.schemas import TaskDb, TaskCreate
from src.tasks.dependencies import TaskServiceDep

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskDb])
async def get_all_tasks(service: TaskServiceDep) -> list[TaskDb]:
    return await service.get_all()


@router.post("/", response_model=TaskDb, status_code=status.HTTP_201_CREATED)
async def create_task(new_task: TaskCreate, service: TaskServiceDep) -> TaskDb:
    return await service.create(new_task)


@router.get("/{task_id}", response_model=TaskDb)
async def get_one_task(task_id: int, service: TaskServiceDep) -> TaskDb:
    return await service.get_by_id(task_id)


@router.put("/{task_id}", response_model=TaskDb)
async def update_task(task_id: int, updated_task: TaskCreate, service: TaskServiceDep) -> TaskDb:
    return await service.update_by_id(task_id, updated_task)


@router.delete("/{task_id}", response_model=TaskDb)
async def delete_task(task_id: int, service: TaskServiceDep) -> TaskDb:
    return await service.delete_by_id(task_id)


@router.get("/category/{cat_id}", response_model=list[TaskDb])
async def get_tasks_by_category(cat_id: int, service: TaskServiceDep) -> list[TaskDb]:
    return await service.get_tasks_by_category(cat_id)
