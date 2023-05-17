from __future__ import annotations #allows self referencing classes
from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: str

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    owner_id: str
    response_to: int | None = None
    content: str
    picture: int | None = None
    

class Post(PostBase):
    id: int
    like_count : int
    class Config:
        orm_mode = True

class PostCreate(PostBase):
    pass


class UserBase(BaseModel): #common data while creating or reading data!
    email: str
    name: str
    intro: str
    birthday: str

class UserCreate(UserBase): 
    password: str

class User(UserBase): #these are for reading data!
    posts: list[Post] = []
    items: list[Item] = [] #uses lazy eval!
    class Config: #.. because it is told here to do so! And also will know that this is not a dict, but an orm model to read out!
        orm_mode = True





