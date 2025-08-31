from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None # Optional value


@app.get("/")
async def root():
    return {"message": "Welcome to my new api"}


@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}


@app.post("/creatposts")
def create_posts(new_post: Post):
    print(new_post.rating)
    print(new_post.dict())
    return  {"data": "new post"}
# title str, content str