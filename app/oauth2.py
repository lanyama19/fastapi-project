from jose import JWTError, jwt
import copy
from datetime import datetime, timedelta


# SECRET_KEY
SECRET_KEY = "3ae82acd8da07595d8b20cffaf1e40827b18a02742750c7bc50806a234700939"
# Algorithm
ALGORITHM = "HS256"
# Expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = copy.deepcopy(data)
    # add expiration data to the JWT
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt