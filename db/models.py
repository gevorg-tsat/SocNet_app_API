from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Constraint, \
UniqueConstraint, PrimaryKeyConstraint, CheckConstraint, DateTime, Null
from sqlalchemy.orm import relationship, validates
from fastapi.exceptions import HTTPException
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    fullname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="owner")
    likes = relationship("Like", back_populates="user_info")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    create_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_update_date = Column(DateTime, nullable=True)
    owner = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post_info")

class Like(Base):
    __tablename__ = "likes"
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    like = Column(Boolean)
    user_info = relationship("User", back_populates="likes")
    post_info = relationship("Post", back_populates="likes")
    __table_args__ = (PrimaryKeyConstraint("user_id", "post_id"), )
