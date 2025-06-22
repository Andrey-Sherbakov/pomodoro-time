from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo


class BaseUser(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    full_name: str | None = Field(None, max_length=100)
    age: int | None = Field(None, ge=18, le=99)


class UserCreate(BaseUser):
    password: str
    password_confirm: str

    @field_validator("password_confirm")
    def password_match(cls, v, info: ValidationInfo):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserToDb(BaseUser):
    hashed_password: str
    is_admin: bool = False


class UserDb(BaseUser):
    id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=100)
    age: int | None = Field(None, ge=18, le=99)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UserUpdate":
        if not any([self.username, self.email, self.full_name, self.age]):
            raise ValueError("At least one field must be provided")
        return self


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password_confirm")
    def password_match(cls, v, info: ValidationInfo):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class EmailBody(BaseModel):
    subject: str
    message: str
    recipients: list[EmailStr]


class PasswordUpdateResponse(BaseModel):
    detail: str = "Password successfully updated, please login again"


class UserDeleteResponse(BaseModel):
    detail: str = "User successfully deleted"
