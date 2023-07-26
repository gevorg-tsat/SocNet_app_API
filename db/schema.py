from pydantic import BaseModel
from typing import Optional, Literal
import enum
from datetime import datetime

class Status(BaseModel):
    status : Literal["ok", "error"]

class PostBase(BaseModel):
    description: str

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : str | None = None

class PostCreate(PostBase):
    pass

class PostEdit(PostBase):
    pass

class Post(PostBase):
    id : int
    create_date : Optional[datetime]
    last_update_date : Optional[datetime]

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    fullname: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    posts: list[Post] = []
    is_active : bool
    class Config:
        from_attributes = True

class PostWithLikes(Post):
    author_username : str
    likes : int
    dislikes : int

class LikeBase(BaseModel):
    like : bool = True

class LikeCreateOrUpdate(LikeBase):
    pass


class LikeCreate(LikeBase):
    post_id : int

class Like(LikeBase):
    post_info : Post