"""
Model service for machine learning model management
"""
import os
import json
import joblib
import pickle
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import pandas as pd
import numpy as np

import models


class ModelService:
    def __init__(self, db: Session):
        self.db = db

    def create_model(self, name: str, description: str, model_type: str, 
                    owner_id: int, dataset_id: int, hyperparameters: Dict = None) -> models.Model:
        """Create a new model"""
        # Validate owner and dataset exist
        owner = self.db.query(models.User).filter(models.User.id == owner_id).first()
        if not owner:
            raise ValueError("Owner not found")
        
        dataset = self.db.query(models.Dataset).filter(
            and_(Dataset.id == dataset_id, Dataset.is_active == True)
        ).first()
        if not dataset:
            raise ValueError("Dataset not found")
        
        # Create model record
        model = models.Model(
            name=name,
            description=description,
            model_type=model_type,
            owner_id=owner_id,
            dataset_id=dataset_id,
            hyperparameters=hyperparameters or {},
            status="created"
        )
        
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_model_by_id(self, model_id: int) -> Optional[models.Model]:
        """Get model by ID"""
        return self.db.query(models.Model).filter(
            and_(Model.id == model_id, Model.is_active == True)
        ).first()

    def get_models_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[models.Model]:
        """Get models by owner"""
        return self.db.query(models.Model).filter(
            and_(Model.owner_id == owner_id, Model.is_active == True)
        ).offset(skip).limit(limit).all()

    def get_all_models(self, skip: int = 0, limit: int = 100) -> List[models.Model]:
        """Get all models (admin only)"""
        return self.db.query(models.Model).filter(Model.is_active == True).offset(skip).limit(limit).all()

    def update_model(self, model_id: int, **kwargs) -> Optional[models.Model]:
        """Update model information"""
        model = self.get_model_by_id(model_id)
        if not model:
            return None
        
        for key, value in kwargs.items():
            if hasattr(model, key) and key not in ['id', 'owner_id', 'created_at']:
                setattr(model, key, value)
        
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete_model(self, model_id: int) -> bool:
        """Delete model (soft delete)"""
        model = self.get_model_by_id(model_id)
        if not model:
            return False
        
        model.is_active = False
        self.db.commit()
        return True

    def save_trained_model(self, model_id: int, trained_model: Any, metrics: Dict = None) -> bool:
        """Save trained model to disk and update database"""
        model = self.get_model_by_id(model_id)
        if not model:
            return False
        
        try:
            # Create models directory if it doesn't exist
            os.makedirs("models", exist_ok=True)
            
            # Save model to file
            file_path = f"models/model_{model_id}.pkl"
            joblib.dump(trained_model, file_path)
            
            # Update model record
            model.file_path = file_path
            model.status = "trained"
            model.trained_at = datetime.utcnow()
            if metrics:
                model.metrics = metrics
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error saving model {model_id}: {e}")
            model.status = "failed"
            self.db.commit()
            return False

    def load_trained_model(self, model_id: int) -> Optional[Any]:
        """Load trained model from disk"""
        model = self.get_model_by_id(model_id)
        if not model or not model.file_path or model.status != "trained":
            return None
        
        try:
            return joblib.load(model.file_path)
        except Exception as e:
            print(f"Error loading model {model_id}: {e}")
            return None

    def train_dummy_model(self, model_id: int) -> bool:
        """Train a dummy model for demonstration purposes"""
        model = self.get_model_by_id(model_id)
        if not model:
            return False
        
        try:
            # Update status to training
            model.status = "training"
            self.db.commit()
            
            # Create a simple dummy model based on type
            if model.model_type.lower() in ["tft", "transformer"]:
                dummy_model = DummyTFTmodels.Model()
            elif model.model_type.lower() in ["lstm", "rnn"]:
                dummy_model = DummyLSTMmodels.Model()
            elif model.model_type.lower() == "arima":
                dummy_model = DummyARIMAmodels.Model()
            else:
                dummy_model = DummyLinearmodels.Model()
            
            # Simulate training metrics
            metrics = {
                "mse": np.random.uniform(0.1, 0.5),
                "mae": np.random.uniform(0.05, 0.3),
                "rmse": np.random.uniform(0.2, 0.7),
                "r2_score": np.random.uniform(0.7, 0.95),
                "training_time": np.random.uniform(10, 300),
                "epochs": np.random.randint(50, 200) if model.model_type.lower() in ["tft", "lstm"] else None
            }
            
            # Save the trained model
            return self.save_trained_model(model_id, dummy_model, metrics)
            
        except Exception as e:
            print(f"Error training model {model_id}: {e}")
            model.status = "failed"
            self.db.commit()
            return False


# Dummy model classes for demonstration
class DummyTFTModel:
    def __init__(self):
        self.model_type = "TFT"
        self.weights = np.random.randn(10, 5)
    
    def predict(self, X):
        if isinstance(X, list):
            X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        # Pad or truncate to expected size
        if X.shape[1] < 10:
            X = np.pad(X, ((0, 0), (0, 10 - X.shape[1])), mode='constant')
        elif X.shape[1] > 10:
            X = X[:, :10]
        return np.dot(X, self.weights)
    
    def predict_proba(self, X):
        pred = self.predict(X)
        # Convert to probabilities
        exp_pred = np.exp(pred - np.max(pred, axis=1, keepdims=True))
        return exp_pred / np.sum(exp_pred, axis=1, keepdims=True)


class DummyLSTMModel:
    def __init__(self):
        self.model_type = "LSTM"
        self.weights = np.random.randn(8, 3)
    
    def predict(self, X):
        if isinstance(X, list):
            X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        # Pad or truncate to expected size
        if X.shape[1] < 8:
            X = np.pad(X, ((0, 0), (0, 8 - X.shape[1])), mode='constant')
        elif X.shape[1] > 8:
            X = X[:, :8]
        return np.dot(X, self.weights)
    
    def predict_proba(self, X):
        pred = self.predict(X)
        exp_pred = np.exp(pred - np.max(pred, axis=1, keepdims=True))
        return exp_pred / np.sum(exp_pred, axis=1, keepdims=True)


class DummyARIMAModel:
    def __init__(self):
        self.model_type = "ARIMA"
        self.coefficients = np.random.randn(5)
    
    def predict(self, X):
        if isinstance(X, list):
            X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        # Simple linear combination
        result = np.sum(X * self.coefficients[:X.shape[1]], axis=1, keepdims=True)
        return result.reshape(-1, 1)
    
    def predict_proba(self, X):
        pred = self.predict(X)
        # For ARIMA, return confidence intervals as probabilities
        return np.column_stack([pred * 0.8, pred, pred * 1.2])


class DummyLinearModel:
    def __init__(self):
        self.model_type = "Linear"
        self.weights = np.random.randn(6)
        self.bias = np.random.randn()
    
    def predict(self, X):
        if isinstance(X, list):
            X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        # Pad or truncate to expected size
        if X.shape[1] < 6:
            X = np.pad(X, ((0, 0), (0, 6 - X.shape[1])), mode='constant')
        elif X.shape[1] > 6:
            X = X[:, :6]
        return (np.dot(X, self.weights) + self.bias).reshape(-1, 1)
    
    def predict_proba(self, X):
        pred = self.predict(X)
        # Simple binary classification probabilities
        prob_pos = 1 / (1 + np.exp(-pred.flatten()))
        return np.column_stack([1 - prob_pos, prob_pos])

