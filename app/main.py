from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth


# Create databse for postgres
models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg.connect(host = 'localhost', dbname = 'fastapi', row_factory=dict_row,
                               user = 'postgres', password = '123', port = '5432')
        cur = conn.cursor()
        print("Database connection was succesful!")
        break
    except Exception as error:
        print("connecting to database failed")
        print("Error: ", error)
        time.sleep(3)


# Hard coded data for demo, stored in memory
my_posts = [{"title":"title of post 1", "content": "content of post 1", "id": 1},
            {"title":"favorite foods", "content": "I like pizza", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Welcome to my new api"}


@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {"details": post}