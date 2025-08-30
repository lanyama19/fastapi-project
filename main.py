from fastapi import FastAPI
from fastapi.params import Body

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to my new api"}


@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}


@app.post("/creatposts")
def create_posts(payload: dict = Body(...)):
    print(payload)
    return  {"message":"Succesfully created posts"}