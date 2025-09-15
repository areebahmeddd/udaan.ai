from fastapi import APIRouter, HTTPException
from app.agents import timeline_agent
from app.models import TimelineRequest
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/timeline")


@router.post("/")
async def fetch_timeline(request: TimelineRequest) -> Dict[str, Any]:
    try:
        timeline = await timeline_agent.fetch_timeline(request.user_id, request.quiz_id)
        return timeline
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{user_id}")
async def get_timeline(user_id: str) -> Dict[str, Any]:
    try:
        timeline = await timeline_agent.get_timeline(user_id)
        if not timeline:
            raise HTTPException(404, "timeline not found")
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
