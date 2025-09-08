from .. import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from typing import List, Optional


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# Return posts with aggregated vote counts
@router.get("/", response_model=List[schemas.PostWithVotes])
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):
    rows = (
        db.query(
            models.Post,
            func.count(models.Vote.user_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .filter(models.Post.title.contains(search))
        .filter(models.Post.published == True)
        .group_by(models.Post.id)
        .limit(limit)
        .offset(skip)
        .all()
    )

    return [{"post": row[0], "votes": int(row[1])} for row in rows]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    ## Run Regular SQL Query to Insert data into the db
    # cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING* """, 
    #             (post.title, post.content, post.published))
    # new_post = cur.fetchone()
    # conn.commit() # push and stage changes
    ## With the ORM:
    # new_post = models.Post(title = post.title, content = post.content, published = post.published)  # Bad practice for having many fields
    print(current_user.email)
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.PostWithVotes)
def get_post(id: int, response: Response, db: Session = Depends(get_db), 
             current_user: int = Depends(oauth2.get_current_user)):
    row = (
        db.query(
            models.Post,
            func.count(models.Vote.user_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .filter(models.Post.id == id)
        .group_by(models.Post.id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return {"post": row[0], "votes": int(row[1])}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cur.execute("""DELETE FROM posts WHERE id = %s returning* """,(str(id),))
    # deleted_post = cur.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action.")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # 204 not send any message back


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
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
    
    if post_query.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action.")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()
