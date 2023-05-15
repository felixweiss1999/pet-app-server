from pydantic import BaseModel, Field, EmailStr


# schema of user post requests
class PostSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(default=None)
    content: str = Field(default=None)
    class Config:
        schema_extra = {
            "post_demo" : {
                "title" : "some title about animals",
                "content" : "some content"
            }
        }

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
