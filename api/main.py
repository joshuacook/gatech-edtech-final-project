# api/main.py

import fastapi
from routers import chat_router

app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

app.include_router(chat_router, prefix="/api")
