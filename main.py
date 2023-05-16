from fastapi import FastAPI, Body, Depends, Request, HTTPException
from app.model import PostSchema, UserLoginSchema, UserSchema
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
@app.get("/posts", tags=["posts"])
def get_posts():
    return {"data" : posts}

#retrieve posts by id
@app.get("/posts/{id}", tags=["posts"])
def get_post_by_id(id: int):
    if id > len(posts) or id < 0:
        return {"error" : "Post with this ID does not exist!"}
    for post in posts:
        if post["id"] == id:
            return {"data" : post}
    return {"error" : "Post not found!"}

#post a post
@app.post("/posts", dependencies=[Depends(jwtBearer())], tags=["posts"]) # remove dependency for production!
async def add_post(post: PostSchema, request : Request):
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if post.poster != confirmeduid:
        return {"error" : f"Only able to post as {confirmeduid}!"}
    if not any(user.email == confirmeduid for user in users):
        return {"error" : f"Unable to post as nonexistent user!"}

    post.id = len(posts) + 1
    posts.append(post.dict())
    return {"info" : "post added", "id" : post.id}





#user signup - create new user
@app.post("/user/signup", tags=["user"], response_model=schemas.User)
def user_signup(user: schemas.UserCreate, db: Session = Depends(get_db)): #!!! lookup what this Body thing is in docs!
    db_user = crud.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists!")
    return crud.create_user(db=db, user=user) #for this to work response model must be declared!
    
@app.post("/user/login", tags=["user"])
def user_login(user: schemas.UserCreate, db: Session = Depends(get_db)): #UserCreate has password!
    db_user = crud.get_user(db, email=user.email)
    if db_user:
        return signJWT(user.email)
    raise HTTPException(status_code=403, detail="Invalid login credentials!")

#depending on who is logged in, return full info or only public info
@app.get("/user/{user_id}", response_model=schemas.User) #User does not contain password!
async def read_user(user_id: str, db: Session = Depends(get_db)):
    # useMeToExtract = jwtBearer()
    # confirmeduid : str = await useMeToExtract(request=request)
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user