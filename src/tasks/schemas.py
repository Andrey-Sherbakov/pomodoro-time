from pydantic import BaseModel


class Task(BaseModel):
    name: str
    pomodoro_count: int
    category_id: int | None = None


class DbTask(Task):
    id: int


class CreateTask(Task):
    pass
