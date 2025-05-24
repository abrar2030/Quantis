import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..middleware.auth import (ApiKeyManager, RateLimiter, Roles,
                              admin_required, readonly_or_above,
                              user_or_admin_required, validate_api_key)
from ..schemas import UserBase, UserCreate, User

router = APIRouter()
rate_limiter = RateLimiter(60)  # 60 requests per minute


class ApiKeyResponse(BaseModel):
    api_key: str
    expires_at: str
    role: str


class ApiKeyRequest(BaseModel):
    user_id: str
    role: str = Roles.USER
    expiry_days: int = 30


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    request: ApiKeyRequest,
    current_user: dict = Depends(admin_required)
):
    """Create a new API key (admin only)."""
    api_key = ApiKeyManager.create_api_key(
        user_id=request.user_id,
        role=request.role,
        expiry_days=request.expiry_days
    )
    
    key_info = ApiKeyManager.validate_api_key(api_key)
    
    return {
        "api_key": api_key,
        "expires_at": key_info["expires_at"],
        "role": key_info["role"]
    }


@router.delete("/api-keys/{api_key}")
async def revoke_api_key(
    api_key: str,
    current_user: dict = Depends(admin_required)
):
    """Revoke an API key (admin only)."""
    success = ApiKeyManager.revoke_api_key(api_key)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return {"message": "API key revoked successfully"}


@router.get("/api-keys/user/{user_id}", response_model=List[str])
async def get_user_api_keys(
    user_id: str,
    current_user: dict = Depends(admin_required)
):
    """Get all API keys for a user (admin only)."""
    keys = ApiKeyManager.get_user_keys(user_id)
    return keys


@router.get("/users/me")
async def get_current_user(current_user: dict = Depends(validate_api_key)):
    """Get information about the current authenticated user."""
    # Remove sensitive information
    if "expires_at" in current_user:
        return {
            "user_id": current_user["user_id"],
            "role": current_user["role"],
            "expires_at": current_user["expires_at"]
        }
    return {
        "user_id": current_user["user_id"],
        "role": current_user["role"]
    }


@router.get("/users", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(admin_required)
):
    """Get list of users (admin only)."""
    # In a real application, this would fetch from a database
    # This is a placeholder implementation
    return [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "is_active": True
        },
        {
            "id": 2,
            "username": "user",
            "email": "user@example.com",
            "role": "user",
            "is_active": True
        }
    ][skip:skip+limit]


@router.post("/users", response_model=User)
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(admin_required)
):
    """Create a new user (admin only)."""
    # In a real application, this would store in a database
    # This is a placeholder implementation
    return {
        "id": 3,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": True
    }
