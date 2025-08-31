from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None # Optional value


my_posts = [{"title":"title of post 1", "content": "content of post 1", "id": 1},
            {"title":"favorite foods", "content": "I like pizza", "id": 2}]


@app.get("/")
async def root():
    return {"message": "Welcome to my new api"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts")
def create_posts(post: Post):
    # print(post.rating)
    # print(post.model_dump())  # .dict() method is deprecated
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 100000000)
    my_posts.append(post_dict)
    return  {"data": post_dict}
# title str, content str


@app.get("/posts/{id}")
def get_post(id):
    print(id)
    return {"post details": f"Here is post {id}"}
    