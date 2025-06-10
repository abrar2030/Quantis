"""
Enhanced background task processing system using Celery
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from celery import Celery, Task
from celery.result import AsyncResult
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import joblib
import json
import os

from .config import get_settings
from .database_enhanced import SessionLocal
from .models_enhanced import (
    Model, Dataset, Prediction, User, Notification, 
    ModelStatus, NotificationType, DataQualityReport
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Create Celery app
celery_app = Celery(
    "quantis_tasks",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=[
        "quantis.tasks.ml_tasks",
        "quantis.tasks.data_tasks", 
        "quantis.tasks.notification_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.celery.task_serializer,
    result_serializer=settings.celery.result_serializer,
    accept_content=settings.celery.accept_content,
    timezone=settings.celery.timezone,
    enable_utc=settings.celery.enable_utc,
    task_routes=settings.celery.task_routes,
    task_annotations={
        '*': {'rate_limit': '10/s'}
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    result_expires=3600,  # 1 hour
    task_soft_time_limit=1800,  # 30 minutes
    task_time_limit=3600,  # 1 hour
)


class DatabaseTask(Task):
    """Base task class with database session management"""
    
    def __call__(self, *args, **kwargs):
        """Execute task with database session"""
        db = SessionLocal()
        try:
            return self.run_with_db(db, *args, **kwargs)
        except Exception as e:
            db.rollback()
            logger.error(f"Task {self.name} failed: {e}")
            raise
        finally:
            db.close()
    
    def run_with_db(self, db: Session, *args, **kwargs):
        """Override this method in subclasses"""
        raise NotImplementedError


@celery_app.task(bind=True, base=DatabaseTask, name="quantis.tasks.ml.train_model")
def train_model_task(self, db: Session, model_id: int, user_id: int) -> Dict[str, Any]:
    """Train a machine learning model"""
    try:
        # Get model and dataset
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        dataset = db.query(Dataset).filter(Dataset.id == model.dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {model.dataset_id} not found")
        
        # Update model status
        model.status = ModelStatus.TRAINING
        db.commit()
        
        # Load dataset
        logger.info(f"Loading dataset from {dataset.file_path}")
        if dataset.file_path.endswith('.csv'):
            data = pd.read_csv(dataset.file_path)
        elif dataset.file_path.endswith('.parquet'):
            data = pd.read_parquet(dataset.file_path)
        else:
            raise ValueError(f"Unsupported file format: {dataset.file_path}")
        
        # Prepare features and target
        feature_columns = model.feature_columns or []
        target_column = model.target_column
        
        if not feature_columns:
            # Use all numeric columns except target as features
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            if target_column in numeric_columns:
                numeric_columns.remove(target_column)
            feature_columns = numeric_columns
        
        X = data[feature_columns]
        y = data[target_column] if target_column else None
        
        # Split data
        from sklearn.model_selection import train_test_split
        test_size = model.training_config.get('test_size', 0.2)
        random_state = model.training_config.get('random_state', 42)
        
        if y is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
        else:
            # For unsupervised learning
            X_train, X_test = train_test_split(
                X, test_size=test_size, random_state=random_state
            )
            y_train, y_test = None, None
        
        # Train model based on type
        trained_model = None
        metrics = {}
        
        if model.model_type.value == "linear_regression":
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_squared_error, r2_score
            
            trained_model = LinearRegression(**model.hyperparameters)
            trained_model.fit(X_train, y_train)
            
            # Calculate metrics
            y_pred_train = trained_model.predict(X_train)
            y_pred_test = trained_model.predict(X_test)
            
            metrics = {
                "train_mse": float(mean_squared_error(y_train, y_pred_train)),
                "test_mse": float(mean_squared_error(y_test, y_pred_test)),
                "train_r2": float(r2_score(y_train, y_pred_train)),
                "test_r2": float(r2_score(y_test, y_pred_test))
            }
            
        elif model.model_type.value == "random_forest":
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_squared_error, r2_score
            
            trained_model = RandomForestRegressor(**model.hyperparameters)
            trained_model.fit(X_train, y_train)
            
            # Calculate metrics
            y_pred_train = trained_model.predict(X_train)
            y_pred_test = trained_model.predict(X_test)
            
            metrics = {
                "train_mse": float(mean_squared_error(y_train, y_pred_train)),
                "test_mse": float(mean_squared_error(y_test, y_pred_test)),
                "train_r2": float(r2_score(y_train, y_pred_train)),
                "test_r2": float(r2_score(y_test, y_pred_test)),
                "feature_importance": dict(zip(
                    feature_columns, 
                    trained_model.feature_importances_.tolist()
                ))
            }
            
        elif model.model_type.value == "xgboost":
            try:
                import xgboost as xgb
                from sklearn.metrics import mean_squared_error, r2_score
                
                trained_model = xgb.XGBRegressor(**model.hyperparameters)
                trained_model.fit(X_train, y_train)
                
                # Calculate metrics
                y_pred_train = trained_model.predict(X_train)
                y_pred_test = trained_model.predict(X_test)
                
                metrics = {
                    "train_mse": float(mean_squared_error(y_train, y_pred_train)),
                    "test_mse": float(mean_squared_error(y_test, y_pred_test)),
                    "train_r2": float(r2_score(y_train, y_pred_train)),
                    "test_r2": float(r2_score(y_test, y_pred_test)),
                    "feature_importance": dict(zip(
                        feature_columns,
                        trained_model.feature_importances_.tolist()
                    ))
                }
            except ImportError:
                raise ValueError("XGBoost not installed")
        
        else:
            raise ValueError(f"Unsupported model type: {model.model_type.value}")
        
        # Save trained model
        model_dir = os.path.join(settings.ml.model_storage_path, str(model.id))
        os.makedirs(model_dir, exist_ok=True)
        model_file_path = os.path.join(model_dir, f"model_{model.version}.joblib")
        
        joblib.dump(trained_model, model_file_path)
        
        # Update model in database
        model.file_path = model_file_path
        model.file_size = os.path.getsize(model_file_path)
        model.metrics = metrics
        model.validation_score = metrics.get("test_r2", metrics.get("test_mse"))
        model.test_score = metrics.get("test_r2", metrics.get("test_mse"))
        model.status = ModelStatus.TRAINED
        model.trained_at = datetime.utcnow()
        model.training_samples = len(X_train)
        model.test_samples = len(X_test)
        model.feature_columns = feature_columns
        
        db.commit()
        
        # Send notification
        send_notification_task.delay(
            user_id=user_id,
            title="Model Training Completed",
            message=f"Model '{model.name}' has been successfully trained.",
            notification_type=NotificationType.IN_APP.value,
            category="model_training",
            data={"model_id": model_id, "metrics": metrics}
        )
        
        logger.info(f"Model {model_id} training completed successfully")
        
        return {
            "model_id": model_id,
            "status": "completed",
            "metrics": metrics,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "file_path": model_file_path
        }
        
    except Exception as e:
        # Update model status to failed
        model = db.query(Model).filter(Model.id == model_id).first()
        if model:
            model.status = ModelStatus.FAILED
            db.commit()
        
        # Send error notification
        send_notification_task.delay(
            user_id=user_id,
            title="Model Training Failed",
            message=f"Model training failed: {str(e)}",
            notification_type=NotificationType.IN_APP.value,
            category="model_training",
            priority="high",
            data={"model_id": model_id, "error": str(e)}
        )
        
        logger.error(f"Model {model_id} training failed: {e}")
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="quantis.tasks.data.process_dataset")
def process_dataset_task(self, db: Session, dataset_id: int, user_id: int) -> Dict[str, Any]:
    """Process and analyze a dataset"""
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        # Load dataset
        logger.info(f"Processing dataset {dataset_id}")
        
        if dataset.file_path.endswith('.csv'):
            data = pd.read_csv(dataset.file_path)
        elif dataset.file_path.endswith('.parquet'):
            data = pd.read_parquet(dataset.file_path)
        else:
            raise ValueError(f"Unsupported file format: {dataset.file_path}")
        
        # Basic statistics
        row_count = len(data)
        column_count = len(data.columns)
        
        # Column analysis
        columns_info = {}
        for col in data.columns:
            col_info = {
                "dtype": str(data[col].dtype),
                "null_count": int(data[col].isnull().sum()),
                "null_percentage": float(data[col].isnull().sum() / len(data) * 100),
                "unique_count": int(data[col].nunique()),
                "unique_percentage": float(data[col].nunique() / len(data) * 100)
            }
            
            if data[col].dtype in ['int64', 'float64']:
                col_info.update({
                    "mean": float(data[col].mean()) if not data[col].isnull().all() else None,
                    "std": float(data[col].std()) if not data[col].isnull().all() else None,
                    "min": float(data[col].min()) if not data[col].isnull().all() else None,
                    "max": float(data[col].max()) if not data[col].isnull().all() else None,
                    "median": float(data[col].median()) if not data[col].isnull().all() else None
                })
            
            columns_info[col] = col_info
        
        # Data quality analysis
        missing_values_count = int(data.isnull().sum().sum())
        duplicate_rows_count = int(data.duplicated().sum())
        
        # Outlier detection for numeric columns
        outliers_count = 0
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers_count += int(((data[col] < lower_bound) | (data[col] > upper_bound)).sum())
        
        # Calculate quality score
        completeness_score = (1 - missing_values_count / (row_count * column_count)) * 100
        uniqueness_score = (1 - duplicate_rows_count / row_count) * 100 if row_count > 0 else 100
        consistency_score = max(0, 100 - (outliers_count / row_count * 100)) if row_count > 0 else 100
        quality_score = (completeness_score + uniqueness_score + consistency_score) / 3
        
        # Update dataset
        dataset.row_count = row_count
        dataset.columns_info = columns_info
        dataset.missing_values_count = missing_values_count
        dataset.duplicate_rows_count = duplicate_rows_count
        dataset.outliers_count = outliers_count
        dataset.quality_score = quality_score
        dataset.status = "ready"
        
        # Detect date columns and set date range
        date_columns = []
        for col in data.columns:
            if data[col].dtype == 'object':
                try:
                    pd.to_datetime(data[col].dropna().head(100))
                    date_columns.append(col)
                except:
                    pass
        
        if date_columns:
            # Use first date column for date range
            date_col = date_columns[0]
            date_series = pd.to_datetime(data[date_col], errors='coerce')
            dataset.start_date = date_series.min()
            dataset.end_date = date_series.max()
        
        db.commit()
        
        # Create data quality report
        quality_report = DataQualityReport(
            dataset_id=dataset_id,
            completeness_score=completeness_score,
            accuracy_score=85.0,  # Placeholder - would need more sophisticated analysis
            consistency_score=consistency_score,
            validity_score=90.0,  # Placeholder - would need validation rules
            overall_score=quality_score,
            column_analysis=columns_info,
            outliers_analysis={"total_outliers": outliers_count, "numeric_columns": len(numeric_columns)},
            duplicates_analysis={"duplicate_rows": duplicate_rows_count, "duplicate_percentage": duplicate_rows_count / row_count * 100},
            missing_values_analysis={"total_missing": missing_values_count, "missing_percentage": missing_values_count / (row_count * column_count) * 100},
            recommendations=[
                "Remove duplicate rows" if duplicate_rows_count > 0 else None,
                "Handle missing values" if missing_values_count > 0 else None,
                "Investigate outliers" if outliers_count > row_count * 0.05 else None
            ],
            issues_found=[
                f"Found {duplicate_rows_count} duplicate rows" if duplicate_rows_count > 0 else None,
                f"Found {missing_values_count} missing values" if missing_values_count > 0 else None,
                f"Found {outliers_count} potential outliers" if outliers_count > 0 else None
            ]
        )
        
        # Remove None values from lists
        quality_report.recommendations = [r for r in quality_report.recommendations if r is not None]
        quality_report.issues_found = [i for i in quality_report.issues_found if i is not None]
        
        db.add(quality_report)
        db.commit()
        
        # Send notification
        send_notification_task.delay(
            user_id=user_id,
            title="Dataset Processing Completed",
            message=f"Dataset '{dataset.name}' has been processed successfully.",
            notification_type=NotificationType.IN_APP.value,
            category="data_processing",
            data={
                "dataset_id": dataset_id,
                "row_count": row_count,
                "quality_score": quality_score
            }
        )
        
        logger.info(f"Dataset {dataset_id} processing completed successfully")
        
        return {
            "dataset_id": dataset_id,
            "status": "completed",
            "row_count": row_count,
            "column_count": column_count,
            "quality_score": quality_score,
            "missing_values_count": missing_values_count,
            "duplicate_rows_count": duplicate_rows_count,
            "outliers_count": outliers_count
        }
        
    except Exception as e:
        # Update dataset status to error
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if dataset:
            dataset.status = "error"
            db.commit()
        
        # Send error notification
        send_notification_task.delay(
            user_id=user_id,
            title="Dataset Processing Failed",
            message=f"Dataset processing failed: {str(e)}",
            notification_type=NotificationType.IN_APP.value,
            category="data_processing",
            priority="high",
            data={"dataset_id": dataset_id, "error": str(e)}
        )
        
        logger.error(f"Dataset {dataset_id} processing failed: {e}")
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="quantis.tasks.ml.batch_predict")
def batch_predict_task(self, db: Session, model_id: int, input_data: List[Dict[str, Any]], user_id: int) -> Dict[str, Any]:
    """Perform batch predictions"""
    try:
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        if model.status != ModelStatus.TRAINED:
            raise ValueError(f"Model {model_id} is not trained")
        
        # Load trained model
        trained_model = joblib.load(model.file_path)
        
        # Prepare input data
        input_df = pd.DataFrame(input_data)
        
        # Ensure all required features are present
        missing_features = set(model.feature_columns) - set(input_df.columns)
        if missing_features:
            raise ValueError(f"Missing features: {missing_features}")
        
        # Select only the required features in the correct order
        X = input_df[model.feature_columns]
        
        # Make predictions
        start_time = time.time()
        predictions = trained_model.predict(X)
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Store predictions in database
        prediction_results = []
        for i, (input_row, prediction) in enumerate(zip(input_data, predictions)):
            prediction_obj = Prediction(
                user_id=user_id,
                model_id=model_id,
                input_data=input_row,
                prediction_result={"prediction": float(prediction)},
                execution_time_ms=execution_time_ms // len(predictions),
                model_version=model.version,
                api_version="2.0.0"
            )
            db.add(prediction_obj)
            prediction_results.append({
                "input": input_row,
                "prediction": float(prediction)
            })
        
        db.commit()
        
        # Send notification
        send_notification_task.delay(
            user_id=user_id,
            title="Batch Prediction Completed",
            message=f"Batch prediction with {len(predictions)} samples completed.",
            notification_type=NotificationType.IN_APP.value,
            category="prediction",
            data={
                "model_id": model_id,
                "prediction_count": len(predictions),
                "execution_time_ms": execution_time_ms
            }
        )
        
        logger.info(f"Batch prediction for model {model_id} completed successfully")
        
        return {
            "model_id": model_id,
            "status": "completed",
            "prediction_count": len(predictions),
            "execution_time_ms": execution_time_ms,
            "predictions": prediction_results
        }
        
    except Exception as e:
        # Send error notification
        send_notification_task.delay(
            user_id=user_id,
            title="Batch Prediction Failed",
            message=f"Batch prediction failed: {str(e)}",
            notification_type=NotificationType.IN_APP.value,
            category="prediction",
            priority="high",
            data={"model_id": model_id, "error": str(e)}
        )
        
        logger.error(f"Batch prediction for model {model_id} failed: {e}")
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="quantis.tasks.notifications.send_notification")
def send_notification_task(
    self, 
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    category: Optional[str] = None,
    priority: str = "normal",
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Send a notification to a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Create notification record
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType(notification_type),
            category=category,
            priority=priority,
            data=data or {}
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Send notification based on type
        delivery_status = "sent"
        delivery_error = None
        
        try:
            if notification_type == NotificationType.EMAIL.value:
                # Send email notification
                # This would integrate with an email service
                logger.info(f"Sending email notification to {user.email}")
                
            elif notification_type == NotificationType.SMS.value:
                # Send SMS notification
                # This would integrate with an SMS service
                logger.info(f"Sending SMS notification to {user.phone_number}")
                
            elif notification_type == NotificationType.WEBHOOK.value:
                # Send webhook notification
                # This would make HTTP requests to user's webhook URL
                logger.info(f"Sending webhook notification")
                
            elif notification_type == NotificationType.IN_APP.value:
                # In-app notification (already stored in database)
                logger.info(f"In-app notification created")
            
            # Update notification status
            notification.is_sent = True
            notification.sent_at = datetime.utcnow()
            notification.delivery_status = delivery_status
            
        except Exception as e:
            delivery_error = str(e)
            notification.delivery_status = "failed"
            notification.delivery_error = delivery_error
            notification.retry_count += 1
            
            logger.error(f"Failed to send notification: {e}")
        
        db.commit()
        
        return {
            "notification_id": notification.id,
            "status": delivery_status,
            "error": delivery_error
        }
        
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        raise


@celery_app.task(bind=True, name="quantis.tasks.data.fetch_market_data")
def fetch_market_data_task(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
    """Fetch market data for given symbols"""
    try:
        import yfinance as yf
        from .models_enhanced import MarketData
        
        db = SessionLocal()
        
        try:
            results = {}
            
            for symbol in symbols:
                logger.info(f"Fetching market data for {symbol}")
                
                # Fetch data from Yahoo Finance
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)
                
                if data.empty:
                    logger.warning(f"No data found for symbol {symbol}")
                    continue
                
                # Store data in database
                records_added = 0
                for date, row in data.iterrows():
                    market_data = MarketData(
                        symbol=symbol,
                        exchange="NASDAQ",  # Default exchange
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=int(row['Volume']),
                        adjusted_close=float(row['Close']),  # Yahoo Finance already provides adjusted close
                        data_date=date.date(),
                        timestamp=datetime.utcnow(),
                        source="yahoo_finance",
                        source_id=f"{symbol}_{date.strftime('%Y%m%d')}",
                        is_validated=True,
                        quality_score=95.0
                    )
                    
                    # Check if record already exists
                    existing = db.query(MarketData).filter(
                        MarketData.symbol == symbol,
                        MarketData.data_date == date.date(),
                        MarketData.source == "yahoo_finance"
                    ).first()
                    
                    if not existing:
                        db.add(market_data)
                        records_added += 1
                
                db.commit()
                results[symbol] = {
                    "records_added": records_added,
                    "date_range": f"{start_date} to {end_date}"
                }
                
                logger.info(f"Added {records_added} records for {symbol}")
            
            return {
                "status": "completed",
                "symbols": symbols,
                "results": results
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to fetch market data: {e}")
        raise


# Task monitoring and management
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a Celery task"""
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None,
        "date_done": result.date_done.isoformat() if result.date_done else None
    }


def cancel_task(task_id: str) -> bool:
    """Cancel a Celery task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return True
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        return False


def get_active_tasks() -> List[Dict[str, Any]]:
    """Get list of active tasks"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return []
        
        tasks = []
        for worker, task_list in active_tasks.items():
            for task in task_list:
                tasks.append({
                    "worker": worker,
                    "task_id": task["id"],
                    "name": task["name"],
                    "args": task["args"],
                    "kwargs": task["kwargs"],
                    "time_start": task["time_start"]
                })
        
        return tasks
    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        return []

