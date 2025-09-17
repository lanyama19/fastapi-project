from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, utils
from app.database import get_async_db

router = APIRouter(
    prefix="/v2/users",
    tags=['Users v2']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):
    user_data = user.model_dump()
    user_data["password"] = utils.hash(user_data["password"])
    new_user = models.User(**user_data)
    db.add(new_user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists."
        )

    await db.refresh(new_user)
    return new_user


@router.get('/{id}', response_model=schemas.UserOut)
async def get_user(id: int, db: AsyncSession = Depends(get_async_db)):
    query = select(models.User).where(models.User.id == id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist.")

    return user
