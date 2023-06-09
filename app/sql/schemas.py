#from __future__ import annotations #allows self referencing classes
from pydantic import BaseModel, EmailStr


class FollowBase(BaseModel):
    follower: str
    follows: str

class Follow(FollowBase):
    timestamp: int
    class Config:
        orm_mode = True

class FollowCreate(FollowBase):
    pass



class LikeBase(BaseModel):
    liker: str
    

class Like(LikeBase):
    timestamp: int
    class Config:
        orm_mode = True

class LikeCreate(LikeBase):
    liked_post: int



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
    attraction: int | None = None
    content: str
    label: str
    

class Post(PostBase):
    id: int
    files: list[File] = []
    likes: list[Like] = []
    timestamp: int
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
    location: str

class UserCreate(UserBase): 
    password: str

class User(UserBase): #these are for reading data!
    posts: list[Post] = []
    pets: list[Pet] = []
    follows: list[Follow] = []
    followed_by: list[Follow] = []
    class Config: #.. because it is told here to do so! And also will know that this is not a dict, but an orm model to read out!
        orm_mode = True

class AttractionBase(BaseModel):
    name: str
    location: str
    lat: float
    lon: float

class AttractionCreate(AttractionBase):
    pass

class Attraction(AttractionBase):
    id: int
    posts: list[Post] = []
    class Config:
        orm_mode = True

