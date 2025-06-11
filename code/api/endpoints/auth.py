"""
Enhanced authentication endpoints for Quantis API
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import secrets

from ..config import get_settings
from ..database_enhanced import get_db, get_cache_manager, CacheManager
from ..auth_enhanced import (
    authenticate_user, create_tokens, refresh_access_token,
    get_current_user, security_manager, AuditLogger,
    create_user_session, rate_limit
)
from ..models_enhanced import User, ApiKey, UserSession
from ..schemas_enhanced import (
    UserLogin, Token, TokenRefresh, UserCreate, UserResponse,
    PasswordChange, ApiKeyCreate, ApiKeyResponse, ApiKeyWithSecret,
    ErrorResponse
)

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@rate_limit(requests=5, window=300)  # 5 registrations per 5 minutes
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = security_manager.hash_password(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            timezone=user_data.timezone,
            role=user_data.role,
            is_active=True,
            is_verified=False  # Email verification required
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log registration event
        AuditLogger.log_event(
            db=db,
            user_id=new_user.id,
            action="user_registration",
            resource_type="user",
            resource_id=str(new_user.id),
            resource_name=new_user.username,
            request=request,
            status_code=201
        )
        
        logger.info(f"New user registered: {new_user.username}")
        
        return UserResponse.from_orm(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
@rate_limit(requests=10, window=300)  # 10 login attempts per 5 minutes
async def login(
    user_credentials: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    try:
        # Authenticate user
        user = authenticate_user(db, user_credentials.username, user_credentials.password)
        
        if not user:
            # Log failed login attempt
            AuditLogger.log_login_attempt(
                db=db,
                username=user_credentials.username,
                success=False,
                request=request,
                failure_reason="Invalid credentials"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Check if user is verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required"
            )
        
        # Create tokens
        tokens = create_tokens(user)
        
        # Create user session
        session = create_user_session(
            db=db,
            user=user,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            request=request
        )
        
        # Set secure cookie for refresh token if remember_me is True
        if user_credentials.remember_me:
            response.set_cookie(
                key="refresh_token",
                value=tokens.refresh_token,
                max_age=settings.security.refresh_token_expire_days * 24 * 60 * 60,
                httponly=True,
                secure=not settings.debug,
                samesite="lax"
            )
        
        # Log successful login
        AuditLogger.log_login_attempt(
            db=db,
            username=user_credentials.username,
            success=True,
            request=request,
            user_id=user.id
        )
        
        logger.info(f"User logged in: {user.username}")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
@rate_limit(requests=20, window=300)  # 20 refresh attempts per 5 minutes
async def refresh_token(
    token_data: Optional[TokenRefresh] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        # Get refresh token from request body or cookie
        refresh_token = None
        if token_data:
            refresh_token = token_data.refresh_token
        elif request:
            refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required"
            )
        
        # Refresh tokens
        new_tokens = refresh_access_token(db, refresh_token)
        
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        logger.info("Token refreshed successfully")
        
        return new_tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
@rate_limit(requests=30, window=300)  # 30 logout attempts per 5 minutes
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate session"""
    try:
        # Get refresh token from cookie
        refresh_token = request.cookies.get("refresh_token")
        
        if refresh_token:
            # Invalidate session
            session = db.query(UserSession).filter(
                UserSession.user_id == current_user.id,
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            ).first()
            
            if session:
                session.is_active = False
                db.commit()
        
        # Clear refresh token cookie
        response.delete_cookie(key="refresh_token")
        
        # Log logout event
        AuditLogger.log_event(
            db=db,
            user_id=current_user.id,
            action="user_logout",
            resource_type="authentication",
            resource_name=current_user.username,
            request=request
        )
        
        logger.info(f"User logged out: {current_user.username}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/change-password")
@rate_limit(requests=5, window=300)  # 5 password changes per 5 minutes
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not security_manager.verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = security_manager.hash_password(password_data.new_password)
        db.commit()
        
        # Invalidate all user sessions except current one
        db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).update({"is_active": False})
        db.commit()
        
        # Log password change event
        AuditLogger.log_event(
            db=db,
            user_id=current_user.id,
            action="password_change",
            resource_type="user",
            resource_id=str(current_user.id),
            resource_name=current_user.username,
            request=request
        )
        
        logger.info(f"Password changed for user: {current_user.username}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.get("/sessions", response_model=List[dict])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active sessions"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).all()
    
    return [
        {
            "id": session.id,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "expires_at": session.expires_at
        }
        for session in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.is_active = False
    db.commit()
    
    return {"message": "Session revoked successfully"}


# API Key Management
@router.post("/api-keys", response_model=ApiKeyWithSecret, status_code=status.HTTP_201_CREATED)
@rate_limit(requests=10, window=3600)  # 10 API keys per hour
async def create_api_key(
    api_key_data: ApiKeyCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    try:
        # Generate API key
        api_key = security_manager.generate_api_key()
        key_hash = security_manager.hash_api_key(api_key)
        
        # Create API key record
        new_api_key = ApiKey(
            user_id=current_user.id,
            key_hash=key_hash,
            name=api_key_data.name,
            description=api_key_data.description,
            expires_at=api_key_data.expires_at,
            rate_limit=api_key_data.rate_limit,
            scopes=api_key_data.scopes,
            is_active=True
        )
        
        db.add(new_api_key)
        db.commit()
        db.refresh(new_api_key)
        
        # Log API key creation
        AuditLogger.log_event(
            db=db,
            user_id=current_user.id,
            action="api_key_creation",
            resource_type="api_key",
            resource_id=str(new_api_key.id),
            resource_name=new_api_key.name,
            request=request
        )
        
        logger.info(f"API key created: {new_api_key.name} for user {current_user.username}")
        
        # Return API key with secret (only shown once)
        response_data = ApiKeyWithSecret.from_orm(new_api_key)
        response_data.key = api_key
        response_data.key_preview = api_key[:8] + "..."
        
        return response_data
        
    except Exception as e:
        logger.error(f"API key creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key creation failed"
        )


@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's API keys"""
    api_keys = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_deleted == False
    ).all()
    
    return [
        {
            **ApiKeyResponse.from_orm(api_key).dict(),
            "key_preview": "qk_" + "*" * 8 + "..."
        }
        for api_key in api_keys
    ]


@router.delete("/api-keys/{api_key_id}")
async def revoke_api_key(
    api_key_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke an API key"""
    api_key = db.query(ApiKey).filter(
        ApiKey.id == api_key_id,
        ApiKey.user_id == current_user.id,
        ApiKey.is_deleted == False
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Soft delete API key
    api_key.is_active = False
    api_key.is_deleted = True
    api_key.deleted_at = datetime.utcnow()
    api_key.deleted_by_id = current_user.id
    db.commit()
    
    # Log API key revocation
    AuditLogger.log_event(
        db=db,
        user_id=current_user.id,
        action="api_key_revocation",
        resource_type="api_key",
        resource_id=str(api_key.id),
        resource_name=api_key.name,
        request=request
    )
    
    logger.info(f"API key revoked: {api_key.name} for user {current_user.username}")
    
    return {"message": "API key revoked successfully"}


@router.post("/verify-email")
@rate_limit(requests=3, window=300)  # 3 verification attempts per 5 minutes
async def verify_email(
    verification_token: str,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache_manager)
):
    """Verify user email address"""
    try:
        # In a real implementation, you would:
        # 1. Validate the verification token
        # 2. Find the user associated with the token
        # 3. Mark the user as verified
        
        # For now, this is a placeholder
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Email verification not implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.post("/forgot-password")
@rate_limit(requests=3, window=300)  # 3 password reset requests per 5 minutes
async def forgot_password(
    email: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    try:
        # Find user by email
        user = db.query(User).filter(
            User.email == email,
            User.is_active == True,
            User.is_deleted == False
        ).first()
        
        if user:
            # In a real implementation, you would:
            # 1. Generate a password reset token
            # 2. Store it in the database or cache
            # 3. Send an email with the reset link
            
            # Log password reset request
            AuditLogger.log_event(
                db=db,
                user_id=user.id,
                action="password_reset_request",
                resource_type="user",
                resource_id=str(user.id),
                resource_name=user.username,
                request=request
            )
            
            logger.info(f"Password reset requested for user: {user.username}")
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

