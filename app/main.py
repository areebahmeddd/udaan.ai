from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import profile, quiz, recommend, colleges, timeline

app = FastAPI(title="udaan.ai", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(profile.router)
app.include_router(quiz.router)
app.include_router(recommend.router)
app.include_router(colleges.router)
app.include_router(timeline.router)


@app.get("/health")
async def health_check():
    return {"server": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
