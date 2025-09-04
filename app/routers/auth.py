from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, utils

router = APIRouter(tags=['Authentication'])


@router.post('/login')
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Invalid credentials, please try again.")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Invalid username or password.")

    # create a token
    # return the token to users
    return {"token": "example token"}