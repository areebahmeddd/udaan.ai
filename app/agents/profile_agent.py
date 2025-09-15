import uuid
from app.db import get_supabase
from app.models import ProfileCreate, Profile
from typing import Optional


async def create_profile(profile_data: ProfileCreate) -> Profile:
    supabase = get_supabase()
    user_id = str(uuid.uuid4())

    profile_dict = profile_data.model_dump()
    profile_dict["user_id"] = user_id

    result = supabase.table("profiles").insert(profile_dict).execute()

    if result.data:
        return Profile(**result.data[0])
    else:
        raise Exception("failed to create profile")


async def get_profile(user_id: str) -> Optional[Profile]:
    supabase = get_supabase()
    result = supabase.table("profiles").select("*").eq("user_id", user_id).execute()

    if result.data:
        return Profile(**result.data[0])
    return None


async def update_profile(user_id: str, profile_data: ProfileCreate) -> Profile:
    supabase = get_supabase()
    profile_dict = profile_data.model_dump()

    result = (
        supabase.table("profiles").update(profile_dict).eq("user_id", user_id).execute()
    )

    if result.data:
        return Profile(**result.data[0])
    else:
        raise Exception("failed to update profile")
