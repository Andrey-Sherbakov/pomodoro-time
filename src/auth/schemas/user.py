from pydantic import BaseModel, EmailStr, Field, ConfigDict


class BaseUser(BaseModel):
    username: str = Field(min_length=3, max_length=100)


class UserUpdate(BaseUser):
    email: EmailStr
    full_name: str | None = Field(None, max_length=100)
    age: int | None = Field(None, ge=18, le=99)


class UserCreate(UserUpdate):
    password: str


class UserDb(UserUpdate):
    id: int

    model_config = ConfigDict(from_attributes=True)
