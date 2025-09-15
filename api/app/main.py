from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="College API Wrapper", version="0.1")

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "College API Wrapper is running. Visit /docs for interactive API docs"}
