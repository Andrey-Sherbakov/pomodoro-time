from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    name: str
    pomodoro_count: int | None = None
    category_id: int | None = None


class TaskDb(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass
