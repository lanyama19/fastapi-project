from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, models, oauth2
from app.database import get_async_db

router = APIRouter(
    prefix="/v2/vote",
    tags=['Vote v2']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(
    vote: schemas.Vote,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = select(models.Post).where(models.Post.id == vote.post_id)
    post_exists = (await db.execute(post_query)).scalar_one_or_none()
    if not post_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post {vote.post_id} not found")

    vote_query = select(models.Vote).where(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = (await db.execute(vote_query)).scalar_one_or_none()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"You've already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        await db.commit()
        return {"message": "You've just voted for this post"}

    if not found_vote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Vote does not exist.")
    await db.delete(found_vote)
    await db.commit()
    return {"message": "You just revoked the vote on this post"}
