from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents import quiz_agent
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/quiz")


class QuizStartRequest(BaseModel):
    user_id: str


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answer: str


@router.post("/start")
async def start_quiz(request: QuizStartRequest) -> Dict[str, Any]:
    try:
        result = await quiz_agent.generate_question(request.user_id)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/submit")
async def submit_answer(request: QuizSubmitRequest) -> Dict[str, Any]:
    try:
        result = await quiz_agent.submit_answer(request.quiz_id, request.answer)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
