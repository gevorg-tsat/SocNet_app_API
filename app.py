from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from db.crud import authenticate_user, create_access_token, get_current_active_user, get_db
from db.utils import ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
import uvicorn
from datetime import timedelta

from db import crud, models, schema
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"]
)

HOST="0.0.0.0"
PORT=8081


@app.get("/")
async def root():
    return RedirectResponse(f"http://{HOST}:{PORT}/docs")


@app.post("/user/", response_model=schema.User)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=list[schema.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


@app.get("/user/", response_model=schema.User)
def read_user(current_user : schema.User = Depends(get_current_active_user)):
    return current_user


# @app.post("/users/{user_id}/posts/", response_model=schema.Post)
# def create_post_for_user(
#     user_id: int, post: schema.PostCreate, db: Session = Depends(get_db)
# ):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return crud.create_user_post(db=db, post=post, user_id=user_id)


# @app.get("/posts/", response_model=list[schema.Post])
# def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     posts = crud.get_posts(db, skip=skip, limit=limit)
#     return posts

# @app.post("/posts/{post_id}/like", response_model=schema.Like)
# def like_post(
#     post_id : int, like : schema.LikeCreateOrUpdate,  db: Session = Depends(get_db)
# ):
#     post = db.query(models.Post).filter(models.Post.id == post_id).first()
#     if post is None:
#         raise HTTPException(status_code=404, detail="Post not found")
#     if post.id == like.user_id:
#         raise HTTPException(status_code=400, detail="You can't evaluate your own post")
#     post_like = crud.like_dislike_post(db=db, post_id=post_id, like_post=like)
#     return post_like

@app.post("/token", response_model=schema.Token)
async def login_for_access_token(form_data : OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate" : "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub" : user.email}, expires_delta=access_token_expires)
    return schema.Token(access_token=access_token, token_type="bearer")

if __name__ == "__main__":
    uvicorn.run("app:app", port=PORT, host=HOST, reload=False)