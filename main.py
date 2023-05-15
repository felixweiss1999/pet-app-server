from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from app.model import PostSchema

app = FastAPI()

posts = [
    {
        "id" : 1,
        "title" : "penguins",
        "text" : "penguins are blabla"
    },
    {
        "id" : 2,
        "title" : "elephant",
        "text" : "elephants like trees"
    },
    {
        "id" : 3,
        "title" : "lions",
        "text" : "lions be lyin'"
    }
]

users = []



app = FastAPI()


@app.get("/")
def greet():
    return {"Hello", "World"}

#retrieve all posts
@app.get("/posts", tags=["posts"])
def get_posts():
    return {"data" : posts}

#retrieve pots by id
@app.get("/posts/{id}", tags=["posts"])
def get_post_by_id(id: int):
    if id > len(posts) or id < 0:
        return {"error" : "Post with this ID does not exist!"}
    for post in posts:
        if post["id"] == id:
            return {"data" : post}
    return {"error" : "Post not found!"}

#post a post
@app.post("/posts", tags=["posts"])
def add_post(post: PostSchema):
    post.id = len(posts) + 1
    posts.append(post.dict())
    return {"info" : "pots added"}



"""
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id : int):
    return {"item_id": item_id}

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
"""