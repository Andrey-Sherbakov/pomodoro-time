from fastapi import APIRouter, status

from src.tasks.dependencies import TaskServiceDep
from src.tasks.schemas import DbTask, CreateTask

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[DbTask])
async def get_all_tasks(service: TaskServiceDep) -> list[DbTask]:
    return await service.get_all()


@router.post("/", response_model=DbTask, status_code=status.HTTP_201_CREATED)
async def create_task(new_task: CreateTask, service: TaskServiceDep) -> DbTask:
    return await service.create(new_task)


@router.get("/{task_id}", response_model=DbTask)
async def get_one_task(task_id: int, service: TaskServiceDep) -> DbTask:
    return await service.get_by_id(task_id)


@router.put("/{task_id}", response_model=DbTask)
async def update_task(task_id: int, updated_task: CreateTask, service: TaskServiceDep) -> DbTask:
    return await service.update_by_id(task_id, updated_task)


@router.delete("/{task_id}", response_model=DbTask)
async def delete_task(task_id: int, service: TaskServiceDep) -> DbTask:
    return await service.delete_by_id(task_id)
