from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db import get_supabase
from typing import Dict, Any

security = HTTPBearer()


async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    try:
        supabase = get_supabase()

        user = supabase.auth.get_user(credentials.credentials)

        if user is None:
            raise HTTPException(401, "Invalid authentication token")

        return {
            "user_id": user.user.id,
            "email": user.user.email,
        }

    except Exception as e:
        raise HTTPException(401, f"Authentication failed: {str(e)}")


async def get_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any] | None:
    try:
        return await get_user(credentials)
    except HTTPException:
        return None
