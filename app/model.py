from pydantic import BaseModel, Field, EmailStr


# schema of user post requests
class PostSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(default=None)
    content: str = Field(default=None)
    poster: str = Field(default=None)

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class UserSchema(BaseModel):
    fullname : str = Field(default=None)
    email : EmailStr = Field(default = None)
    password : str = Field(default = None)

class UserLoginSchema(BaseModel):
    email : EmailStr = Field(default = None)
    password : str = Field(default = None)


