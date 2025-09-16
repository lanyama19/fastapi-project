from jose import JWTError, jwt
import copy
from datetime import datetime, timedelta, timezone
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings


oath2_schema = OAuth2PasswordBearer(tokenUrl='login')

# SECRET_KEY
SECRET_KEY = settings.secret_key
# Algorithm
ALGORITHM = settings.algorithm
# Expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = copy.deepcopy(data)
    # add expiration data to the JWT
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):

    try:
        # python-jose expects a list for "algorithms"
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        raw_id = payload.get("user_id")

        if raw_id is None:
            raise credentials_exception
        # Coerce to int to match TokenData schema
        token_data = schemas.TokenData(id=int(raw_id))
    except JWTError:
        raise credentials_exception
    
    return token_data
    

def get_current_user(token: str = Depends(oath2_schema), db: Session = Depends(database.get_db)) -> int:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user
 
