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


class UserBase(BaseModel): #common data while creating or reading data!
    email: str

class UserCreate(UserBase): 
    password: str

class User(UserBase): #these are for reading data!
    is_active: bool
    items: list[Item] = [] #uses lazy eval!

    class Config: #.. because it is told here to do so! And also will know that this is not a dict, but an orm model to read out!
        orm_mode = True