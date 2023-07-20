from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    description: str | None = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    items: list[Post] = []

    class Config:
        orm_mode = True
