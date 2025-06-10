"""
Enhanced FastAPI application with comprehensive backend features
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging

from .database import init_db, get_db
from .endpoints import prediction, users, datasets, models, monitoring
from .middleware.auth import validate_api_key


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Quantis API...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Quantis API...")


# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="Quantis API",
    description="""
    ## Quantis Time Series Forecasting Platform API
    
    A comprehensive API for time series forecasting with machine learning models.
    
    ### Features
    - **User Management**: Registration, authentication, and role-based access control
    - **Dataset Management**: Upload, analyze, and manage time series datasets
    - **Model Management**: Create, train, and deploy forecasting models
    - **Predictions**: Generate forecasts with confidence scores and batch processing
    - **Monitoring**: System health, metrics, and audit logging
    
    ### Authentication
    Use API keys in the `X-API-Key` header or JWT tokens for authentication.
    
    ### Rate Limiting
    API endpoints are rate-limited based on user roles:
    - Admin: 120 requests/minute
    - User: 60 requests/minute
    - Readonly: 60 requests/minute
    """,
    version="2.0.0",
    contact={
        "name": "Quantis Team",
        "email": "support@quantis.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify actual hosts
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response


# Include routers with proper tags and prefixes
app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["Authentication & Users"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    datasets.router,
    prefix="/api/v1",
    tags=["Dataset Management"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    models.router,
    prefix="/api/v1",
    tags=["Model Management"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    prediction.router,
    prefix="/api/v1",
    tags=["Predictions & Forecasting"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    monitoring.router,
    prefix="/api/v1",
    tags=["Monitoring & Analytics"],
    responses={404: {"description": "Not found"}}
)


# Root endpoints
@app.get("/", tags=["Root"])
async def root():
    """Welcome message and API information."""
    return {
        "message": "Welcome to Quantis API v2.0",
        "description": "Time Series Forecasting Platform",
        "version": "2.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0"
    }


@app.get("/info", tags=["Root"])
async def api_info():
    """Get API information and available endpoints."""
    return {
        "api_name": "Quantis API",
        "version": "2.0.0",
        "description": "Time Series Forecasting Platform",
        "endpoints": {
            "authentication": "/api/v1/auth/",
            "users": "/api/v1/users/",
            "datasets": "/api/v1/datasets/",
            "models": "/api/v1/models/",
            "predictions": "/api/v1/predict/",
            "monitoring": "/api/v1/health/",
            "documentation": "/docs"
        },
        "features": [
            "User authentication and authorization",
            "Dataset upload and management",
            "Model training and deployment",
            "Time series forecasting",
            "Batch predictions",
            "System monitoring",
            "Audit logging",
            "Rate limiting"
        ]
    }


# Protected endpoint example
@app.get("/api/v1/protected", tags=["Examples"])
async def protected_route(current_user: dict = Depends(validate_api_key)):
    """Example of a protected endpoint requiring authentication."""
    return {
        "message": f"Hello, {current_user['username']}!",
        "user_id": current_user["user_id"],
        "role": current_user["role"],
        "access_level": "authenticated"
    }


# Enhanced error handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Custom HTTP exception handler with enhanced error information."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time(),
            "path": str(request.url),
            "method": request.method
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation error handler."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "details": exc.errors(),
            "status_code": 422,
            "timestamp": time.time(),
            "path": str(request.url),
            "method": request.method
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
            "timestamp": time.time(),
            "path": str(request.url),
            "method": request.method
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks."""
    logger.info("Quantis API startup completed")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks on shutdown."""
    logger.info("Quantis API shutdown completed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

