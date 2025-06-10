"""
Prediction service for handling model predictions
"""
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import numpy as np

import models
from .model_service import ModelService


class PredictionService:
    def __init__(self, db: Session):
        self.db = db
        self.model_service = ModelService(db)

    def create_prediction(self, user_id: int, model_id: int, input_data: List[float]) -> Optional[models.Prediction]:
        """Create a new prediction"""
        # Validate user and model exist
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        model = self.model_service.get_model_by_id(model_id)
        if not model:
            raise ValueError("Model not found")
        
        if model.status != "trained":
            raise ValueError("Model is not trained yet")
        
        try:
            # Load the trained model
            start_time = time.time()
            trained_model = self.model_service.load_trained_model(model_id)
            if not trained_model:
                raise ValueError("Failed to load trained model")
            
            # Make prediction
            prediction_result = trained_model.predict([input_data])
            
            # Calculate confidence score
            try:
                probabilities = trained_model.predict_proba([input_data])
                confidence_score = float(np.max(probabilities))
            except:
                # If predict_proba is not available, use a default confidence
                confidence_score = 0.8
            
            execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            # Convert prediction result to serializable format
            if isinstance(prediction_result, np.ndarray):
                prediction_result = prediction_result.tolist()
            
            # Create prediction record
            prediction = models.Prediction(
                user_id=user_id,
                model_id=model_id,
                input_data=input_data,
                prediction_result=prediction_result,
                confidence_score=confidence_score,
                execution_time_ms=execution_time
            )
            
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)
            return prediction
            
        except Exception as e:
            print(f"Error creating prediction: {e}")
            raise ValueError(f"Prediction failed: {str(e)}")

    def get_prediction_by_id(self, prediction_id: int) -> Optional[models.Prediction]:
        """Get prediction by ID"""
        return self.db.query(models.Prediction).filter(Prediction.id == prediction_id).first()

    def get_predictions_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Prediction]:
        """Get predictions by user"""
        return self.db.query(models.Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(desc(Prediction.created_at)).offset(skip).limit(limit).all()

    def get_predictions_by_model(self, model_id: int, skip: int = 0, limit: int = 100) -> List[models.Prediction]:
        """Get predictions by model"""
        return self.db.query(models.Prediction).filter(
            Prediction.model_id == model_id
        ).order_by(desc(Prediction.created_at)).offset(skip).limit(limit).all()

    def get_all_predictions(self, skip: int = 0, limit: int = 100) -> List[models.Prediction]:
        """Get all predictions (admin only)"""
        return self.db.query(models.Prediction).order_by(
            desc(Prediction.created_at)
        ).offset(skip).limit(limit).all()

    def get_prediction_statistics(self, user_id: int = None, model_id: int = None) -> Dict[str, Any]:
        """Get prediction statistics"""
        query = self.db.query(models.Prediction)
        
        if user_id:
            query = query.filter(Prediction.user_id == user_id)
        if model_id:
            query = query.filter(Prediction.model_id == model_id)
        
        predictions = query.all()
        
        if not predictions:
            return {
                "total_predictions": 0,
                "avg_confidence": 0,
                "avg_execution_time_ms": 0,
                "predictions_by_model": {},
                "predictions_by_day": {}
            }
        
        # Calculate statistics
        total_predictions = len(predictions)
        avg_confidence = np.mean([p.confidence_score for p in predictions if p.confidence_score])
        avg_execution_time = np.mean([p.execution_time_ms for p in predictions if p.execution_time_ms])
        
        # Group by model
        predictions_by_model = {}
        for prediction in predictions:
            model_id = prediction.model_id
            if model_id not in predictions_by_model:
                predictions_by_model[model_id] = 0
            predictions_by_model[model_id] += 1
        
        # Group by day
        predictions_by_day = {}
        for prediction in predictions:
            day = prediction.created_at.date().isoformat()
            if day not in predictions_by_day:
                predictions_by_day[day] = 0
            predictions_by_day[day] += 1
        
        return {
            "total_predictions": total_predictions,
            "avg_confidence": float(avg_confidence),
            "avg_execution_time_ms": float(avg_execution_time),
            "predictions_by_model": predictions_by_model,
            "predictions_by_day": predictions_by_day
        }

    def batch_predict(self, user_id: int, model_id: int, input_data_list: List[List[float]]) -> List[models.Prediction]:
        """Create multiple predictions in batch"""
        predictions = []
        
        for input_data in input_data_list:
            try:
                prediction = self.create_prediction(user_id, model_id, input_data)
                predictions.append(prediction)
            except Exception as e:
                print(f"Error in batch prediction: {e}")
                # Continue with other predictions
                continue
        
        return predictions

