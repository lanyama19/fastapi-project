from fastapi import Response, status, HTTPException, Depends, APIRouter
from app import schemas, models, oauth2
from app.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/v1/vote",
    tags=['Vote']
)


@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), 
         current_user: int = Depends(oauth2.get_current_user)):
    # Ensure the target post exists
    post_exists = db.query(models.Post.id).filter(models.Post.id == vote.post_id).first()
    if not post_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {vote.post_id} not found")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, 
                                              models.Vote.user_id == current_user.id)
    found_vote = vote_query.first() 
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"you've already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        
        return {"message": "you've just voted this post"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote does not exist.")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "you just revoked the vote on this post"}
