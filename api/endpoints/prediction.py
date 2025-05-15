import os
import sys

import joblib
import numpy as np
from fastapi import APIRouter, Depends, HTTPException

from ..middleware.auth import validate_api_key
from ..schemas import (ModelHealthResponse, PredictionRequest,
                       PredictionResponse)

router = APIRouter()
model_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "tft_model.pkl",
)


# Load model lazily when needed
def get_model():
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        # For development, return a dummy model if the real one doesn't exist
        class DummyModel:
            def predict(self, features):
                return np.array([[0.5] * 3])

            def predict_proba(self, features):
                return np.array([[0.2, 0.5, 0.3]])

        return DummyModel()


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, api_key: str = Depends(validate_api_key)):
    model = get_model()
    prediction = model.predict([request.features]).tolist()

    # Get the highest probability from predict_proba
    probas = model.predict_proba([request.features])
    confidence = float(probas.max())

    return {
        "prediction": prediction[0] if isinstance(prediction[0], list) else prediction,
        "confidence": confidence,
    }


@router.get("/model_health", response_model=ModelHealthResponse)
def health_check():
    return {"status": "healthy", "version": "2.1.0"}
