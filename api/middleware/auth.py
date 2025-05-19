import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

# Constants
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-should-be-in-env")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

# OAuth2 for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage for API keys (in production, use a database)
api_keys: Dict[str, Dict] = {}

# Role definitions
class Roles:
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class ApiKeyManager:
    @staticmethod
    def create_api_key(user_id: str, role: str = Roles.USER, expiry_days: int = 30) -> str:
        """Create a new API key with expiration and role."""
        api_key = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(days=expiry_days)
        
        api_keys[api_key] = {
            "user_id": user_id,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "expires_at": expiry.isoformat(),
            "last_used": None
        }
        
        return api_key
    
    @staticmethod
    def validate_api_key(api_key: str) -> Dict:
        """Validate API key and return user info if valid."""
        if api_key not in api_keys:
            raise HTTPException(status_code=403, detail="Invalid API key")
        
        key_info = api_keys[api_key]
        
        # Check expiration
        if datetime.now() > datetime.fromisoformat(key_info["expires_at"]):
            raise HTTPException(status_code=403, detail="API key has expired")
        
        # Update last used timestamp
        key_info["last_used"] = datetime.now().isoformat()
        
        return key_info
    
    @staticmethod
    def revoke_api_key(api_key: str) -> bool:
        """Revoke an API key."""
        if api_key in api_keys:
            del api_keys[api_key]
            return True
        return False
    
    @staticmethod
    def get_user_keys(user_id: str) -> List[str]:
        """Get all API keys for a user."""
        return [key for key, info in api_keys.items() if info["user_id"] == user_id]


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
async def validate_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Validate API key and return user info."""
    try:
        # First check environment variable for backward compatibility
        env_api_key = os.getenv("API_SECRET")
        if env_api_key and api_key == env_api_key:
            return {"user_id": "system", "role": Roles.ADMIN}
        
        # Then check the API key manager
        return ApiKeyManager.validate_api_key(api_key)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )


async def validate_jwt_token(token: str = Depends(oauth2_scheme)):
    """Validate JWT token and return user info."""
    payload = decode_jwt_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


# Role-based access control
class RoleChecker:
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    def __call__(self, user: dict = Depends(validate_api_key)):
        if user.get("role") not in self.required_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions. Required roles: {', '.join(self.required_roles)}"
            )
        return user


# Rate limiting
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
            timestamp for timestamp in self.request_history[user_id] 
            if timestamp > minute_ago
        ]
        
        # Check rate limit
        if len(self.request_history[user_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later."
            )
        
        # Add current request
        self.request_history[user_id].append(current_time)
        
        return user


# Convenience dependencies
admin_required = RoleChecker([Roles.ADMIN])
user_or_admin_required = RoleChecker([Roles.USER, Roles.ADMIN])
readonly_or_above = RoleChecker([Roles.READONLY, Roles.USER, Roles.ADMIN])
standard_rate_limit = RateLimiter(60)  # 60 requests per minute
