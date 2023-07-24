from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Constraint, UniqueConstraint, PrimaryKeyConstraint, CheckConstraint
from sqlalchemy.orm import relationship, validates

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    fullname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="owner")
    # likes = relationship("Like", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="posts")
    # likes = relationship("Like", back_populates="post")

class Like(Base):
    __tablename__ = "likes"
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    like = Column(Boolean)
    __table_args__ = (PrimaryKeyConstraint("user_id", "post_id"), )
    user = relationship("User")
    post = relationship("Post")
