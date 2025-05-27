from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
async def get_all_tasks() -> dict:
    return {"message": "all tasks"}


@router.post("/")
async def create_task() -> dict:
    return {"message": "task is created"}
