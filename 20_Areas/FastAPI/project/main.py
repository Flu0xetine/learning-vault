from fastapi import FastAPI 
from fastapi.responses import HTMLResponse  

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}

@app.get("/home",response_class = HTMLResponse, include_in_schema= False)
@app.get("/hom", response_class = HTMLResponse, include_in_schema= False)
def home():
    return f"<h1>welcome home or hom</h1>"

# 同一路径可以对应不同方法
@app.post("/home")
async def home_post():
    return 0;

@app.get("/users/{user_id}")
async def get_user(user_id:str):
    return {
       "user_id":user_id,
       "name": "ddd",
    }
