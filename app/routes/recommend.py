from fastapi import APIRouter, HTTPException
from app.agents import recommendation_agent
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/recommend")


class RecommendationRequest(BaseModel):
    user_id: str
    quiz_id: str


@router.post("/")
async def fetch_recommendations(request: RecommendationRequest) -> Dict[str, Any]:
    try:
        recommendations = await recommendation_agent.fetch_recommendations(
            request.user_id, request.quiz_id
        )
        return recommendations
    except Exception as e:
        raise HTTPException(500, str(e))
