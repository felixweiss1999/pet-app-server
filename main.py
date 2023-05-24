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
async def create_post(post: schemas.PostCreate, request : Request, db: Session = Depends(get_db)):
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

@app.post("/posts/{post_id}/file", dependencies=[Depends(jwtBearer())], tags=["posts"], response_model=schemas.File)
async def upload_file_to_post(post_id: int, fileending: str, file: UploadFile, request : Request, db: Session = Depends(get_db)):
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
    return db_file





#user 

@app.post("/user/signup", tags=["user"], response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)): #!!! lookup what this Body thing is in docs!
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists!")
    return crud.create_user(db=db, user=user) #for this to work response model must be declared!
    
@app.post("/user/edit", tags=["user"], dependencies=[Depends(jwtBearer())], response_model=schemas.User)
async def edit_user(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db)): #!!! lookup what this Body thing is in docs!
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if user.email != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot edit profile of someone else!")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User does not exists!")
    return crud.edit_user(db=db, user=user)

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

@app.post("/user/{user_id}/profile_picture", dependencies=[Depends(jwtBearer())], tags=["user"], response_model=schemas.File)
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
    return db_file

@app.get("/user/{user_id}/profile_picture", response_class=FileResponse, tags=["user"]) #FileResponse will handle everything from just returning the path to the file!
async def download_profile_picture(user_id: str, db: Session = Depends(get_db)):
    db_file = crud.get_filename_by_user(db=db, userid=user_id)
    if db_file[-1] is None:
        raise HTTPException(status_code=404, detail="User does not have a profile picture!")
    mimetype = mimetypes.guess_type(db_file[-1].file_path)[0]
    print(mimetype)
    if mimetypes is None:
        return FileResponse(path=db_file[-1].file_path)
    return FileResponse(path=db_file[-1].file_path, content_disposition_type=mimetype)







#file

@app.get("/file/{file_id}", response_class=FileResponse, dependencies=[Depends(jwtBearer())], tags=["file"]) #FileResponse will handle everything from just returning the path to the file!
async def download_file_by_id(file_id: int, request: Request, db: Session = Depends(get_db)):
    db_file = crud.get_filename_by_id(db=db, fileid=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    if db_file.message is not None: #perform security check by getting chat of message of file
        db_message = crud.get_message_by_id(db=db, messageid=db_file.message)
        db_chat = crud.get_chat_by_id(db=db, chatid=db_message.chat)
        useMeToExtract = jwtBearer()
        confirmeduid : str = await useMeToExtract(request=request)
        if db_chat.user1 != confirmeduid and db_chat.user2 != confirmeduid:
            raise HTTPException(status_code=404, detail="Not allowed to get file of other chat!")
    mimetype = mimetypes.guess_type(db_file.file_path)[0]
    if mimetypes is None:
        return FileResponse(path=db_file.file_path)
    return FileResponse(path=db_file.file_path, content_disposition_type=mimetype)





# chat

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

@app.get("/user/{user_id}/chats", tags=["chat"], dependencies=[Depends(jwtBearer())], response_model=list[schemas.Chat])
async def get_chats_by_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if user_id != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot get chats of someone else!")
    return crud.get_chats_by_user(db=db, uid=user_id)

@app.get("/chat/{chat_id}/messages", tags=["chat"], dependencies=[Depends(jwtBearer())], response_model=list[schemas.Message])
async def get_messages_by_chat(chat_id: int, request: Request, db: Session = Depends(get_db)):
    db_chat = crud.get_chat_by_id(db=db, chatid=chat_id)
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if db_chat.user1 != confirmeduid and db_chat.user2 != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot get messages of someone elses chat!")
    return db_chat.messages

@app.post("/chat/sendmsg", tags=["chat"], dependencies=[Depends(jwtBearer())], response_model=schemas.Message)
async def send_message(msg: schemas.MessageCreate, request: Request, db: Session = Depends(get_db)):
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if msg.owner != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot send message as someone else!")
    db_chat = crud.get_chat_by_id(db=db, chatid=msg.chat)
    if db_chat is None:
        raise HTTPException(status_code=404, detail="Chat does not exist!")
    if db_chat.user1 != msg.owner and db_chat.user2 != msg.owner:
        raise HTTPException(status_code=400, detail="Cannot send message in someone elses chat!")
    return crud.create_message(db=db, message=msg)

@app.post("/chat/{message_id}/file", dependencies=[Depends(jwtBearer())], tags=["chat"], response_model=schemas.File)
async def add_file_to_message(message_id: int, fileending: str, file: UploadFile, request : Request, db: Session = Depends(get_db)):
    #check if message exists
    db_message = crud.get_message_by_id(db=db,messageid=message_id)
    if db_message == None:
        raise HTTPException(status_code=404, detail="Message does not exist!")
    #check if message owner is currently logged-in user
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if db_message.owner != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot upload file for message of someone else!")
    
    db_file = crud.create_file(db=db,file=schemas.FileCreate(message=message_id, file_ending=fileending))
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
    return db_file


#pet:
@app.post("/pet/createOrEdit", tags=["pet"], dependencies=[Depends(jwtBearer())], response_model=schemas.Pet)
async def create_or_edit_pet(pet: schemas.PetCreate, request: Request, db: Session = Depends(get_db), pet_id: int = None):
    if crud.get_user_by_email(db=db, email=pet.owner) == None:
        raise HTTPException(status_code=404, detail="Owner does not exist!")
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if pet.owner != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot create or edit someone elses pet!")
    if pet_id is not None: 
        if crud.get_pet_by_id(db=db, petid=pet_id) is not None:
            return crud.edit_pet(db=db, pet=pet, petid=pet_id)
        raise HTTPException(status_code=404, detail="Trying to edit nonexistent pet!")
    return crud.create_pet(db=db, pet=pet) 

@app.get("/user/{user_id}/pets", tags=["pet"], response_model=list[schemas.Pet])
async def get_pets_by_user(user_id: str, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db=db, email=user_id) is None:
        raise HTTPException(status_code=403, detail="User does not exist!")
    return crud.get_user_by_email(db=db, email=user_id).pets


@app.post("/pet/{pet_id}/file", dependencies=[Depends(jwtBearer())], tags=["pet"], response_model=schemas.File)
async def upload_file_to_pet(pet_id: int, fileending: str, file: UploadFile, request : Request, db: Session = Depends(get_db)):
    #check if pet exists
    db_pet = crud.get_pet_by_id(db=db,petid=pet_id)
    if db_pet == None:
        raise HTTPException(status_code=404, detail="Pet does not exist!")
    #check if message owner is currently logged-in user
    useMeToExtract = jwtBearer()
    confirmeduid : str = await useMeToExtract(request=request)
    if db_pet.owner != confirmeduid:
        raise HTTPException(status_code=403, detail="Cannot upload file for pet of someone else!")
    
    db_file = crud.create_file(db=db,file=schemas.FileCreate(pet=pet_id, file_ending=fileending))
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
    return db_file

