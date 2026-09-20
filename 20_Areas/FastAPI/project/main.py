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

