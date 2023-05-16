from pydantic import BaseModel, EmailStr


# schema of user post requests
class PostSchema(BaseModel):
    id: int 
    title: str
    content: str
    poster: str

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class UserSchema(BaseModel):
    fullname : str
    email : EmailStr
    password : str

class UserLoginSchema(BaseModel):
    email : EmailStr
    password : str


