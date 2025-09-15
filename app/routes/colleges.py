from fastapi import APIRouter, HTTPException, Depends
from app.agents import college_agent
from app.auth import get_user
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/v1/colleges")


class CollegeRequestAuth(BaseModel):
    quiz_id: str
    field: Optional[str] = None
    location_type: Optional[str] = "state"


@router.post("/")
async def fetch_colleges(
    request: CollegeRequestAuth, current_user: Dict[str, Any] = Depends(get_user)
) -> Dict[str, Any]:
    try:
        user_id = current_user["user_id"]
        colleges = await college_agent.fetch_colleges(user_id, request.quiz_id)
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
