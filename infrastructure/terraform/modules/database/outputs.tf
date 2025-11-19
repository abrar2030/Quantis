# Enhanced Database Module Outputs for Financial Services

# Primary Database Instance
output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.main.arn
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "db_instance_hosted_zone_id" {
  description = "RDS instance hosted zone ID"
  value       = aws_db_instance.main.hosted_zone_id
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_instance_name" {
  description = "RDS instance database name"
  value       = aws_db_instance.main.db_name
}

output "db_instance_username" {
  description = "RDS instance master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "db_instance_engine" {
  description = "RDS instance engine"
  value       = aws_db_instance.main.engine
}

output "db_instance_engine_version" {
  description = "RDS instance engine version"
  value       = aws_db_instance.main.engine_version
}

output "db_instance_class" {
  description = "RDS instance class"
  value       = aws_db_instance.main.instance_class
}

output "db_instance_status" {
  description = "RDS instance status"
  value       = aws_db_instance.main.status
}

output "db_instance_multi_az" {
  description = "RDS instance Multi-AZ status"
  value       = aws_db_instance.main.multi_az
}

output "db_instance_availability_zone" {
  description = "RDS instance availability zone"
  value       = aws_db_instance.main.availability_zone
}

# Read Replicas
output "read_replica_endpoints" {
  description = "RDS read replica endpoints"
  value       = aws_db_instance.read_replica[*].endpoint
  sensitive   = true
}

output "read_replica_ids" {
  description = "RDS read replica IDs"
  value       = aws_db_instance.read_replica[*].id
}

output "read_replica_arns" {
  description = "RDS read replica ARNs"
  value       = aws_db_instance.read_replica[*].arn
}

# Database Proxy
output "db_proxy_endpoint" {
  description = "RDS Proxy endpoint"
  value       = var.create_db_proxy ? aws_db_proxy.main[0].endpoint : null
  sensitive   = true
}

output "db_proxy_arn" {
  description = "RDS Proxy ARN"
  value       = var.create_db_proxy ? aws_db_proxy.main[0].arn : null
}

output "db_proxy_id" {
  description = "RDS Proxy ID"
  value       = var.create_db_proxy ? aws_db_proxy.main[0].id : null
}

# Secrets Manager
output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "db_credentials_secret_name" {
  description = "Name of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.name
}

# Subnet Group
output "db_subnet_group_name" {
  description = "Database subnet group name"
  value       = aws_db_subnet_group.main.name
}

output "db_subnet_group_arn" {
  description = "Database subnet group ARN"
  value       = aws_db_subnet_group.main.arn
}

# Parameter Group
output "db_parameter_group_name" {
  description = "Database parameter group name"
  value       = aws_db_parameter_group.main.name
}

output "db_parameter_group_arn" {
  description = "Database parameter group ARN"
  value       = aws_db_parameter_group.main.arn
}

# Option Group (MySQL only)
output "db_option_group_name" {
  description = "Database option group name"
  value       = var.engine == "mysql" ? aws_db_option_group.main[0].name : null
}

output "db_option_group_arn" {
  description = "Database option group ARN"
  value       = var.engine == "mysql" ? aws_db_option_group.main[0].arn : null
}

# Monitoring
output "enhanced_monitoring_role_arn" {
  description = "Enhanced monitoring IAM role ARN"
  value       = var.enhanced_monitoring_interval > 0 ? aws_iam_role.rds_enhanced_monitoring[0].arn : null
}

# CloudWatch Alarms
output "cpu_alarm_arn" {
  description = "CPU utilization alarm ARN"
  value       = aws_cloudwatch_metric_alarm.database_cpu.arn
}

output "connections_alarm_arn" {
  description = "Database connections alarm ARN"
  value       = aws_cloudwatch_metric_alarm.database_connections.arn
}

output "memory_alarm_arn" {
  description = "Freeable memory alarm ARN"
  value       = aws_cloudwatch_metric_alarm.database_freeable_memory.arn
}

output "storage_alarm_arn" {
  description = "Free storage space alarm ARN"
  value       = aws_cloudwatch_metric_alarm.database_free_storage_space.arn
}

# Manual Snapshot
output "manual_snapshot_id" {
  description = "Manual snapshot ID"
  value       = var.create_manual_snapshot ? aws_db_snapshot.manual_snapshot[0].id : null
}

output "manual_snapshot_arn" {
  description = "Manual snapshot ARN"
  value       = var.create_manual_snapshot ? aws_db_snapshot.manual_snapshot[0].db_snapshot_arn : null
}

# EventBridge Rule
output "db_events_rule_arn" {
  description = "Database events EventBridge rule ARN"
  value       = aws_cloudwatch_event_rule.db_events.arn
}

# Connection Information
output "connection_info" {
  description = "Database connection information"
  value = {
    primary_endpoint = aws_db_instance.main.endpoint
    proxy_endpoint   = var.create_db_proxy ? aws_db_proxy.main[0].endpoint : null
    port            = aws_db_instance.main.port
    database_name   = aws_db_instance.main.db_name
    engine          = aws_db_instance.main.engine
    engine_version  = aws_db_instance.main.engine_version
  }
  sensitive = true
}

# High Availability Configuration
output "high_availability_config" {
  description = "High availability configuration summary"
  value = {
    multi_az_enabled        = aws_db_instance.main.multi_az
    read_replicas_count     = length(aws_db_instance.read_replica)
    backup_retention_days   = aws_db_instance.main.backup_retention_period
    automated_backups       = aws_db_instance.main.backup_retention_period > 0
    deletion_protection     = aws_db_instance.main.deletion_protection
    proxy_enabled          = var.create_db_proxy
  }
}

# Security Configuration
output "security_config" {
  description = "Security configuration summary"
  value = {
    encryption_at_rest      = aws_db_instance.main.storage_encrypted
    kms_key_id             = aws_db_instance.main.kms_key_id
    ssl_enforcement        = true
    secrets_manager_integration = true
    vpc_security_groups    = aws_db_instance.main.vpc_security_group_ids
    publicly_accessible    = aws_db_instance.main.publicly_accessible
  }
}

# Performance Configuration
output "performance_config" {
  description = "Performance configuration summary"
  value = {
    instance_class              = aws_db_instance.main.instance_class
    allocated_storage          = aws_db_instance.main.allocated_storage
    max_allocated_storage      = aws_db_instance.main.max_allocated_storage
    storage_type               = aws_db_instance.main.storage_type
    performance_insights       = aws_db_instance.main.performance_insights_enabled
    enhanced_monitoring        = var.enhanced_monitoring_interval > 0
    parameter_group           = aws_db_parameter_group.main.name
  }
}

# Monitoring Configuration
output "monitoring_config" {
  description = "Monitoring configuration summary"
  value = {
    enhanced_monitoring_interval    = var.enhanced_monitoring_interval
    performance_insights_enabled   = var.performance_insights_enabled
    cloudwatch_logs_exports        = var.enabled_cloudwatch_logs_exports
    cpu_alarm_threshold           = var.cpu_alarm_threshold
    connection_alarm_threshold    = var.connection_alarm_threshold
    memory_alarm_threshold        = var.freeable_memory_alarm_threshold
    storage_alarm_threshold       = var.free_storage_alarm_threshold
  }
}

# Backup Configuration
output "backup_config" {
  description = "Backup configuration summary"
  value = {
    backup_retention_period = aws_db_instance.main.backup_retention_period
    backup_window          = aws_db_instance.main.backup_window
    maintenance_window     = aws_db_instance.main.maintenance_window
    copy_tags_to_snapshot  = aws_db_instance.main.copy_tags_to_snapshot
    manual_snapshot_created = var.create_manual_snapshot
    skip_final_snapshot    = var.skip_final_snapshot
  }
}

# Compliance Information
output "compliance_info" {
  description = "Compliance-related information"
  value = {
    audit_logging_enabled     = var.enable_audit_logging
    encryption_at_rest       = var.enable_encryption_at_rest
    encryption_in_transit    = var.enable_encryption_in_transit
    point_in_time_recovery   = var.enable_point_in_time_recovery
    compliance_standards     = var.compliance_standards
    data_retention_policy    = var.data_retention_policy
    security_hardening       = var.security_hardening
  }
}

# Cost Optimization
output "cost_optimization_config" {
  description = "Cost optimization configuration"
  value = {
    reserved_instances_eligible = var.cost_optimization.enable_reserved_instances
    storage_autoscaling        = var.cost_optimization.enable_storage_autoscaling
    compute_autoscaling        = var.cost_optimization.enable_compute_autoscaling
    non_prod_shutdown_schedule = var.cost_optimization.schedule_non_prod_shutdown
  }
}

# Disaster Recovery
output "disaster_recovery_config" {
  description = "Disaster recovery configuration"
  value = {
    cross_region_backup_enabled = var.disaster_recovery_config.enable_cross_region_backup
    backup_region              = var.disaster_recovery_config.backup_region
    recovery_time_objective    = var.disaster_recovery_config.rto_hours
    recovery_point_objective   = var.disaster_recovery_config.rpo_hours
    multi_az_deployment       = aws_db_instance.main.multi_az
    read_replicas_for_dr      = length(aws_db_instance.read_replica) > 0
  }
}

# Resource Tags
output "resource_tags" {
  description = "Tags applied to database resources"
  value       = var.common_tags
}
