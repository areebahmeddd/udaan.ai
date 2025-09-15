from fastapi import APIRouter, HTTPException
from app.agents import college_agent
from app.models import CollegeRequest
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/colleges")


@router.post("/")
async def fetch_colleges(request: CollegeRequest) -> Dict[str, Any]:
    try:
        colleges = await college_agent.fetch_colleges(request.user_id, request.quiz_id)
        return colleges
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/search/{field}/{location_type}/{location}")
async def search_colleges(
    field: str, location_type: str, location: str
) -> Dict[str, Any]:
    try:
        colleges = await college_agent.search_colleges(field, location, location_type)
        return {"colleges": colleges, "count": len(colleges)}
    except Exception as e:
        raise HTTPException(500, str(e))
