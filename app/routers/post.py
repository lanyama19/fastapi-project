from .. import models, schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List


router = APIRouter()


@router.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    ## Run Regular SQL Query to fetch data from the db
    ## Please remove the dependency above before running the code before 
    # cur.execute("""SELECT * FROM posts;""")
    # posts = cur.fetchall()
    posts = db.query(models.Post).all()
    return posts


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    ## Run Regular SQL Query to Insert data into the db
    # cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING* """, 
    #             (post.title, post.content, post.published))
    # new_post = cur.fetchone()
    # conn.commit() # push and stage changes
    ## With the ORM:
    # new_post = models.Post(title = post.title, content = post.content, published = post.published)  # Bad practice for having many fields
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    # # Regular SQL query for getting one entry
    # cur.execute("""SELECT * FROM posts WHERE id = %s""",(str(id),))
    # post = cur.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        # --------- handling no-exiting post ids: method 1-----------
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} was not found"}
        # --------- handling no-exiting post ids: method 2-----------
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    
    return post


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cur.execute("""DELETE FROM posts WHERE id = %s returning* """,(str(id),))
    # deleted_post = cur.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # 204 not send any message back


@router.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # # Using regular querys to do updates on db
    # cur.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING* """, 
    #             (post.title, post.content, post.published, str(id)))
    # updated_post = cur.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()