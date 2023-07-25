from sqlalchemy.orm import Session
from . import models, schema
from .utils import hash_password, verify_password, JWT_SECRET_KEY, ALGORITHM, oauth_2_scheme
from datetime import timedelta
import datetime
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.exceptions import HTTPException
from .schema import TokenData, User
from db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()



def create_user(db: Session, user: schema.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, fullname=user.fullname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_posts(username: str, db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.username == username).first().posts

def like_dislike_post(db: Session, post_id : int, user_id : int, like : schema.LikeEnum):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id == user_id:
        raise HTTPException(status_code=400, detail="You can't like your own post")
    db_like = models.Like(post_id=post_id, user_id=user_id,
                          like = True if like == schema.LikeEnum.LIKE else False)
    q = db.query(models.Like).filter(models.Like.post_id == post_id, models.Like.user_id == user_id)
    if q is None:
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like
    else:
        post_eval = q.one()
        post_eval.like = True if like == schema.LikeEnum.LIKE else False
        db.commit()
        return post_eval
        

def create_user_post(db: Session, post: schema.PostCreate, user_id: int):
    db_post = models.Post(**post.model_dump(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def edit_post(db: Session, post_id : int, post: schema.PostEdit, user_id : int):
    q = db.query(models.Post).filter(models.Post.id == post_id)
    if q.first() is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if q.first().owner_id != user_id:
        raise HTTPException(status_code=403, detail="You can edit only your own posts")
    post_from_db = q.one()
    post_from_db.description = post.description
    post_from_db.last_update_date = datetime.datetime.utcnow()
    db.commit()
    return post_from_db

def delete_post(db : Session, post_id : int, user_id : int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != user_id:
        raise HTTPException(status_code=403, detail="You can delete only your own posts")
    db.query(models.Like).filter(models.Like.post_id == post.id).delete(synchronize_session=False)
    db.delete(post)
    db.commit()
    return schema.Status(status="ok")

def authenticate_user(db : Session, username : str, password : str):
    user = get_user_by_username(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def create_access_token(data : dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db : Session = Depends(get_db), token : str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate" : "Bearer"})
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credential_exception 
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credential_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user