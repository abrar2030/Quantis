"""
Enhanced FastAPI application with comprehensive backend features
"""
import os
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
import asyncio
import json

from .config import get_settings, Settings # Import Settings class
from .database_enhanced import init_db, get_db, health_check, close_redis, AuditLog, get_encryption_manager, get_data_retention_manager, get_consent_manager, get_data_masking_manager # Import new managers and AuditLog
from .auth_enhanced import get_current_user, AuditLogger, rate_limit
from .models_enhanced import User
from .schemas_enhanced import ErrorResponse, HealthCheck, SystemMetricsResponse
from .endpoints import (
    auth_enhanced, users_enhanced, datasets_enhanced, 
    models_enhanced, predictions_enhanced, notifications_enhanced,
    monitoring_enhanced, websocket_enhanced, financial
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
settings: Settings = get_settings() # Use type hint for settings

# Prometheus metrics
REQUEST_COUNT = Counter(
    'quantis_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'quantis_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

WEBSOCKET_CONNECTIONS = Counter(
    'quantis_websocket_connections_total',
    'Total number of WebSocket connections',
    ['endpoint']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Add response headers
        response.headers["X-Response-Time"] = str(duration)
        
        return response


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = f"req_{int(time.time() * 1000000)}"
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Log audit event for sensitive operations if audit logging is enabled
        if settings.logging.enable_audit_logging and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            try:
                # Get user if authenticated
                user = getattr(request.state, "user", None)
                user_id = user.id if user else None
                
                # Get database session
                db = next(get_db())
                
                AuditLogger.log_event(
                    db=db,
                    user_id=user_id,
                    action=f"{request.method.lower()}_{request.url.path.replace('/', '_')}",
                    resource_type="api_endpoint",
                    resource_name=request.url.path,
                    request=request,
                    status_code=response.status_code
                )
                
            except Exception as e:
                logger.error("Failed to log audit event", error=str(e))
        
        return response


class WebSocketManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.user_connections: Dict[int, list] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: int):
        """Accept a WebSocket connection"""
        await websocket.accept()
        
        if connection_id not in self.active_connections:
            self.active_connections[connection_id] = {}
        
        self.active_connections[connection_id][str(user_id)] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        WEBSOCKET_CONNECTIONS.labels(endpoint=connection_id).inc()
        logger.info("WebSocket connected", connection_id=connection_id, user_id=user_id)
    
    def disconnect(self, connection_id: str, user_id: int):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            if str(user_id) in self.active_connections[connection_id]:
                del self.active_connections[connection_id][str(user_id)]
                
                if not self.active_connections[connection_id]:
                    del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
                
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
        
        logger.info("WebSocket disconnected", connection_id=connection_id, user_id=user_id)
    
    async def send_personal_message(self, message: str, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    if str(user_id) in self.active_connections[connection_id]:
                        websocket = self.active_connections[connection_id][str(user_id)]
                        try:
                            await websocket.send_text(message)
                        except Exception as e:
                            logger.error("Failed to send WebSocket message", error=str(e))
                            self.disconnect(connection_id, user_id)
    
    async def broadcast(self, message: str, connection_id: str):
        """Broadcast a message to all connections in a specific endpoint"""
        if connection_id in self.active_connections:
            for websocket in self.active_connections[connection_id].values():
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error("Failed to broadcast WebSocket message", error=str(e))


# Global WebSocket manager
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Quantis API...")
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        # Initialize other services
        if settings.celery_broker_url:
            logger.info("Background tasks enabled")
        
        # No specific setting for websockets, it's always enabled if the router is included
        logger.info("Quantis API started successfully")
        
    except Exception as e:
        logger.error("Failed to start Quantis API", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Quantis API...")
    try:
        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))
    
    logger.info("Quantis API shutdown complete")


# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="Quantis API",
    description="""
    ## Quantis Time Series Forecasting Platform API
    
    A comprehensive API for quantitative trading and investment analytics with machine learning models.
    
    ### Features
    - **Authentication**: JWT tokens and API keys
    - **Machine Learning**: Train and deploy ML models
    - **Data Processing**: Upload and analyze datasets
    - **Real-time Updates**: WebSocket support
    - **Background Tasks**: Asynchronous processing
    - **Monitoring**: Comprehensive metrics and health checks
    
    ### Authentication
    
    The API supports two authentication methods:
    1. **JWT Tokens**: Use the `/auth/login` endpoint to get access tokens
    2. **API Keys**: Include `X-API-Key` header with your API key
    
    ### Rate Limiting
    
    API endpoints are rate limited to ensure fair usage:
    - Default: 100 requests per minute
    - Authenticated users: Higher limits based on subscription
    
    ### WebSocket Endpoints
    
    Real-time updates are available via WebSocket connections:
    - `/ws/notifications`: Real-time notifications
    - `/ws/predictions`: Live prediction updates
    - `/ws/market-data`: Real-time market data
    """,
    version="2.0.0",
    contact={
        "name": "Quantis API Support",
        "email": "support@quantis.com",
        "url": "https://quantis.com/support"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["quantis.com", "*.quantis.com"]
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(MetricsMiddleware)
app.add_middleware(AuditMiddleware)


# Exception handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            timestamp=time.time(),
            request_id=getattr(request.state, "request_id", None)
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation exception handler"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ValidationError",
            message="Request validation failed",
            details=[
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "code": error["type"]
                }
                for error in exc.errors()
            ],
            timestamp=time.time(),
            request_id=getattr(request.state, "request_id", None)
        ).dict()
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Custom internal server error handler"""
    logger.error("Internal server error", error=str(exc), request_id=getattr(request.state, "request_id", None))
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An internal server error occurred",
            timestamp=time.time(),
            request_id=getattr(request.state, "request_id", None)
        ).dict()
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheck, tags=["System"])
async def health_check_endpoint():
    """System health check"""
    health_status = health_check()
    
    return HealthCheck(
        status="healthy" if all(health_status.values()) else "unhealthy",
        timestamp=health_status["timestamp"],
        database=health_status["database"],
        redis=health_status["redis"],
        external_apis={},
        version=settings.app_version,
        uptime_seconds=int(time.time())  # Simplified uptime
    )


# Metrics endpoint
@app.get("/metrics", tags=["System"])
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# System info endpoint
@app.get("/info", tags=["System"])
@rate_limit(requests=10, window=60)
async def system_info():
    """Get system information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "features": {
            "websockets": True, # WebSockets are now always enabled if the router is included
            "background_tasks": bool(settings.celery_broker_url),
            "data_encryption": settings.compliance.enable_data_encryption,
            "data_masking": settings.compliance.enable_data_masking,
            "data_retention": settings.compliance.enable_data_retention_policies,
            "consent_management": settings.compliance.enable_consent_management,
            "audit_logging": settings.logging.enable_audit_logging
        },
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to Quantis API",
        "version": settings.app_version,
        "docs_url": "/docs" if settings.debug else None,
        "health_url": "/health",
        "metrics_url": "/metrics"
    }


# Include routers
app.include_router(auth_enhanced.router, prefix="/auth", tags=["Authentication"])
app.include_router(users_enhanced.router, prefix="/users", tags=["Users"])
app.include_router(datasets_enhanced.router, prefix="/datasets", tags=["Datasets"])
app.include_router(models_enhanced.router, prefix="/models", tags=["Models"])
app.include_router(predictions_enhanced.router, prefix="/predictions", tags=["Predictions"])
app.include_router(notifications_enhanced.router, prefix="/notifications", tags=["Notifications"])
app.include_router(monitoring_enhanced.router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(financial.router, prefix="/financial", tags=["Financial"])

# WebSocket endpoints
app.include_router(websocket_enhanced.router, prefix="/ws", tags=["WebSocket"])


# WebSocket endpoint for notifications
@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time notifications"""
    try:
        # Authenticate user (simplified for WebSocket)
        # In production, you'd validate the user_id and check permissions
        
        await websocket_manager.connect(websocket, "notifications", user_id)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process incoming WebSocket messages (e.g., user actions, acknowledgements)
                logger.info("Received WebSocket message", user_id=user_id, message=message)
                
                # Example: Echo message back or trigger some action
                await websocket.send_text(f"Message received: {message.get('text', 'No text')}")

        except WebSocketDisconnect:
            websocket_manager.disconnect("notifications", user_id)
            logger.info("WebSocket disconnected", user_id=user_id)
        except Exception as e:
            logger.error("WebSocket error", user_id=user_id, error=str(e))
            websocket_manager.disconnect("notifications", user_id)
            raise HTTPException(status_code=500, detail="WebSocket internal error")



