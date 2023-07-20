from sqlalchemy.orm import Session
from . import models, schema
from .utils import hash_password, verify_password

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def like_dislike_post(db: Session, user_id: int, post_id : int, like: bool = True):
    db_item = models.Like(user_id = user_id, post_id=post_id, like=like)
    try:
        db.add(db_item)
    except BaseException as error:
        return {"error": error}
    db.commit()
    db.refresh(db_item)
    return db_item

def create_user_post(db: Session, item: schema.PostCreate, user_id: int):
    db_item = models.Post(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
