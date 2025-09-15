from fastapi import APIRouter, HTTPException
from app.models import ProfileCreate, Profile
from app.agents import profile_agent, quiz_agent
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/profile")


@router.post("/", response_model=Dict[str, Any])
async def create_profile(profile_data: ProfileCreate):
    try:
        profile = await profile_agent.create_profile(profile_data)
        quiz_result = await quiz_agent.generate_question(profile.user_id)

        return {
            "profile": profile.model_dump(),
            "quiz_id": quiz_result["quiz_id"],
            "question": quiz_result["question"],
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{user_id}", response_model=Profile)
async def get_profile(user_id: str):
    try:
        profile = await profile_agent.get_profile(user_id)
        if not profile:
            raise HTTPException(404, "profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.put("/{user_id}", response_model=Profile)
async def update_profile(user_id: str, profile_data: ProfileCreate):
    try:
        profile = await profile_agent.update_profile(user_id, profile_data)
        return profile
    except Exception as e:
        raise HTTPException(500, str(e))
