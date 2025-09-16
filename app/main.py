from fastapi import FastAPI
from app import models
from app.database import engine
from app.v1.routers import post as v1_post, user as v1_user, auth as v1_auth, vote as v1_vote
from fastapi.middleware.cors import CORSMiddleware


# # Create databse for postgres
# models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = ["*"] # allow for every single domain

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_post.router)
app.include_router(v1_user.router)
app.include_router(v1_auth.router)
app.include_router(v1_vote.router)


@app.get("/")
async def root():
    return {"message": "Welcome to my new api"}