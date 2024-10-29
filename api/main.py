# api/main.py

import fastapi
from routers.chat import chat_router
from routers.concepts import concepts_router
from routers.relationships import relationships_router
app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

app.include_router(chat_router, prefix="/api")
app.include_router(concepts_router, prefix="/api")
app.include_router(relationships_router, prefix="/api")
