from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryDb(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryDeleteResponse(BaseModel):
    detail: str = "Category successfully deleted"
