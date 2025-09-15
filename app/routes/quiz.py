from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.agents import quiz_agent
from app.auth import get_user
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/v1/quiz")


class QuizStartRequest(BaseModel):
    max_questions: Optional[int] = 10


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answer: str
    max_questions: Optional[int] = 10


@router.post("/start")
async def start_quiz(
    request: QuizStartRequest, current_user: Dict[str, Any] = Depends(get_user)
) -> Dict[str, Any]:
    try:
        user_id = current_user["user_id"]
        result = await quiz_agent.generate_question(user_id)
        result["total_questions"] = request.max_questions
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/submit")
async def submit_answer(
    request: QuizSubmitRequest, current_user: Dict[str, Any] = Depends(get_user)
) -> Dict[str, Any]:
    try:
        result = await quiz_agent.submit_answer(
            request.quiz_id, request.answer, max_questions=request.max_questions
        )
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
