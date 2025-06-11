"""
Monitoring service for system health and performance tracking
"""
import psutil
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..config import get_settings
from .. import models
from ..middleware.logging import metrics_collector

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    load_average: List[float]


@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    timestamp: str
    total_users: int
    active_users: int
    total_datasets: int
    total_models: int
    total_predictions: int
    predictions_today: int
    avg_prediction_time: float
    error_rate: float


class MonitoringService:
    """Service for monitoring system health and performance"""
    
    def __init__(self, db: Session):
        self.db = db
        self._start_time = time.time()
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        # Network metrics
        network = psutil.net_io_counters()
        network_sent_mb = network.bytes_sent / (1024**2)
        network_recv_mb = network.bytes_recv / (1024**2)
        
        # Connection count
        try:
            connections = len(psutil.net_connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            connections = 0
        
        # Load average (Unix-like systems only)
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory_used_gb,
            memory_total_gb=memory_total_gb,
            disk_percent=disk.percent,
            disk_used_gb=disk_used_gb,
            disk_total_gb=disk_total_gb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_connections=connections,
            load_average=load_avg
        )
    
    def get_database_metrics(self) -> DatabaseMetrics:
        """Get database performance metrics"""
        
        # User metrics
        total_users = self.db.query(models.User).count()
        active_users = self.db.query(models.User).filter(
            models.User.is_active == True
        ).count()
        
        # Dataset metrics
        total_datasets = self.db.query(models.Dataset).filter(
            models.Dataset.is_active == True
        ).count()
        
        # Model metrics
        total_models = self.db.query(models.Model).filter(
            models.Model.is_active == True
        ).count()
        
        # Prediction metrics
        total_predictions = self.db.query(models.Prediction).count()
        
        # Today's predictions
        today = datetime.utcnow().date()
        predictions_today = self.db.query(models.Prediction).filter(
            func.date(models.Prediction.created_at) == today
        ).count()
        
        # Average prediction time
        avg_time_result = self.db.query(
            func.avg(models.Prediction.execution_time_ms)
        ).scalar()
        avg_prediction_time = float(avg_time_result) if avg_time_result else 0.0
        
        # Error rate (from metrics collector)
        app_metrics = metrics_collector.get_metrics()
        error_rate = app_metrics.get("error_rate", 0.0)
        
        return DatabaseMetrics(
            timestamp=datetime.utcnow().isoformat(),
            total_users=total_users,
            active_users=active_users,
            total_datasets=total_datasets,
            total_models=total_models,
            total_predictions=total_predictions,
            predictions_today=predictions_today,
            avg_prediction_time=avg_prediction_time,
            error_rate=error_rate
        )
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        
        app_metrics = metrics_collector.get_metrics()
        
        # Add uptime
        uptime_seconds = time.time() - self._start_time
        uptime_hours = uptime_seconds / 3600
        
        app_metrics.update({
            "uptime_seconds": uptime_seconds,
            "uptime_hours": uptime_hours,
            "uptime_days": uptime_hours / 24
        })
        
        return app_metrics
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        
        try:
            system_metrics = self.get_system_metrics()
            db_metrics = self.get_database_metrics()
            app_metrics = self.get_application_metrics()
            
            # Determine health status based on thresholds
            health_issues = []
            
            # Check CPU usage
            if system_metrics.cpu_percent > 80:
                health_issues.append(f"High CPU usage: {system_metrics.cpu_percent:.1f}%")
            
            # Check memory usage
            if system_metrics.memory_percent > 85:
                health_issues.append(f"High memory usage: {system_metrics.memory_percent:.1f}%")
            
            # Check disk usage
            if system_metrics.disk_percent > 90:
                health_issues.append(f"High disk usage: {system_metrics.disk_percent:.1f}%")
            
            # Check error rate
            if db_metrics.error_rate > 0.05:  # 5% error rate
                health_issues.append(f"High error rate: {db_metrics.error_rate:.2%}")
            
            # Check database connectivity
            try:
                self.db.execute("SELECT 1")
                db_status = "healthy"
            except Exception as e:
                db_status = "unhealthy"
                health_issues.append(f"Database connectivity issue: {str(e)}")
            
            # Determine overall status
            if not health_issues:
                status = "healthy"
            elif len(health_issues) <= 2:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_hours": app_metrics["uptime_hours"],
                "database_status": db_status,
                "system_metrics": asdict(system_metrics),
                "database_metrics": asdict(db_metrics),
                "application_metrics": app_metrics,
                "health_issues": health_issues,
                "checks": {
                    "cpu_ok": system_metrics.cpu_percent <= 80,
                    "memory_ok": system_metrics.memory_percent <= 85,
                    "disk_ok": system_metrics.disk_percent <= 90,
                    "error_rate_ok": db_metrics.error_rate <= 0.05,
                    "database_ok": db_status == "healthy"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            return {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        
        try:
            # Get predictions in the time window
            since = datetime.utcnow() - timedelta(hours=hours)
            
            predictions = self.db.query(models.Prediction).filter(
                models.Prediction.created_at >= since
            ).all()
            
            if not predictions:
                return {
                    "period_hours": hours,
                    "total_predictions": 0,
                    "avg_execution_time": 0,
                    "min_execution_time": 0,
                    "max_execution_time": 0,
                    "predictions_per_hour": 0,
                    "unique_users": 0,
                    "unique_models": 0
                }
            
            # Calculate metrics
            execution_times = [p.execution_time_ms for p in predictions if p.execution_time_ms]
            
            return {
                "period_hours": hours,
                "total_predictions": len(predictions),
                "avg_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
                "min_execution_time": min(execution_times) if execution_times else 0,
                "max_execution_time": max(execution_times) if execution_times else 0,
                "predictions_per_hour": len(predictions) / hours,
                "unique_users": len(set(p.user_id for p in predictions)),
                "unique_models": len(set(p.model_id for p in predictions)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {"error": str(e)}
    
    def check_resource_limits(self) -> Dict[str, Any]:
        """Check if system is approaching resource limits"""
        
        warnings = []
        critical = []
        
        system_metrics = self.get_system_metrics()
        
        # CPU checks
        if system_metrics.cpu_percent > 90:
            critical.append(f"CPU usage critical: {system_metrics.cpu_percent:.1f}%")
        elif system_metrics.cpu_percent > 75:
            warnings.append(f"CPU usage high: {system_metrics.cpu_percent:.1f}%")
        
        # Memory checks
        if system_metrics.memory_percent > 95:
            critical.append(f"Memory usage critical: {system_metrics.memory_percent:.1f}%")
        elif system_metrics.memory_percent > 80:
            warnings.append(f"Memory usage high: {system_metrics.memory_percent:.1f}%")
        
        # Disk checks
        if system_metrics.disk_percent > 95:
            critical.append(f"Disk usage critical: {system_metrics.disk_percent:.1f}%")
        elif system_metrics.disk_percent > 85:
            warnings.append(f"Disk usage high: {system_metrics.disk_percent:.1f}%")
        
        # Check available memory in GB
        available_memory = system_metrics.memory_total_gb - system_metrics.memory_used_gb
        if available_memory < 0.5:  # Less than 500MB
            critical.append(f"Low available memory: {available_memory:.2f}GB")
        elif available_memory < 1.0:  # Less than 1GB
            warnings.append(f"Low available memory: {available_memory:.2f}GB")
        
        # Check available disk space
        available_disk = system_metrics.disk_total_gb - system_metrics.disk_used_gb
        if available_disk < 1.0:  # Less than 1GB
            critical.append(f"Low available disk space: {available_disk:.2f}GB")
        elif available_disk < 5.0:  # Less than 5GB
            warnings.append(f"Low available disk space: {available_disk:.2f}GB")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "critical" if critical else ("warning" if warnings else "ok"),
            "warnings": warnings,
            "critical": critical,
            "system_metrics": asdict(system_metrics)
        }
    
    def get_user_activity_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get user activity statistics"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        # Active users (users who made predictions)
        active_users = self.db.query(models.Prediction.user_id).filter(
            models.Prediction.created_at >= since
        ).distinct().count()
        
        # Predictions by day
        daily_predictions = self.db.query(
            func.date(models.Prediction.created_at).label('date'),
            func.count(models.Prediction.id).label('count')
        ).filter(
            models.Prediction.created_at >= since
        ).group_by(func.date(models.Prediction.created_at)).all()
        
        # Most active users
        top_users = self.db.query(
            models.Prediction.user_id,
            func.count(models.Prediction.id).label('prediction_count')
        ).filter(
            models.Prediction.created_at >= since
        ).group_by(models.Prediction.user_id).order_by(
            func.count(models.Prediction.id).desc()
        ).limit(10).all()
        
        return {
            "period_days": days,
            "active_users": active_users,
            "daily_predictions": [
                {"date": str(date), "count": count} 
                for date, count in daily_predictions
            ],
            "top_users": [
                {"user_id": user_id, "predictions": count}
                for user_id, count in top_users
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

