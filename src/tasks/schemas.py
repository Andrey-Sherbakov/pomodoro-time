from pydantic import BaseModel, ConfigDict


class Task(BaseModel):
    name: str
    pomodoro_count: int | None = None
    category_id: int | None = None


class DbTask(Task):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CreateTask(Task):
    pass
