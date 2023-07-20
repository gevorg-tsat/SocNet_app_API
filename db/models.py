from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Constraint, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, validates

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    fullname = Column(String)
    hashed_password = Column(String)

    items = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

class Like(Base):
    __tablename__ = "likes"
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"), Constraint("user_id not in (select owner_id from posts where posts.id=post_id"))
    like = Column(Boolean)
    __table_args__ = PrimaryKeyConstraint("user_id", "post_id")
    user = relationship("User", back_populates="likes")
    post = relationship("User", back_populates="likes")
