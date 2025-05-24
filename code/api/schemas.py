from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    features: List[float]
    api_key: str


class PredictionResponse(BaseModel):
    prediction: List[float]
    confidence: float


class ModelHealthResponse(BaseModel):
    status: str
    version: str


class UserBase(BaseModel):
    username: str
    email: str
    role: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class FeatureImportance(BaseModel):
    feature_name: str
    importance: float


class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    feature_importance: List[FeatureImportance]
