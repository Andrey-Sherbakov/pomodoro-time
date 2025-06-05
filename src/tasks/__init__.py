from fastapi import APIRouter

from src.tasks.routers import category_router, task_router

tasks_router = APIRouter()

tasks_router.include_router(task_router)
tasks_router.include_router(category_router)
