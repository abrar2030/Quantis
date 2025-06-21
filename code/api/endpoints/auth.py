"""
Enhanced authentication and security system for Quantis API
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import redis.asyncio as redis
from functools import wraps
import time
import hashlib
import pyotp # Added for MFA
import qrcode # Added for MFA QR code generation
import io # Added for MFA QR code generation

from .config import get_settings
from .database_enhanced import get_db, get_redis
from .models_enhanced import User, ApiKey, UserSession, AuditLog, RolePermission # Added RolePermission
from .schemas_enhanced import UserResponse, Token

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = settings.security.algorithm
SECRET_KEY = settings.security.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.security.refresh_token_expire_days

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)


class SecurityManager:
    """Centralized security management"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.failed_attempts = {}  # In production, use Redis
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Generate a JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    def create_access_token(self, user_id: int, username: str, role: str, permissions: List[str]) -> str: # Added permissions
        """Create an access token"""
        data = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "permissions": permissions, # Added permissions
            "type": "access"
        }
        return self.generate_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    def create_refresh_token(self, user_id: int, username: str) -> str:
        """Create a refresh token"""
        data = {
            "sub": str(user_id),
            "username": username,
            "type": "refresh"
        }
        return self.generate_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    
    def generate_api_key(self) -> str:
        """Generate a new API key"""
        return f"qk_{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def check_rate_limit(self, identifier: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit"""
        # This is a simple in-memory implementation
        # In production, use Redis for distributed rate limiting
        current_time = time.time()
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Remove old attempts outside the window
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if current_time - attempt < window
        ]
        
        # Check if within limit
        if len(self.failed_attempts[identifier]) >= limit:
            return False
        
        # Add current attempt
        self.failed_attempts[identifier].append(current_time)
        return True
    
    def is_account_locked(self, user: User) -> bool:
        """Check if user account is locked"""
        if user.locked_until and user.locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_account(self, user: User, db: Session):
        """Lock user account after failed attempts"""
        user.locked_until = datetime.utcnow() + timedelta(
            minutes=settings.security.lockout_duration_minutes
        )
        user.login_attempts = 0
        db.commit()
        logger.warning(f"Account locked for user {user.username}")
    
    def record_failed_login(self, user: User, db: Session):
        """Record a failed login attempt"""
        user.login_attempts += 1
        if user.login_attempts >= settings.security.max_login_attempts:
            self.lock_account(user, db)
        else:
            db.commit()
    
    def record_successful_login(self, user: User, db: Session):
        """Record a successful login"""
        user.last_login = datetime.utcnow()
        user.login_attempts = 0
        user.locked_until = None
        db.commit()

    def generate_mfa_secret(self) -> str:
        """Generates a new MFA secret."""
        return pyotp.random_base32()

    def get_mfa_uri(self, user_email: str, secret: str) -> str:
        """Generates the provisioning URI for MFA."""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name="Quantis"
        )

    def verify_mfa_code(self, secret: str, otp_code: str) -> bool:
        """Verifies the MFA code."""
        totp = pyotp.TOTP(secret)
        return totp.verify(otp_code)

    def generate_qr_code_svg(self, uri: str) -> str:
        """Generates an SVG string for a QR code from a URI."""
        img = qrcode.make(uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG") # Save as PNG first, then convert to SVG if needed, or directly use base64 encoded PNG
        # For simplicity, returning base64 encoded PNG. If SVG is strictly required, more complex libs might be needed.
        # Or, a direct SVG generation library like 'qrcode[svg]' could be used.
        # For now, let's assume a base64 encoded PNG is acceptable for display.
        import base64
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


# Global security manager instance
security_manager = SecurityManager()


class RateLimiter:
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
        identifier: str = "default"
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limit
        Returns (is_allowed, info_dict)
        """
        current_time = int(time.time())
        pipe = self.redis.pipeline()
        
        # Use sliding window log algorithm
        window_start = current_time - window
        
        # Remove old entries
        await pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_requests = await pipe.zcard(key)
        
        if current_requests >= limit:
            # Get time until reset
            oldest_request = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest_request:
                reset_time = int(oldest_request[0][1]) + window
                time_until_reset = max(0, reset_time - current_time)
            else:
                time_until_reset = window
            
            return False, {
                "limit": limit,
                "remaining": 0,
                "reset_time": time_until_reset,
                "retry_after": time_until_reset
            }
        
        # Add current request
        await pipe.zadd(key, {f"{current_time}:{identifier}": current_time})
        await pipe.expire(key, window)
        await pipe.execute()
        
        remaining = limit - current_requests - 1
        
        return True, {
            "limit": limit,
            "remaining": remaining,
            "reset_time": window,
            "retry_after": 0
        }


async def get_rate_limiter() -> RateLimiter:
    """Get rate limiter dependency"""
    redis_client = await get_redis()
    return RateLimiter(redis_client)


def rate_limit(requests: int = 100, window: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)
            
            # Get client identifier
            client_ip = request.client.host
            user_agent = request.headers.get("user-agent", "")
            identifier = f"{client_ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
            
            # Check rate limit
            rate_limiter = await get_rate_limiter()
            is_allowed, info = await rate_limiter.is_allowed(
                f"rate_limit:{identifier}",
                requests,
                window,
                identifier
            )
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(info["reset_time"]),
                        "Retry-After": str(info["retry_after"])
                    }
                )
            
            # Add rate limit headers to response
            response = await func(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(info["reset_time"])
            
            return response
        return wrapper
    return decorator


async def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    mfa_code: Optional[str] = None # Added for MFA
) -> User:
    """Get current user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    payload = security_manager.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(
        User.id == int(user_id),
        User.is_active == True,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if security_manager.is_account_locked(user):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked"
        )

    # MFA check
    if user.is_mfa_enabled:
        if not mfa_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA code required"
            )
        if not user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MFA enabled but secret not found"
            )
        if not security_manager.verify_mfa_code(user.mfa_secret, mfa_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid MFA code"
            )
    
    return user


async def get_current_user_from_api_key(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from API key"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None
    
    # Hash the API key
    key_hash = security_manager.hash_api_key(api_key)
    
    # Find API key in database
    api_key_obj = db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True,
        ApiKey.is_deleted == False
    ).first()
    
    if not api_key_obj:
        return None
    
    # Check if API key is expired
    if api_key_obj.is_expired():
        return None

    # Check IP Whitelist for API Key
    client_ip = request.client.host
    if api_key_obj.ip_whitelist and client_ip not in api_key_obj.ip_whitelist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized from this IP address"
        )
    
    # Get user
    user = db.query(User).filter(
        User.id == api_key_obj.user_id,
        User.is_active == True,
        User.is_deleted == False
    ).first()
    
    if not user:
        return None
    
    # Update API key usage
    api_key_obj.last_used = datetime.utcnow()
    api_key_obj.usage_count += 1
    db.commit()
    
    return user


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from either JWT token or API key"""
    # Try API key first
    user = await get_current_user_from_api_key(request, db)
    if user:
        return user
    
    # Fall back to JWT token
    return await get_current_user_from_token(credentials, db)


def require_permission(required_permissions: List[str]): # Renamed from require_role
    """Decorator to require specific user permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find current user in kwargs
            current_user = None
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg # Corrected assignment
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has all required permissions
            user_permissions = set([p.permission_name for p in current_user.role.permissions]) # Access permissions via role
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_verified_user(current_user: User = Depends(get_current_user)):
    """Dependency to require verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


class AuditLogger:
    """Audit logging for security events"""
    
    @staticmethod
    def log_event(
        db: Session,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        status_code: Optional[int] = None
    ):
        """Log an audit event"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details or {},
            status_code=status_code
        )
        
        if request:
            audit_log.ip_address = request.client.host
            audit_log.user_agent = request.headers.get("user-agent")
            audit_log.endpoint = str(request.url.path)
            audit_log.method = request.method
        
        db.add(audit_log)
        db.commit()
    
    @staticmethod
    def log_login_attempt(
        db: Session,
        username: str,
        success: bool,
        request: Request,
        user_id: Optional[int] = None,
        failure_reason: Optional[str] = None
    ):
        """Log a login attempt"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id,
            action="user_login",
            resource_type="authentication",
            resource_name=username,
            request=request,
            status_code=200 if success else 401,
            details={"success": success, "failure_reason": failure_reason}
        )

    @staticmethod
    def log_mfa_event(
        db: Session,
        user_id: int,
        action: str,
        request: Request,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an MFA related event"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id,
            action=action,
            resource_type="mfa",
            resource_id=str(user_id),
            resource_name=f"MFA for user {user_id}",
            request=request,
            status_code=200 if success else 400,
            details=details
        )


# Dependency to get current user with optional MFA code
async def get_current_user_with_mfa(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current user, requiring MFA if enabled"""
    mfa_code = request.headers.get("X-MFA-Code") # Assuming MFA code is passed in a header
    return await get_current_user_from_token(credentials, db, mfa_code)


# Dependency to get current user for MFA setup/disable
async def get_current_user_for_mfa_setup(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current user without MFA check for MFA setup/disable endpoints"""
    # This dependency is used for endpoints where MFA is being set up or disabled,
    # so we don't want to enforce MFA check here.
    return await get_current_user_from_token(credentials, db, mfa_code=None)


async def create_user_session(
    db: Session,
    user: User,
    access_token: str,
    refresh_token: str,
    request: Request,
    max_concurrent_sessions: int = settings.security.max_concurrent_sessions # Added for concurrent session control
) -> UserSession:
    """Create a new user session, handling concurrent sessions and IP/User-Agent binding"""
    # Invalidate old sessions if max_concurrent_sessions is exceeded
    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True
    ).order_by(UserSession.last_activity.asc()).all()

    if len(active_sessions) >= max_concurrent_sessions:
        # Invalidate the oldest session(s)
        for i in range(len(active_sessions) - max_concurrent_sessions + 1):
            active_sessions[i].is_active = False
            AuditLogger.log_event(
                db=db,
                user_id=user.id,
                action="session_invalidation",
                resource_type="user_session",
                resource_id=str(active_sessions[i].id),
                resource_name=f"Session {active_sessions[i].id} for {user.username}",
                request=request,
                details={"reason": "Max concurrent sessions exceeded"}
            )

    # Invalidate any existing session with the same IP and User-Agent (optional, but good for security)
    # This prevents a user from having multiple active sessions from the exact same client fingerprint
    existing_session_same_client = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.ip_address == request.client.host,
        UserSession.user_agent == request.headers.get("user-agent"),
        UserSession.is_active == True
    ).first()

    if existing_session_same_client:
        existing_session_same_client.is_active = False
        AuditLogger.log_event(
            db=db,
            user_id=user.id,
            action="session_invalidation",
            resource_type="user_session",
            resource_id=str(existing_session_same_client.id),
            resource_name=f"Session {existing_session_same_client.id} for {user.username}",
            request=request,
            details={"reason": "New session from same client fingerprint"}
        )

    session = UserSession(
        user_id=user.id,
        session_token=access_token, # Storing access token here for simplicity, typically you'd store a hash or a separate session ID
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.security.refresh_token_expire_days),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        is_active=True
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user by username/email and password"""
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    if security_manager.is_account_locked(user):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to too many failed login attempts."
        )

    if not security_manager.verify_password(password, user.hashed_password):
        security_manager.record_failed_login(user, db)
        return None
    
    security_manager.record_successful_login(user, db)
    return user


def create_tokens(user: User) -> Token:
    """Create access and refresh tokens for a user"""
    # Fetch user's permissions from the database
    user_permissions = [p.permission_name for p in user.role.permissions]

    access_token = security_manager.create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role.value,
        permissions=user_permissions # Pass permissions to the token
    )
    refresh_token = security_manager.create_refresh_token(
        user_id=user.id,
        username=user.username
    )
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.security.access_token_expire_minutes * 60
    )


def refresh_access_token(db: Session, refresh_token: str) -> Optional[Token]:
    """Refresh access token using a valid refresh token"""
    payload = security_manager.verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = db.query(User).filter(
        User.id == int(user_id),
        User.is_active == True,
        User.is_deleted == False
    ).first()
    
    if not user:
        return None

    # Validate refresh token against active sessions and IP/User-Agent binding
    session = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.refresh_token == refresh_token,
        UserSession.is_active == True
    ).first()

    if not session or session.is_expired():
        # If session is invalid or expired, invalidate it and return None
        if session: # Only if session exists
            session.is_active = False
            db.commit()
        return None

    # Optional: Check if IP address or User-Agent has changed significantly
    # This might be too strict for some use cases (e.g., mobile users switching networks)
    # For financial applications, this is a good security measure.
    # You would need to pass the current request object to this function.
    # For now, we'll just update the last_activity.
    session.last_activity = datetime.utcnow()
    db.commit()

    return create_tokens(user)


