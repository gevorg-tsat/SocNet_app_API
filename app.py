from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from db.crud import authenticate_user, create_access_token, get_current_active_user, \
get_db, edit_post, delete_post, get_user_by_username, get_post_by_id, delete_like
from db.utils import ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
import uvicorn
from datetime import timedelta

from db import crud, models, schema
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "posts",
        "description": "Manage posts: create, edit, delete, like, dislike, etc."
    },
]

app = FastAPI(openapi_tags=tags_metadata)

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


@app.post("/user/", response_model=schema.User, tags=["users"])
async def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    return crud.create_user(db=db, user=user)



@app.get("/user/", response_model=schema.User, tags=["users"])
async def read_current_user_info(current_user : schema.User = Depends(get_current_active_user)):
    return current_user

@app.get("/user/{username}", tags=["users"])
async def read_user_info_by_username(username : str, current_user : schema.User = Depends(get_current_active_user),
                                      db: Session = Depends(get_db)):
    return get_user_by_username(db=db, username=username)

@app.post("/posts/", response_model=schema.Post, tags=["posts"])
async def create_post_for_user(
    post: schema.PostCreate, current_user : schema.User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    return crud.create_user_post(db=db, post=post, user_id=current_user.id)


@app.get("/user/{username}/posts/", response_model=list[schema.Post], tags=["posts"])
async def read_posts(username : str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(username=username, db=db, skip=skip, limit=limit)
    return posts

@app.get("/posts/{post_id}", response_model=schema.PostWithLikes, tags=["posts"])
async def read_post_by_id(post_id : int, db: Session = Depends(get_db), current_user : schema.User = Depends(get_current_active_user)):
    post = get_post_by_id(post_id=post_id, db=db)
    return post


@app.get("/posts/", response_model=list[schema.Post], tags=["posts"])
async def read_my_posts(current_user : schema.User = Depends(get_current_active_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(username=current_user.username, db=db, skip=skip, limit=limit)
    return posts

@app.post("/posts/{post_id}/like", response_model=schema.PostWithLikes, tags=["posts"])
async def like_post(
    post_id : int, current_user : schema.User = Depends(get_current_active_user),
    is_like : bool = Query(default=True),  db: Session = Depends(get_db)
):
    post_like = crud.like_dislike_post(db=db, post_id=post_id, user_id = current_user.id, like=is_like)
    return post_like

@app.post("/token", response_model=schema.Token, tags=["posts"])
async def login_for_access_token(form_data : OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate" : "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data = {"sub" : user.username}, expires_delta=access_token_expires)
    return schema.Token(access_token=access_token, token_type="bearer")

@app.put("/posts/{post_id}", response_model=schema.Post, tags=["posts"])
async def edit_my_post(post_id : int, new_post : schema.PostEdit,
                       current_user : schema.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    post = edit_post(db=db, post_id=post_id, post=new_post, user_id = current_user.id)
    return post

@app.delete("/posts/{post_id}", response_model=schema.Status, tags=["posts"])
async def delete_my_post(post_id : int,
        current_user : schema.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)):
    status = delete_post(db=db, post_id=post_id, user_id=current_user.id)
    return status
    
@app.delete("/posts/{post_id}/like", response_model=schema.Status, tags=["posts"])
async def delete_my_post_evaluation(post_id : int,
        current_user : schema.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)):
    status = delete_like(db=db, post_id=post_id, user_id=current_user.id)
    return status
    
if __name__ == "__main__":
    uvicorn.run("app:app", port=PORT, host=HOST, reload=False)