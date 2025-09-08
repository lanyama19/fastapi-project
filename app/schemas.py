from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
# from pydantic.types import conint
from typing import Literal


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
        

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    model_config = ConfigDict(from_attributes=True)


class PostWithVotes(BaseModel):
    post: Post
    votes: int
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int]  = None


class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1] # Only 1 or 0 is allowed for direction of the vote
