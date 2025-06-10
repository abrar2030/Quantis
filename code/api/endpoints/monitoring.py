"""
Monitoring and system health endpoints
"""
import os
import psutil
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

import database import get_db
importmiddleware.auth import admin_required, readonly_or_above, validate_api_key
import models Prediction, Model, Dataset, User, AuditLog, SystemMetrics

router = APIRouter()


# Pydantic models
class SystemHealth(BaseModel):
    status: str
    timestamp: str
    database_status: str
    api_status: str
    disk_usage: dict
    memory_usage: dict
    cpu_usage: float


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_datasets: int
    total_models: int
    trained_models: int
    total_predictions: int
    predictions_last_24h: int


class AuditLogEntry(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    created_at: str


class MetricEntry(BaseModel):
    id: int
    metric_name: str
    metric_value: float
    metric_unit: Optional[str]
    tags: Optional[dict]
    created_at: str


# System health endpoints
@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    current_user: dict = Depends(readonly_or_above),
    db: Session = Depends(get_db)
):
    """Get overall system health status."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        database_status = "healthy"
    except Exception:
        database_status = "unhealthy"
    
    # Get system metrics
    disk_usage = psutil.disk_usage('/')
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Determine overall status
    overall_status = "healthy"
    if database_status == "unhealthy" or memory.percent > 90 or disk_usage.percent > 90:
        overall_status = "unhealthy"
    elif memory.percent > 80 or disk_usage.percent > 80 or cpu_percent > 80:
        overall_status = "warning"
    
    return SystemHealth(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        database_status=database_status,
        api_status="healthy",
        disk_usage={
            "total": disk_usage.total,
            "used": disk_usage.used,
            "free": disk_usage.free,
            "percent": disk_usage.percent
        },
        memory_usage={
            "total": memory.total,
            "used": memory.used,
            "available": memory.available,
            "percent": memory.percent
        },
        cpu_usage=cpu_percent
    )


@router.get("/stats", response_model=SystemStats)
async def get_system_statistics(
    current_user: dict = Depends(readonly_or_above),
    db: Session = Depends(get_db)
):
    """Get system usage statistics."""
    # Count totals
    total_users = db.query(models.User).filter(models.User.is_active == True).count()
    
    # Active users (logged in within last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(models.User).filter(
        models.User.is_active == True,
        models.User.last_login >= thirty_days_ago
    ).count()
    
    total_datasets = db.query(models.Dataset).filter(Dataset.is_active == True).count()
    total_models = db.query(models.Model).filter(Model.is_active == True).count()
    trained_models = db.query(models.Model).filter(
        Model.is_active == True,
        Model.status == "trained"
    ).count()
    
    total_predictions = db.query(models.Prediction).count()
    
    # Predictions in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    predictions_last_24h = db.query(models.Prediction).filter(
        Prediction.created_at >= twenty_four_hours_ago
    ).count()
    
    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_datasets=total_datasets,
        total_models=total_models,
        trained_models=trained_models,
        total_predictions=total_predictions,
        predictions_last_24h=predictions_last_24h
    )


# Audit logging endpoints
@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)."""
    query = db.query(AuditLog)
    
    # Apply filters
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    # Get logs with user information
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    # Get usernames
    importservices.user_service import UserService
    user_service = UserService(db)
    
    result = []
    for log in logs:
        username = None
        if log.user_id:
            user = user_service.get_user_by_id(log.user_id)
            username = user.username if user else "Unknown"
        
        result.append(AuditLogEntry(
            id=log.id,
            user_id=log.user_id,
            username=username,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at.isoformat()
        ))
    
    return result


@router.post("/audit-logs")
async def create_audit_log(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Create an audit log entry."""
    audit_log = AuditLog(
        user_id=current_user["user_id"],
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
    
    db.add(audit_log)
    db.commit()
    
    return {"message": "Audit log created successfully"}


# System metrics endpoints
@router.get("/metrics", response_model=List[MetricEntry])
async def get_system_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    metric_name: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),  # Last 24 hours by default, max 1 week
    current_user: dict = Depends(readonly_or_above),
    db: Session = Depends(get_db)
):
    """Get system metrics."""
    query = db.query(SystemMetrics)
    
    # Filter by time range
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    query = query.filter(SystemMetrics.created_at >= time_threshold)
    
    # Filter by metric name if provided
    if metric_name:
        query = query.filter(SystemMetrics.metric_name == metric_name)
    
    metrics = query.order_by(SystemMetrics.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        MetricEntry(
            id=metric.id,
            metric_name=metric.metric_name,
            metric_value=metric.metric_value,
            metric_unit=metric.metric_unit,
            tags=metric.tags,
            created_at=metric.created_at.isoformat()
        )
        for metric in metrics
    ]


@router.post("/metrics")
async def record_metric(
    metric_name: str,
    metric_value: float,
    metric_unit: Optional[str] = None,
    tags: Optional[dict] = None,
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Record a system metric."""
    metric = SystemMetrics(
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        tags=tags
    )
    
    db.add(metric)
    db.commit()
    
    return {"message": "Metric recorded successfully"}


# Performance analytics
@router.get("/analytics/predictions")
async def get_prediction_analytics(
    days: int = Query(7, ge=1, le=90),
    current_user: dict = Depends(readonly_or_above),
    db: Session = Depends(get_db)
):
    """Get prediction analytics over time."""
    time_threshold = datetime.utcnow() - timedelta(days=days)
    
    # Daily prediction counts
    daily_counts = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= time_threshold
    ).group_by(
        func.date(Prediction.created_at)
    ).all()
    
    # Average confidence by day
    daily_confidence = db.query(
        func.date(Prediction.created_at).label('date'),
        func.avg(Prediction.confidence_score).label('avg_confidence')
    ).filter(
        Prediction.created_at >= time_threshold,
        Prediction.confidence_score.isnot(None)
    ).group_by(
        func.date(Prediction.created_at)
    ).all()
    
    # Average execution time by day
    daily_execution_time = db.query(
        func.date(Prediction.created_at).label('date'),
        func.avg(Prediction.execution_time_ms).label('avg_execution_time')
    ).filter(
        Prediction.created_at >= time_threshold,
        Prediction.execution_time_ms.isnot(None)
    ).group_by(
        func.date(Prediction.created_at)
    ).all()
    
    return {
        "daily_prediction_counts": [
            {"date": str(row.date), "count": row.count}
            for row in daily_counts
        ],
        "daily_avg_confidence": [
            {"date": str(row.date), "avg_confidence": float(row.avg_confidence)}
            for row in daily_confidence
        ],
        "daily_avg_execution_time": [
            {"date": str(row.date), "avg_execution_time_ms": float(row.avg_execution_time)}
            for row in daily_execution_time
        ]
    }


@router.get("/analytics/models")
async def get_model_analytics(
    current_user: dict = Depends(readonly_or_above),
    db: Session = Depends(get_db)
):
    """Get model usage analytics."""
    # Model type distribution
    model_types = db.query(
        Model.model_type,
        func.count(Model.id).label('count')
    ).filter(
        Model.is_active == True
    ).group_by(Model.model_type).all()
    
    # Model status distribution
    model_status = db.query(
        Model.status,
        func.count(Model.id).label('count')
    ).filter(
        Model.is_active == True
    ).group_by(Model.status).all()
    
    # Most used models (by prediction count)
    popular_models = db.query(
        Model.id,
        Model.name,
        func.count(Prediction.id).label('prediction_count')
    ).join(
        Prediction, Model.id == Prediction.model_id
    ).filter(
        Model.is_active == True
    ).group_by(
        Model.id, Model.name
    ).order_by(
        func.count(Prediction.id).desc()
    ).limit(10).all()
    
    return {
        "model_type_distribution": [
            {"model_type": row.model_type, "count": row.count}
            for row in model_types
        ],
        "model_status_distribution": [
            {"status": row.status, "count": row.count}
            for row in model_status
        ],
        "most_popular_models": [
            {
                "model_id": row.id,
                "model_name": row.name,
                "prediction_count": row.prediction_count
            }
            for row in popular_models
        ]
    }


# System maintenance endpoints
@router.post("/maintenance/cleanup")
async def cleanup_system(
    days_old: int = Query(30, ge=7, le=365),
    current_user: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Clean up old system data."""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    # Clean up old audit logs
    old_audit_logs = db.query(AuditLog).filter(AuditLog.created_at < cutoff_date).count()
    db.query(AuditLog).filter(AuditLog.created_at < cutoff_date).delete()
    
    # Clean up old system metrics
    old_metrics = db.query(SystemMetrics).filter(SystemMetrics.created_at < cutoff_date).count()
    db.query(SystemMetrics).filter(SystemMetrics.created_at < cutoff_date).delete()
    
    db.commit()
    
    return {
        "message": "System cleanup completed",
        "audit_logs_deleted": old_audit_logs,
        "metrics_deleted": old_metrics
    }

