from fastapi import APIRouter, HTTPException, Depends
from app.agents import timeline_agent
from app.auth import get_user
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/timeline")


class TimelineRequestAuth(BaseModel):
    quiz_id: str


@router.post("/")
async def fetch_timeline(
    request: TimelineRequestAuth, current_user: Dict[str, Any] = Depends(get_user)
) -> Dict[str, Any]:
    try:
        user_id = current_user["user_id"]
        timeline = await timeline_agent.fetch_timeline(user_id, request.quiz_id)
        return timeline
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/")
async def get_timeline(
    current_user: Dict[str, Any] = Depends(get_user),
) -> Dict[str, Any]:
    try:
        user_id = current_user["user_id"]
        timeline = await timeline_agent.get_timeline(user_id)
        if not timeline:
            raise HTTPException(404, "timeline not found")
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
