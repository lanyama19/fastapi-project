from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import models, schemas, oauth2
from app.database import get_async_db

router = APIRouter(
    prefix="/v2/posts",
    tags=['Posts v2']
)


@router.get("/", response_model=List[schemas.PostWithVotes])
async def get_posts(
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(oauth2.get_current_user_async),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    query = (
        select(
            models.Post,
            func.count(models.Vote.user_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .options(selectinload(models.Post.owner))
        .where(models.Post.title.contains(search))
        .where(models.Post.published == True)
        .group_by(models.Post.id)
        .limit(limit)
        .offset(skip)
    )
    result = await db.execute(query)
    rows = result.all()
    return [{"post": row[0], "votes": int(row[1])} for row in rows]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(oauth2.get_current_user_async)
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    await db.refresh(new_post, attribute_names=["owner"])
    return new_post


@router.get("/{id}", response_model=schemas.PostWithVotes)
async def get_post(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(oauth2.get_current_user_async)
):
    query = (
        select(
            models.Post,
            func.count(models.Vote.user_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .options(selectinload(models.Post.owner))
        .where(models.Post.id == id)
        .group_by(models.Post.id)
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return {"post": row[0], "votes": int(row[1])}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(oauth2.get_current_user_async)
):
    query = select(models.Post).where(models.Post.id == id)
    result = await db.execute(query)
    post_to_delete = result.scalar_one_or_none()

    if post_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if post_to_delete.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action.")

    await db.delete(post_to_delete)
    await db.commit()


@router.put("/{id}", response_model=schemas.Post)
async def update_post(
    id: int,
    post: schemas.PostCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(oauth2.get_current_user_async)
):
    query = select(models.Post).where(models.Post.id == id)
    result = await db.execute(query)
    post_to_update = result.scalar_one_or_none()

    if post_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if post_to_update.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action.")

    for key, value in post.model_dump().items():
        setattr(post_to_update, key, value)

    await db.commit()
    await db.refresh(post_to_update)
    await db.refresh(post_to_update, attribute_names=["owner"])
    return post_to_update

