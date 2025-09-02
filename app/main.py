from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None # Optional value


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


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status":"success"}


@app.get("/posts")
def get_posts():
    cur.execute("""SELECT * FROM posts;""")
    posts = cur.fetchall()
    # print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # # print(post.rating)
    # # print(post.model_dump())  # .dict() method is deprecated
    # post_dict = post.model_dump()
    # post_dict['id'] = randrange(0, 100000000)
    # my_posts.append(post_dict)
    cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING* """, 
                (post.title, post.content, post.published))
    new_post = cur.fetchone()
    conn.commit() # push and stage changes
    return  {"data": new_post}


@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {"details": post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cur.execute("""SELECT * FROM posts WHERE id = %s""",(str(id),))
    post = cur.fetchone()
    if not post:
        # --------- handling no-exiting post ids: method 1-----------
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} was not found"}
        # --------- handling no-exiting post ids: method 2-----------
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"post details": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cur.execute("""DELETE FROM posts WHERE id = %s returning* """,(str(id),))
    deleted_post = cur.fetchone()
    conn.commit()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) # 204 not send any message back


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cur.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING* """, 
                (post.title, post.content, post.published, str(id)))
    updated_post = cur.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    return {"data": updated_post}