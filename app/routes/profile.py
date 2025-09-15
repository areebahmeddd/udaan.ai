from fastapi import APIRouter, HTTPException, Depends
from app.models import ProfileCreate, Profile
from app.agents import profile_agent, quiz_agent
from app.auth import get_user
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/profile")


@router.post("/", response_model=Dict[str, Any])
async def create_profile(
    profile_data: ProfileCreate, current_user: Dict[str, Any] = Depends(get_user)
):
    try:
        user_id = current_user["user_id"]
        profile = await profile_agent.create_profile(profile_data, user_id)
        quiz_result = await quiz_agent.generate_question(user_id)

        return {
            "profile": profile.model_dump(),
            "quiz_id": quiz_result["quiz_id"],
            "question": quiz_result["question"],
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/", response_model=Profile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_user)):
    try:
        user_id = current_user["user_id"]
        profile = await profile_agent.get_profile(user_id)
        if not profile:
            raise HTTPException(404, "profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.put("/", response_model=Profile)
async def update_profile(
    profile_data: ProfileCreate, current_user: Dict[str, Any] = Depends(get_user)
):
    try:
        user_id = current_user["user_id"]
        profile = await profile_agent.update_profile(user_id, profile_data)
        return profile
    except Exception as e:
        raise HTTPException(500, str(e))
