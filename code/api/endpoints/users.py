"""
Enhanced user management endpoints with database integration
"""
from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

import database import get_db
importmiddleware.auth import (
    admin_required, create_jwt_token, public_rate_limit, readonly_or_above,
    standard_rate_limit, user_or_admin_required, validate_api_key
)
importschemas import User, UserCreate, UserBase
importservices.user_service import UserService

router = APIRouter()


# Additional Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"


class ApiKeyResponse(BaseModel):
    api_key: str
    expires_at: Optional[str]
    name: str


class ApiKeyRequest(BaseModel):
    name: str
    expires_days: int = 30


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str]


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# Authentication endpoints
@router.post("/auth/register", response_model=UserProfile)
async def register_user(
    user_data: UserRegistration,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(public_rate_limit)
):
    """Register a new user account."""
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with username and password to get JWT token."""
    user_service = UserService(db)
    
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=30)
    access_token = create_jwt_token(
        data={"user_id": user.id, "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes in seconds
    }


# User profile endpoints
@router.get("/users/me", response_model=UserProfile)
async def get_current_user(
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Get information about the current authenticated user."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(current_user["user_id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/me", response_model=UserProfile)
async def update_current_user(
    user_update: UserBase,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Update current user's profile information."""
    user_service = UserService(db)
    
    # Users can only update their own profile (except role)
    update_data = user_update.dict(exclude_unset=True)
    if "role" in update_data and current_user["role"] != "admin":
        del update_data["role"]  # Non-admins cannot change their role
    
    user = user_service.update_user(current_user["user_id"], **update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.post("/users/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    user_service = UserService(db)
    
    # Verify current password
    user = user_service.get_user_by_id(current_user["user_id"])
    if not user or not user.verify_password(password_data.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    user_service.update_user(current_user["user_id"], password=password_data.new_password)
    
    return {"message": "Password changed successfully"}


# API Key management
@router.post("/users/me/api-keys", response_model=ApiKeyResponse)
async def create_user_api_key(
    key_request: ApiKeyRequest,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Create a new API key for the current user."""
    user_service = UserService(db)
    
    try:
        api_key = user_service.create_api_key(
            user_id=current_user["user_id"],
            name=key_request.name,
            expires_days=key_request.expires_days
        )
        
        # Get key info for response
        key_info = user_service.validate_api_key(api_key)
        
        return ApiKeyResponse(
            api_key=api_key,
            expires_at=key_info["expires_at"],
            name=key_request.name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/me/api-keys")
async def get_user_api_keys(
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Get all API keys for the current user."""
    user_service = UserService(db)
    api_keys = user_service.get_user_api_keys(current_user["user_id"])
    
    return [
        {
            "id": key.id,
            "name": key.name,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "last_used": key.last_used.isoformat() if key.last_used else None,
            "is_active": key.is_active
        }
        for key in api_keys
    ]


@router.delete("/users/me/api-keys/{key_id}")
async def revoke_user_api_key(
    key_id: int,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Revoke one of the current user's API keys."""
    user_service = UserService(db)
    
    # Get the API key to verify ownership
    api_keys = user_service.get_user_api_keys(current_user["user_id"])
    target_key = next((key for key in api_keys if key.id == key_id), None)
    
    if not target_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Revoke the key by making it inactive
    import models ApiKey
    db.query(ApiKey).filter(ApiKey.id == key_id).update({"is_active": False})
    db.commit()
    
    return {"message": "API key revoked successfully"}


# Admin endpoints
@router.get("/users", response_model=List[UserProfile])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Get list of users (admin only)."""
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    
    return [
        UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        for user in users
    ]


@router.post("/users", response_model=UserProfile)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)."""
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: int,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/{user_id}", response_model=UserProfile)
async def update_user(
    user_id: int,
    user_update: UserBase,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)."""
    user_service = UserService(db)
    
    update_data = user_update.dict(exclude_unset=True)
    user = user_service.update_user(user_id, **update_data)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Deactivate user (admin only)."""
    user_service = UserService(db)
    
    if user_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    success = user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deactivated successfully"}


# Admin API key management
@router.post("/admin/api-keys", response_model=ApiKeyResponse)
async def create_api_key_for_user(
    user_id: int,
    key_request: ApiKeyRequest,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Create API key for any user (admin only)."""
    user_service = UserService(db)
    
    try:
        api_key = user_service.create_api_key(
            user_id=user_id,
            name=key_request.name,
            expires_days=key_request.expires_days
        )
        
        key_info = user_service.validate_api_key(api_key)
        
        return ApiKeyResponse(
            api_key=api_key,
            expires_at=key_info["expires_at"],
            name=key_request.name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/users/{user_id}/api-keys")
async def get_user_api_keys_admin(
    user_id: int,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Get all API keys for a specific user (admin only)."""
    user_service = UserService(db)
    api_keys = user_service.get_user_api_keys(user_id)
    
    return [
        {
            "id": key.id,
            "name": key.name,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "last_used": key.last_used.isoformat() if key.last_used else None,
            "is_active": key.is_active
        }
        for key in api_keys
    ]

