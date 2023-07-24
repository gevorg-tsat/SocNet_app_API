from sqlalchemy.orm import Session
from . import models, schema
from .utils import hash_password, verify_password, JWT_SECRET_KEY, ALGORITHM, oauth_2_scheme
from datetime import timedelta
from datetime import datetime
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


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, fullname=user.fullname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def like_dislike_post(db: Session, post_id : int, like_post : schema.LikeCreateOrUpdate):
    db_post = models.Like(**like_post.model_dump(), post_id=post_id)
    try:
        db.add(db_post)
    except BaseException as error:
        return {"error": error}
    db.commit()
    db.refresh(db_post)
    return db_post

def create_user_post(db: Session, post: schema.PostCreate, user_id: int):
    
    db_post = models.Post(**post.model_dump(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def authenticate_user(db : Session, email : str, password : str):
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def create_access_token(data : dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db : Session = Depends(get_db), token : str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate" : "Bearer"})
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email : str = payload.get("sub")
        if email is None:
            raise credential_exception 
        
        token_data = TokenData(email=email)
    except JWTError:
        raise credential_exception
    
    user = get_user_by_email(db=db, email=email)
    if user is None:
        raise credential_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user