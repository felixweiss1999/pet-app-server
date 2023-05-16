from fastapi import FastAPI, Body, Depends, Request
from app.model import PostSchema, UserLoginSchema, UserSchema
from app.auth.jwt_handler import signJWT 
from app.auth.jwt_bearer import jwtBearer
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

#retrieve posts by id
@app.get("/posts/{id}", tags=["posts"])
def get_post_by_id(id: int):
    if id > len(posts) or id < 0:
        return {"error" : "Post with this ID does not exist!"}
    for post in posts:
        if post["id"] == id:
            return {"data" : post}
    return {"error" : "Post not found!"}

#post a postc
@app.post("/posts", dependencies=[Depends(jwtBearer())], tags=["posts"]) # remove dependency for production!
async def add_post(post: PostSchema, request : Request):
    extractor = jwtBearer()
    confirmeduid : str = await extractor(request=request)
    if post.poster != confirmeduid:
        return {"error" : f"Only able to post as {confirmeduid}!"}
    post.id = len(posts) + 1
    posts.append(post.dict())
    return {"info" : "post added", "id" : post.id}

#user signup - create new user
@app.post("/user/signup", tags=["user"])
def user_signup(user: UserSchema = Body(default=None)): #!!! lookup what this Body thing is in docs!
    users.append(user)
    return signJWT(user.email)

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False
    
@app.post("/user/login", tags=["user"])
def user_login(user: UserLoginSchema = Body()):
    if check_user(user):
        return signJWT(user.email)
    else:
        return {"error" : "Invalid login details!"}