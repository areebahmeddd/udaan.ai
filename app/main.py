from fastapi import FastAPI
from app.routes import profile, quiz

app = FastAPI(title="udaan.ai", version="1.0.0")
app.include_router(profile.router)
app.include_router(quiz.router)


@app.get("/health")
async def health_check():
    return {"server": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
