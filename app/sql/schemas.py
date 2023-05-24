#from __future__ import annotations #allows self referencing classes
from pydantic import BaseModel, EmailStr



class LikeBase(BaseModel):
    liker: str
    

class Like(LikeBase):
    class Config:
        orm_mode = True

class LikeCreate(LikeBase):
    liked_post: str



class FileBase(BaseModel):
    file_ending: str
    post: int | None
    user: str | None = None
    message: int | None
    pet: int | None

class File(FileBase):
    id: int
    file_path: str
    class Config:
        orm_mode = True

class FileCreate(FileBase):
    pass
    

class ChatBase(BaseModel):
    user1: str
    user2: str

class Chat(ChatBase):
    id: int
    class Config:
        orm_mode = True

class ChatCreate(ChatBase):
    pass



class MessageBase(BaseModel):
    chat: int
    owner: str
    content: str
    

class Message(MessageBase):
    id: int
    timestamp: int
    files: list[File] = []
    class Config:
        orm_mode = True
    

class MessageCreate(MessageBase):
    pass



class PostBase(BaseModel):
    owner_id: str
    response_to: int | None = None
    content: str
    

class Post(PostBase):
    id: int
    like_count : int
    files: list[File] = []
    likes: list[Like] = []
    class Config:
        orm_mode = True

class PostCreate(PostBase):
    pass






class PetBase(BaseModel):
    owner: str
    name: str
    breed: str
    gender: str
    birthday: str
    personality_labels: str

class Pet(PetBase):
    id: int
    files: list[File] = []
    class Config:
        orm_mode = True

class PetCreate(PetBase):
    pass




class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserBase(BaseModel): #common data while creating or reading data!
    email: EmailStr
    name: str
    intro: str
    birthday: str

class UserCreate(UserBase): 
    password: str

class User(UserBase): #these are for reading data!
    posts: list[Post] = []
    pets: list[Pet] = []
    class Config: #.. because it is told here to do so! And also will know that this is not a dict, but an orm model to read out!
        orm_mode = True



