import importlib.util
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import prediction, users

app = FastAPI(
    title="Quantis API",
    description="Machine Learning API for time series forecasting",
    version="2.1.0",
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
app.include_router(prediction.router, tags=["prediction"])
app.include_router(users.router, prefix="/api", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Quantis API", "version": "2.1.0"}
