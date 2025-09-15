from fastapi import APIRouter, HTTPException
from app.db import get_supabase
from app.models import UserSignUp, UserSignIn, AuthResponse
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/auth")


@router.post("/signup", response_model=AuthResponse)
async def user_signup(user_data: UserSignUp) -> AuthResponse:
    try:
        supabase = get_supabase()

        auth_response = supabase.auth.sign_up(
            {
                "email": user_data.email,
                "password": user_data.password,
                "options": {"data": {"name": user_data.name}},
            }
        )

        if auth_response.user is None:
            raise HTTPException(400, "Failed to create user account")

        user = auth_response.user
        session = auth_response.session

        if session is None:
            raise HTTPException(400, "Failed to create session")

        profile_exists = False
        try:
            profile_result = (
                supabase.table("profiles").select("*").eq("user_id", user.id).execute()
            )
            profile_exists = len(profile_result.data) > 0
        except Exception:
            profile_exists = False

        return AuthResponse(
            user_id=user.id,
            email=user.email,
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            profile_exists=profile_exists,
        )

    except Exception as e:
        if "already registered" in str(e).lower():
            raise HTTPException(409, "User with this email already exists")
        raise HTTPException(500, f"Signup failed: {str(e)}")


@router.post("/signin", response_model=AuthResponse)
async def user_signin(user_data: UserSignIn) -> AuthResponse:
    try:
        supabase = get_supabase()

        auth_response = supabase.auth.sign_in_with_password(
            {"email": user_data.email, "password": user_data.password}
        )

        if auth_response.user is None:
            raise HTTPException(401, "Invalid email or password")

        user = auth_response.user
        session = auth_response.session

        if session is None:
            raise HTTPException(401, "Failed to create session")

        profile_exists = False
        try:
            profile_result = (
                supabase.table("profiles").select("*").eq("user_id", user.id).execute()
            )
            profile_exists = len(profile_result.data) > 0
        except Exception:
            profile_exists = False

        return AuthResponse(
            user_id=user.id,
            email=user.email,
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            profile_exists=profile_exists,
        )

    except Exception as e:
        if "invalid" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(401, "Invalid email or password")
        raise HTTPException(500, f"Signin failed: {str(e)}")


@router.post("/logout")
async def user_logout() -> Dict[str, str]:
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        return {"message": "Successfully signed out"}

    except Exception as e:
        raise HTTPException(500, f"Logout failed: {str(e)}")


@router.get("/user/{user_id}")
async def get_userdata(user_id: str) -> Dict[str, Any]:
    try:
        supabase = get_supabase()

        profile_result = (
            supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        )

        if not profile_result.data:
            return {"profile_exists": False, "profile": None}

        return {"profile_exists": True, "profile": profile_result.data[0]}

    except Exception as e:
        raise HTTPException(500, f"Failed to get user profile: {str(e)}")


@router.post("/refresh")
async def refresh_token(refresh_token: str) -> Dict[str, str]:
    try:
        supabase = get_supabase()

        auth_response = supabase.auth.refresh_session(refresh_token)

        if auth_response.session is None:
            raise HTTPException(401, "Invalid refresh token")

        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
        }

    except Exception as e:
        raise HTTPException(401, f"Token refresh failed: {str(e)}")
