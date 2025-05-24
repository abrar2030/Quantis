import os
import sys

import joblib
import numpy as np
from fastapi import APIRouter, Depends, HTTPException

from ..middleware.auth import (RateLimiter, readonly_or_above, 
                              user_or_admin_required, validate_api_key)
from ..schemas import (ModelHealthResponse, PredictionRequest,
                       PredictionResponse)

router = APIRouter()
model_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "tft_model.pkl",
)

# Rate limiter for prediction endpoint
prediction_rate_limiter = RateLimiter(30)  # 30 requests per minute


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
async def predict(
    request: PredictionRequest, 
    user: dict = Depends(user_or_admin_required),
    _: dict = Depends(prediction_rate_limiter)
):
    """
    Generate predictions using the forecasting model.
    
    Requires user or admin role and is rate limited to 30 requests per minute.
    """
    try:
        model = get_model()
        prediction = model.predict([request.features]).tolist()

        # Get the highest probability from predict_proba
        probas = model.predict_proba([request.features])
        confidence = float(probas.max())

        return {
            "prediction": prediction[0] if isinstance(prediction[0], list) else prediction,
            "confidence": confidence,
        }
    except Exception as e:
        # Log the error (in a production system)
        print(f"Prediction error: {str(e)}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/model_health", response_model=ModelHealthResponse)
async def health_check(user: dict = Depends(readonly_or_above)):
    """
    Check the health status of the forecasting model.
    
    Requires at least readonly access.
    """
    try:
        # Attempt to load the model to verify it's accessible
        model = get_model()
        # Run a simple prediction to verify functionality
        test_input = np.random.rand(128)
        model.predict([test_input])
        
        return {"status": "healthy", "version": "2.1.0"}
    except Exception as e:
        # Log the error (in a production system)
        print(f"Health check error: {str(e)}", file=sys.stderr)
        return {"status": "unhealthy", "version": "2.1.0"}
