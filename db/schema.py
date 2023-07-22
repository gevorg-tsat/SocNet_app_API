from pydantic import BaseModel


class PostBase(BaseModel):
    description: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    fullname: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    posts: list[Post] = []
    class Config:
        from_attributes = True

class LikeBase(BaseModel):
    user_id : int
    like : bool = True

class LikeCreateOrUpdate(LikeBase):
    pass


class Like(LikeBase):
    post_id : int