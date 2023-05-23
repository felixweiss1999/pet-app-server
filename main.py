from fastapi import FastAPI, Depends, Request, HTTPException, UploadFile
from app.auth.jwt_handler import signJWT 
from app.auth.jwt_bearer import jwtBearer
from sqlalchemy.orm import Session
from app.sql import models, crud, schemas
from app.sql.database import SessionLocal, engine
from fastapi.responses import FileResponse
import aiofiles, mimetypes
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

@app.get("/posts/{post_id}", tags=["posts"], response_model=schemas.Post)
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

@app.get("/posts/{post_id}/replies", tags=["posts"], response_model=list[schemas.Post])
def get_replies_to_post(postid : int, db: Session = Depends(get_db)):
    return crud.get_post_replies(db=db, postid=postid)

@app.post("/posts", dependencies=[Depends(jwtBearer())], tags=["posts"], response_model=schemas.Post) # remove dependency for production!
async def add_post(post: schemas.PostCreate, request : Request, db: Session = Depends(get_db)):
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if post.owner_id != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot post as someone else!")
    if post.response_to != 0 and crud.get_post_by_id(db=db, id=post.response_to) is None:
        raise HTTPException(status_code=404, detail="Cannot respond to nonexisting post!")
    db_user = crud.get_user_by_email(db=db,email=post.owner_id)
    if db_user is None:
        raise HTTPException(status_code=403, detail="User does not exist!")
    return crud.create_post(db=db, post=post)

@app.post("/posts/{post_id}/file", dependencies=[Depends(jwtBearer())], tags=["posts"])
async def add_file_to_post(post_id: int, fileending: str, file: UploadFile, request : Request, db: Session = Depends(get_db)):
    #check if post exists
    post = crud.get_post_by_id(db=db, id=post_id)
    if post == None:
        raise HTTPException(status_code=404, detail="Post does not exist!")
    #check if post owner is currently logged-in user
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if post.owner_id != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot upload file for post of someone else!")
    
    db_file = crud.create_file(db=db,file=schemas.FileCreate(post=post_id, file_ending=fileending))
    crud.set_filepath(db=db, fileid=db_file.id, filepath=f"files/{db_file.id}.{db_file.file_ending}")
    try:
        async with aiofiles.open(f"files/{db_file.id}.{db_file.file_ending}", 'wb') as out_file:
            content = file.file.read()  # async read
            await out_file.write(content)  # async write
    except Exception as e:
        print(e)
        crud.delete_file(db=db, fileid=db_file.id)
        raise HTTPException(status_code=404, detail="Error when storing file! Make sure there is a 'files' folder in the working directory!")
    await file.close()
    return {"id": db_file.id}

@app.get("/posts/{post_id}/file", response_class=FileResponse, tags=["posts"]) #FileResponse will handle everything from just returning the path to the file!
async def get_file_by_post(post_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_post_by_id(db=db, id=post_id).files
    if db_file[-1] is None:
        raise HTTPException(status_code=404, detail="Post does not have any files")
    mimetype = mimetypes.guess_type(db_file[-1].file_path)[0]
    print(mimetype)
    if mimetypes is None:
        return FileResponse(path=db_file[-1].file_path)
    return FileResponse(path=db_file[-1].file_path, content_disposition_type=mimetype)




#user 

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
    db_user = crud.get_user_by_email(db, email=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/user/{user_id}/profile_picture", dependencies=[Depends(jwtBearer())], tags=["user"])
async def upload_profile_picture(user_id: str, fileending: str, file: UploadFile, request : Request, db: Session = Depends(get_db)):
    #check if post owner is currently logged-in user
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if user_id != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot upload profile picture of someone else!")
    
    db_file = crud.create_file(db=db,file=schemas.FileCreate(post=None, file_ending=fileending, user=user_id))
    crud.set_filepath(db=db, fileid=db_file.id, filepath=f"files/{db_file.id}.{db_file.file_ending}")
    try:
        async with aiofiles.open(f"files/{db_file.id}.{db_file.file_ending}", 'wb') as out_file:
            content = file.file.read()  # async read
            await out_file.write(content)  # async write
    except Exception as e:
        print(e)
        crud.delete_file(db=db, fileid=db_file.id)
        raise HTTPException(status_code=404, detail="Error when storing file! Make sure there is a 'files' folder in the working directory!")
    await file.close()
    return {"id": db_file.id}

@app.get("/user/{user_id}/profile_picture", response_class=FileResponse, tags=["user"]) #FileResponse will handle everything from just returning the path to the file!
async def get_profile_picture(user_id: str, db: Session = Depends(get_db)):
    db_file = crud.get_filename_by_user(db=db, userid=user_id)
    if db_file[-1] is None:
        raise HTTPException(status_code=404, detail="User does not have a profile picture!")
    mimetype = mimetypes.guess_type(db_file[-1].file_path)[0]
    print(mimetype)
    if mimetypes is None:
        return FileResponse(path=db_file[-1].file_path)
    return FileResponse(path=db_file[-1].file_path, content_disposition_type=mimetype)







#file

@app.get("/file/{file_id}", response_class=FileResponse, tags=["file"]) #FileResponse will handle everything from just returning the path to the file!
async def get_file_by_id(file_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_filename_by_id(db=db, fileid=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    mimetype = mimetypes.guess_type(db_file.file_path)[0]
    print(mimetype)
    if mimetypes is None:
        return FileResponse(path=db_file.file_path)
    return FileResponse(path=db_file.file_path, content_disposition_type=mimetype)





# chat: send message, add file to message

@app.post("/chat/create", tags=["chat"], dependencies=[Depends(jwtBearer())], response_model=schemas.Chat)
async def create_chat(chat: schemas.ChatCreate, request: Request, db: Session = Depends(get_db)):
    if chat.user1 == chat.user2:
        raise HTTPException(status_code=404, detail="Cannot create chat to oneself!")
    if crud.get_user_by_email(db=db, email=chat.user1) == None or crud.get_user_by_email(db=db, email=chat.user2) == None:
        raise HTTPException(status_code=404, detail="One of the users does not exist!")
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if chat.user1 != confirmeduid and chat.user2 != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot open chat for someone else!")
    if crud.get_chats_by_user(db=db, uid=chat.user1, uid2=chat.user2) != []:
        print(crud.get_chats_by_user(db=db, uid=chat.user1, uid2=chat.user2))
        raise HTTPException(status_code=404, detail="Error: Chat already exists!")
    return crud.create_chat(db=db, chat=chat) 

@app.get("/{user_id}/chats", tags=["chat"], dependencies=[Depends(jwtBearer())], response_model=list[schemas.Chat])
async def get_chats_by_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if user_id != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot get chats of someone else!")
    return crud.get_chats_by_user(db=db, uid=user_id)

@app.get("/{chat_id}/messages", tags=["chat"], dependencies=[Depends(jwtBearer())], response_model=list[schemas.Message])
async def get_messages_by_chat(chat_id: int, request: Request, db: Session = Depends(get_db)):
    db_chat = crud.get_chat_by_id(db=db, chatid=chat_id)
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if db_chat.user1 != confirmeduid and db_chat.user2 != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot get messages of someone elses chat!")
    return db_chat.messages

