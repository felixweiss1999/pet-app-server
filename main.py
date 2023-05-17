from fastapi import FastAPI, Depends, Request, HTTPException
from app.auth.jwt_handler import signJWT 
from app.auth.jwt_bearer import jwtBearer
from sqlalchemy.orm import Session
from app.sql import models, crud, schemas
from app.sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

posts = [
    {
        "id" : 1,
        "title" : "penguins",
        "text" : "penguins are blabla"
    },
    {
        "id" : 2,
        "title" : "elephant",
        "text" : "elephants like trees"
    },
    {
        "id" : 3,
        "title" : "lions",
        "text" : "lions be lyin'"
    }
]


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


@app.get("/")
def greet():
    return {"Hello", "World"}

#retrieve all posts
@app.get("/posts", tags=["posts"], response_model=list[schemas.Post])
def get_all_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_posts(db=db, skip=skip, limit=limit)

#retrieve post by id
@app.get("/posts/{id}", tags=["posts"], response_model=schemas.Post)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post_by_id(db=db, id=id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found!")
    return db_post

#retrieve post by user
@app.get("/user/{user_id}/posts", tags=["posts"], response_model=list[schemas.Post])
def get_post_by_userid(user_id : str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found!")
    return db_user.posts

#retrieve replies to post
@app.get("/posts/{id}/replies", tags=["posts"], response_model=list[schemas.Post])
def get_replies_to_post(postid : int, db: Session = Depends(get_db)):
    return crud.get_post_replies(db=db, postid=postid)

#post a post
@app.post("/posts", dependencies=[Depends(jwtBearer())], tags=["posts"], response_model=schemas.Post) # remove dependency for production!
async def add_post(post: schemas.PostCreate, request : Request, db: Session = Depends(get_db)):
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if post.owner_id != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot post as someone else!")
    db_user = crud.get_user_by_email(db=db,email=post.owner_id)
    if db_user is None:
        raise HTTPException(status_code=403, detail="User does not exist!")
    return crud.create_post(db=db, post=post)





#user signup - create new user
@app.post("/user/signup", tags=["user"], response_model=schemas.User)
def user_signup(user: schemas.UserCreate, db: Session = Depends(get_db)): #!!! lookup what this Body thing is in docs!
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists!")
    return crud.create_user(db=db, user=user) #for this to work response model must be declared!
    
@app.post("/user/login", tags=["user"])
def user_login(user: schemas.UserLogin, db: Session = Depends(get_db)): #UserCreate has password!
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        return signJWT(user.email)
    raise HTTPException(status_code=403, detail="Invalid login credentials!")

@app.get("/user/{user_id}", response_model=schemas.User) #User does not contain password!
async def get_user_by_email(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user