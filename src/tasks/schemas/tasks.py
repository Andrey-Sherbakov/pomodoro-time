from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    name: str
    pomodoro_count: int | None = None
    category_id: int | None = None


class TaskDb(TaskBase):
    id: int
    creator_id: int | None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass


class TaskDeleteResponse(BaseModel):
    detail: str = "Task successfully deleted"
