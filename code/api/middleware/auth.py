"""
Authentication middleware with database integration
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db
from ..services.user_service import UserService

# Constants
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
JWT_SECRET = os.getenv(
    "JWT_SECRET", "your-secret-key-should-be-in-env-change-this-in-production"
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

# OAuth2 for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Role definitions
class Roles:
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


# JWT Token functions
def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT token with expiration."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return encoded_jwt


def decode_jwt_token(token: str):
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# Authentication dependencies
async def validate_api_key(
    api_key: str = Security(API_KEY_HEADER), db: Session = Depends(get_db)
):
    """Validate API key and return user info."""
    try:
        # First check environment variable for backward compatibility
        env_api_key = os.getenv("API_SECRET")
        if env_api_key and api_key == env_api_key:
            return {"user_id": "system", "username": "system", "role": Roles.ADMIN}

        # Use database-backed user service
        user_service = UserService(db)
        user_info = user_service.validate_api_key(api_key)

        if not user_info:
            raise HTTPException(status_code=403, detail="Invalid or expired API key")

        return user_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


async def validate_jwt_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Validate JWT token and return user info."""
    payload = decode_jwt_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database to ensure they still exist and are active
    user_service = UserService(db)
    user = user_service.get_user_by_id(payload.get("user_id"))

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }


# Optional authentication (for endpoints that work with or without auth)
async def optional_auth(
    api_key: str = Security(API_KEY_HEADER, auto_error=False),
    db: Session = Depends(get_db),
):
    """Optional authentication - returns user info if authenticated, None otherwise."""
    if not api_key:
        return None

    try:
        return await validate_api_key(api_key, db)
    except HTTPException:
        return None


# Role-based access control
class RoleChecker:
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles

    def __call__(self, user: dict = Depends(validate_api_key)):
        if user.get("role") not in self.required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required roles: {', '.join(self.required_roles)}",
            )
        return user


# Rate limiting with user-specific tracking
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_history = {}

    def __call__(self, user: dict = Depends(validate_api_key)):
        user_id = user.get("user_id", "anonymous")

        # Initialize if first request
        if user_id not in self.request_history:
            self.request_history[user_id] = []

        # Clean old requests
        current_time = time.time()
        minute_ago = current_time - 60
        self.request_history[user_id] = [
            timestamp
            for timestamp in self.request_history[user_id]
            if timestamp > minute_ago
        ]

        # Check rate limit (admins get higher limits)
        limit = (
            self.requests_per_minute * 2
            if user.get("role") == Roles.ADMIN
            else self.requests_per_minute
        )

        if len(self.request_history[user_id]) >= limit:
            raise HTTPException(
                status_code=429, detail="Rate limit exceeded. Try again later."
            )

        # Add current request
        self.request_history[user_id].append(current_time)

        return user


# IP-based rate limiting for public endpoints
class IPRateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.request_history = {}

    def __call__(self, request):
        # Get client IP
        client_ip = request.client.host

        # Initialize if first request
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []

        # Clean old requests
        current_time = time.time()
        minute_ago = current_time - 60
        self.request_history[client_ip] = [
            timestamp
            for timestamp in self.request_history[client_ip]
            if timestamp > minute_ago
        ]

        # Check rate limit
        if len(self.request_history[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429, detail="Rate limit exceeded. Try again later."
            )

        # Add current request
        self.request_history[client_ip].append(current_time)

        return True


# Convenience dependencies
admin_required = RoleChecker([Roles.ADMIN])
user_or_admin_required = RoleChecker([Roles.USER, Roles.ADMIN])
readonly_or_above = RoleChecker([Roles.READONLY, Roles.USER, Roles.ADMIN])

# Rate limiters
standard_rate_limit = RateLimiter(60)  # 60 requests per minute
prediction_rate_limit = RateLimiter(30)  # 30 requests per minute for predictions
public_rate_limit = IPRateLimiter(30)  # 30 requests per minute for public endpoints


# Legacy compatibility class (for existing code)
class ApiKeyManager:
    """Legacy compatibility class - now uses database backend"""

    @staticmethod
    def create_api_key(
        user_id: str, role: str = Roles.USER, expiry_days: int = 30
    ) -> str:
        """Create a new API key - legacy compatibility method"""
        # This is kept for backward compatibility but should use the service layer
        db = SessionLocal()
        try:
            user_service = UserService(db)
            # Convert string user_id to int if needed
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            return user_service.create_api_key(user_id, f"Legacy Key", expiry_days)
        finally:
            db.close()

    @staticmethod
    def validate_api_key(api_key: str) -> Dict:
        """Validate API key - legacy compatibility method"""
        db = SessionLocal()
        try:
            user_service = UserService(db)
            return user_service.validate_api_key(api_key)
        finally:
            db.close()

    @staticmethod
    def revoke_api_key(api_key: str) -> bool:
        """Revoke an API key - legacy compatibility method"""
        db = SessionLocal()
        try:
            user_service = UserService(db)
            return user_service.revoke_api_key(api_key)
        finally:
            db.close()

    @staticmethod
    def get_user_keys(user_id: str) -> List[str]:
        """Get all API keys for a user - legacy compatibility method"""
        db = SessionLocal()
        try:
            user_service = UserService(db)
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            api_keys = user_service.get_user_api_keys(user_id)
            return [f"key_{key.id}" for key in api_keys]  # Return key IDs for security
        finally:
            db.close()
