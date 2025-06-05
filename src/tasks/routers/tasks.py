from fastapi import APIRouter, status

from src.tasks.dependencies import TaskServiceDep
from src.tasks.schemas import TaskCreate, TaskDb

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskDb])
async def get_all_tasks(service: TaskServiceDep) -> list[TaskDb]:
    return await service.get_all()


@router.post("/", response_model=TaskDb, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, service: TaskServiceDep) -> TaskDb:
    return await service.create(body)


@router.get("/{task_id}", response_model=TaskDb)
async def get_one_task(task_id: int, service: TaskServiceDep) -> TaskDb:
    return await service.get_by_id(task_id)


@router.put("/{task_id}", response_model=TaskDb)
async def update_task(task_id: int, body: TaskCreate, service: TaskServiceDep) -> TaskDb:
    return await service.update_by_id(task_id, body)


@router.delete("/{task_id}", response_model=TaskDb)
async def delete_task(task_id: int, service: TaskServiceDep) -> TaskDb:
    return await service.delete_by_id(task_id)


@router.get("/category/{cat_id}", response_model=list[TaskDb])
async def get_tasks_by_category(cat_id: int, service: TaskServiceDep) -> list[TaskDb]:
    return await service.get_tasks_by_category(cat_id)
