# Enhanced Database Module Variables for Financial Services

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the database"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for the database"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

# Database Engine Configuration
variable "engine" {
  description = "Database engine (postgres, mysql)"
  type        = string
  default     = "postgres"
  validation {
    condition     = contains(["postgres", "mysql"], var.engine)
    error_message = "Engine must be either postgres or mysql."
  }
}

variable "engine_version" {
  description = "Database engine version"
  type        = string
  default     = "14.9"
}

variable "major_engine_version" {
  description = "Major engine version for option group"
  type        = string
  default     = "14"
}

variable "db_family" {
  description = "Database parameter group family"
  type        = string
  default     = "postgres14"
}

# Instance Configuration
variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "read_replica_instance_class" {
  description = "RDS read replica instance class"
  type        = string
  default     = "db.r6g.large"
}

# Storage Configuration
variable "allocated_storage" {
  description = "Initial allocated storage in GB"
  type        = number
  default     = 100
  validation {
    condition     = var.allocated_storage >= 20
    error_message = "Allocated storage must be at least 20 GB."
  }
}

variable "max_allocated_storage" {
  description = "Maximum allocated storage for autoscaling in GB"
  type        = number
  default     = 1000
}

variable "storage_type" {
  description = "Storage type (gp3, io1, io2)"
  type        = string
  default     = "gp3"
  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.storage_type)
    error_message = "Storage type must be one of: gp2, gp3, io1, io2."
  }
}

# Database Configuration
variable "database_name" {
  description = "Name of the database to create"
  type        = string
  default     = "quantis"
}

variable "master_username" {
  description = "Master username for the database"
  type        = string
  default     = "quantis_admin"
}

variable "database_port" {
  description = "Port for the database"
  type        = number
  default     = 5432
}

# High Availability Configuration
variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

variable "create_read_replica" {
  description = "Create read replicas"
  type        = bool
  default     = true
}

variable "read_replica_count" {
  description = "Number of read replicas to create"
  type        = number
  default     = 2
  validation {
    condition     = var.read_replica_count >= 0 && var.read_replica_count <= 5
    error_message = "Read replica count must be between 0 and 5."
  }
}

# Backup Configuration
variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 35  # Extended for financial compliance
  validation {
    condition     = var.backup_retention_period >= 7 && var.backup_retention_period <= 35
    error_message = "Backup retention period must be between 7 and 35 days."
  }
}

variable "backup_window" {
  description = "Preferred backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "create_manual_snapshot" {
  description = "Create a manual snapshot"
  type        = bool
  default     = true
}

# Performance Configuration
variable "max_connections" {
  description = "Maximum number of database connections"
  type        = string
  default     = "200"
}

variable "work_mem_mb" {
  description = "Work memory in MB"
  type        = number
  default     = 4
}

variable "maintenance_work_mem_mb" {
  description = "Maintenance work memory in MB"
  type        = number
  default     = 64
}

variable "effective_cache_size_mb" {
  description = "Effective cache size in MB"
  type        = number
  default     = 1024
}

# Monitoring Configuration
variable "enhanced_monitoring_interval" {
  description = "Enhanced monitoring interval in seconds (0, 1, 5, 10, 15, 30, 60)"
  type        = number
  default     = 60
  validation {
    condition     = contains([0, 1, 5, 10, 15, 30, 60], var.enhanced_monitoring_interval)
    error_message = "Enhanced monitoring interval must be one of: 0, 1, 5, 10, 15, 30, 60."
  }
}

variable "performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
  validation {
    condition     = contains([7, 731], var.performance_insights_retention_period)
    error_message = "Performance Insights retention period must be 7 or 731 days."
  }
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch"
  type        = list(string)
  default     = ["postgresql"]
}

# Security Configuration
variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when deleting"
  type        = bool
  default     = false
}

variable "auto_minor_version_upgrade" {
  description = "Enable automatic minor version upgrades"
  type        = bool
  default     = true
}

# Database Proxy Configuration
variable "create_db_proxy" {
  description = "Create RDS Proxy for connection pooling"
  type        = bool
  default     = true
}

variable "proxy_idle_client_timeout" {
  description = "Idle client timeout for proxy in seconds"
  type        = number
  default     = 1800
}

variable "proxy_max_connections_percent" {
  description = "Maximum connections percent for proxy"
  type        = number
  default     = 100
}

variable "proxy_max_idle_connections_percent" {
  description = "Maximum idle connections percent for proxy"
  type        = number
  default     = 50
}

# Monitoring and Alerting
variable "alarm_actions" {
  description = "List of ARNs to notify when alarm triggers"
  type        = list(string)
  default     = []
}

variable "cpu_alarm_threshold" {
  description = "CPU utilization threshold for alarm"
  type        = number
  default     = 80
}

variable "connection_alarm_threshold" {
  description = "Connection count threshold for alarm"
  type        = number
  default     = 150
}

variable "freeable_memory_alarm_threshold" {
  description = "Freeable memory threshold for alarm in bytes"
  type        = number
  default     = 268435456  # 256 MB
}

variable "free_storage_alarm_threshold" {
  description = "Free storage space threshold for alarm in bytes"
  type        = number
  default     = 10737418240  # 10 GB
}

# Common Tags
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "quantis"
    ManagedBy   = "terraform"
    Compliance  = "financial-grade"
    DataClass   = "confidential"
  }
}

# Financial Compliance Configuration
variable "enable_audit_logging" {
  description = "Enable comprehensive audit logging"
  type        = bool
  default     = true
}

variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest"
  type        = bool
  default     = true
}

variable "enable_encryption_in_transit" {
  description = "Enable encryption in transit"
  type        = bool
  default     = true
}

variable "enable_point_in_time_recovery" {
  description = "Enable point-in-time recovery"
  type        = bool
  default     = true
}

variable "compliance_standards" {
  description = "List of compliance standards to meet"
  type        = list(string)
  default     = ["PCI-DSS", "SOX", "GDPR", "ISO-27001"]
}

# Data Retention and Archival
variable "data_retention_policy" {
  description = "Data retention policy configuration"
  type = object({
    transaction_data_days = number
    audit_log_days       = number
    backup_days          = number
    archive_after_days   = number
  })
  default = {
    transaction_data_days = 2555  # 7 years
    audit_log_days       = 2555  # 7 years
    backup_days          = 35
    archive_after_days   = 365
  }
}

# Disaster Recovery Configuration
variable "disaster_recovery_config" {
  description = "Disaster recovery configuration"
  type = object({
    enable_cross_region_backup = bool
    backup_region             = string
    rto_hours                = number
    rpo_hours                = number
  })
  default = {
    enable_cross_region_backup = true
    backup_region             = "us-west-2"
    rto_hours                = 4
    rpo_hours                = 1
  }
}

# Performance Tuning
variable "performance_config" {
  description = "Database performance configuration"
  type = object({
    enable_query_optimization = bool
    enable_connection_pooling = bool
    enable_read_scaling      = bool
    enable_write_scaling     = bool
  })
  default = {
    enable_query_optimization = true
    enable_connection_pooling = true
    enable_read_scaling      = true
    enable_write_scaling     = false
  }
}

# Security Hardening
variable "security_hardening" {
  description = "Security hardening configuration"
  type = object({
    enforce_ssl_connections    = bool
    enable_row_level_security = bool
    enable_column_encryption  = bool
    enable_data_masking       = bool
  })
  default = {
    enforce_ssl_connections    = true
    enable_row_level_security = true
    enable_column_encryption  = true
    enable_data_masking       = true
  }
}

# Cost Optimization
variable "cost_optimization" {
  description = "Cost optimization configuration"
  type = object({
    enable_reserved_instances = bool
    enable_storage_autoscaling = bool
    enable_compute_autoscaling = bool
    schedule_non_prod_shutdown = bool
  })
  default = {
    enable_reserved_instances = true
    enable_storage_autoscaling = true
    enable_compute_autoscaling = false
    schedule_non_prod_shutdown = true
  }
}

