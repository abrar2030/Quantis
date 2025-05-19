import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import prediction, users
from .middleware.auth import validate_api_key

# Create FastAPI app
app = FastAPI(
    title="Quantis API",
    description="API for Quantis time series forecasting platform",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prediction.router, tags=["Forecasting"])
app.include_router(users.router, tags=["Users"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Quantis API"}

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Protected endpoint example
@app.get("/protected")
async def protected_route(user: dict = Depends(validate_api_key)):
    return {"message": f"Hello, {user['user_id']}! You have {user['role']} access."}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status_code": exc.status_code,
        "detail": exc.detail,
        "headers": exc.headers,
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # Log the error in a production system
    return {
        "status_code": 500,
        "detail": f"Internal Server Error: {str(exc)}",
    }
