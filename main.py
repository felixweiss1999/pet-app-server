from fastapi import FastAPI, Depends, Request, HTTPException, UploadFile
from app.auth.jwt_handler import signJWT 
from app.auth.jwt_bearer import jwtBearer
from sqlalchemy.orm import Session
from app.sql import models, crud, schemas
from app.sql.database import SessionLocal, engine
from fastapi.responses import FileResponse
import aiofiles
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# uvicorn main:app --reload


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

#posts
@app.get("/posts", tags=["posts"], response_model=list[schemas.Post])
def get_all_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_posts(db=db, skip=skip, limit=limit)

@app.get("/posts/{id}", tags=["posts"], response_model=schemas.Post)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post_by_id(db=db, id=id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found!")
    return db_post

@app.get("/user/{user_id}/posts", tags=["posts"], response_model=list[schemas.Post])
def get_post_by_userid(user_id : str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found!")
    return db_user.posts

@app.get("/posts/{id}/replies", tags=["posts"], response_model=list[schemas.Post])
def get_replies_to_post(postid : int, db: Session = Depends(get_db)):
    return crud.get_post_replies(db=db, postid=postid)

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

@app.get("/user/{user_id}", response_model=schemas.User, tags=["user"]) #User does not contain password!
async def get_user_by_email(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user




#file
@app.get("/file/{file_id}", response_class=FileResponse, tags=["file"])
async def get_file_by_id(file_id: int, db: Session = Depends(get_db)):
    db_filename = crud.get_filename_by_id(db=db, fileid=file_id)
    if db_filename is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_filename

@app.post("/file", tags=["file"])
async def create_file(post_id: int, file: UploadFile, db: Session = Depends(get_db)):
    # create db entry, then write to disk using id as filename
    db_file = crud.create_file(db=db,file=schemas.FileCreate(post=post_id))
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await in_file.read()  # async read
        await out_file.write(content)  # async write
    return {"id": file.filename}