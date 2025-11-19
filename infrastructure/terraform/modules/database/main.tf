# Enhanced Database Module for Financial Services
# Implements robust database infrastructure with high availability, security, and compliance

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# DB Subnet Group for Multi-AZ deployment
resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
    Purpose     = "database-networking"
    Compliance  = "financial-grade"
  })
}

# DB Parameter Group for optimized performance and security
resource "aws_db_parameter_group" "main" {
  family = var.db_family
  name   = "${var.app_name}-${var.environment}-db-params"

  # Security parameters
  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"  # Log queries taking more than 1 second
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_checkpoints"
    value = "1"
  }

  parameter {
    name  = "log_lock_waits"
    value = "1"
  }

  # Performance parameters
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,pg_audit"
  }

  parameter {
    name  = "max_connections"
    value = var.max_connections
  }

  parameter {
    name  = "work_mem"
    value = var.work_mem_mb * 1024  # Convert MB to KB
  }

  parameter {
    name  = "maintenance_work_mem"
    value = var.maintenance_work_mem_mb * 1024
  }

  parameter {
    name  = "effective_cache_size"
    value = var.effective_cache_size_mb * 1024
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "wal_buffers"
    value = "16MB"
  }

  parameter {
    name  = "default_statistics_target"
    value = "100"
  }

  # Security and compliance parameters
  parameter {
    name  = "ssl"
    value = "1"
  }

  parameter {
    name  = "ssl_ciphers"
    value = "HIGH:MEDIUM:+3DES:!aNULL"
  }

  parameter {
    name  = "password_encryption"
    value = "scram-sha-256"
  }

  parameter {
    name  = "row_security"
    value = "1"
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-params"
    Environment = var.environment
    Purpose     = "database-configuration"
    Compliance  = "financial-grade"
  })
}

# DB Option Group for additional features
resource "aws_db_option_group" "main" {
  count                    = var.engine == "mysql" ? 1 : 0
  name                     = "${var.app_name}-${var.environment}-db-options"
  option_group_description = "Option group for ${var.app_name} ${var.environment}"
  engine_name              = var.engine
  major_engine_version     = var.major_engine_version

  option {
    option_name = "MARIADB_AUDIT_PLUGIN"

    option_settings {
      name  = "SERVER_AUDIT_EVENTS"
      value = "CONNECT,QUERY,TABLE"
    }

    option_settings {
      name  = "SERVER_AUDIT_LOGGING"
      value = "ON"
    }
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-options"
    Environment = var.environment
    Purpose     = "database-options"
    Compliance  = "financial-grade"
  })
}

# Primary RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.app_name}-${var.environment}-primary"

  # Engine configuration
  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.instance_class

  # Storage configuration
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = true
  kms_key_id           = var.kms_key_id

  # Database configuration
  db_name  = var.database_name
  username = var.master_username
  password = random_password.db_password.result
  port     = var.database_port

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.security_group_id]
  publicly_accessible    = false

  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.main.name
  option_group_name    = var.engine == "mysql" ? aws_db_option_group.main[0].name : null

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  copy_tags_to_snapshot  = true
  delete_automated_backups = false

  # Maintenance configuration
  maintenance_window         = var.maintenance_window
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  allow_major_version_upgrade = false

  # High availability
  multi_az               = var.multi_az
  availability_zone      = var.multi_az ? null : data.aws_availability_zones.available.names[0]

  # Monitoring and logging
  monitoring_interval = var.enhanced_monitoring_interval
  monitoring_role_arn = var.enhanced_monitoring_interval > 0 ? aws_iam_role.rds_enhanced_monitoring[0].arn : null

  enabled_cloudwatch_logs_exports = var.enabled_cloudwatch_logs_exports

  # Performance Insights
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_kms_key_id      = var.performance_insights_enabled ? var.kms_key_id : null
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null

  # Security
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.app_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Apply changes immediately in non-production environments
  apply_immediately = var.environment != "prod"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-primary-db"
    Environment = var.environment
    Purpose     = "primary-database"
    Compliance  = "financial-grade"
    Backup      = "enabled"
    Monitoring  = "enhanced"
  })

  lifecycle {
    ignore_changes = [
      password,
      final_snapshot_identifier,
    ]
  }
}

# Read Replica for read scaling and disaster recovery
resource "aws_db_instance" "read_replica" {
  count = var.create_read_replica ? var.read_replica_count : 0

  identifier = "${var.app_name}-${var.environment}-replica-${count.index + 1}"

  # Replica configuration
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = var.read_replica_instance_class

  # Storage configuration (inherited from source)
  storage_encrypted = true
  kms_key_id       = var.kms_key_id

  # Network configuration
  vpc_security_group_ids = [var.security_group_id]
  publicly_accessible    = false

  # Monitoring
  monitoring_interval = var.enhanced_monitoring_interval
  monitoring_role_arn = var.enhanced_monitoring_interval > 0 ? aws_iam_role.rds_enhanced_monitoring[0].arn : null

  # Performance Insights
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_kms_key_id      = var.performance_insights_enabled ? var.kms_key_id : null
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null

  # Security
  deletion_protection = var.deletion_protection
  skip_final_snapshot = true

  # Apply changes immediately in non-production environments
  apply_immediately = var.environment != "prod"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-replica-${count.index + 1}"
    Environment = var.environment
    Purpose     = "read-replica"
    Compliance  = "financial-grade"
    Replica     = "true"
  })
}

# Enhanced Monitoring IAM Role
resource "aws_iam_role" "rds_enhanced_monitoring" {
  count = var.enhanced_monitoring_interval > 0 ? 1 : 0
  name  = "${var.app_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-rds-monitoring-role"
    Environment = var.environment
    Purpose     = "database-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  count      = var.enhanced_monitoring_interval > 0 ? 1 : 0
  role       = aws_iam_role.rds_enhanced_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Alarms for database monitoring
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.app_name}-${var.environment}-db-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.cpu_alarm_threshold
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-cpu-alarm"
    Environment = var.environment
    Purpose     = "database-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "${var.app_name}-${var.environment}-db-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.connection_alarm_threshold
  alarm_description   = "This metric monitors RDS connection count"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-connections-alarm"
    Environment = var.environment
    Purpose     = "database-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_cloudwatch_metric_alarm" "database_freeable_memory" {
  alarm_name          = "${var.app_name}-${var.environment}-db-freeable-memory"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.freeable_memory_alarm_threshold
  alarm_description   = "This metric monitors RDS freeable memory"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-memory-alarm"
    Environment = var.environment
    Purpose     = "database-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_cloudwatch_metric_alarm" "database_free_storage_space" {
  alarm_name          = "${var.app_name}-${var.environment}-db-free-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.free_storage_alarm_threshold
  alarm_description   = "This metric monitors RDS free storage space"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-storage-alarm"
    Environment = var.environment
    Purpose     = "database-monitoring"
    Compliance  = "financial-grade"
  })
}

# Database secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.app_name}-${var.environment}-db-credentials"
  description             = "Database credentials for ${var.app_name} ${var.environment}"
  kms_key_id             = var.kms_key_id
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-credentials"
    Environment = var.environment
    Purpose     = "database-credentials"
    Compliance  = "financial-grade"
  })
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.db_password.result
    engine   = var.engine
    host     = aws_db_instance.main.endpoint
    port     = aws_db_instance.main.port
    dbname   = aws_db_instance.main.db_name
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# Database snapshot for point-in-time recovery
resource "aws_db_snapshot" "manual_snapshot" {
  count                  = var.create_manual_snapshot ? 1 : 0
  db_instance_identifier = aws_db_instance.main.id
  db_snapshot_identifier = "${var.app_name}-${var.environment}-manual-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-manual-snapshot"
    Environment = var.environment
    Purpose     = "manual-backup"
    Compliance  = "financial-grade"
  })

  lifecycle {
    ignore_changes = [db_snapshot_identifier]
  }
}

# EventBridge rule for database events
resource "aws_cloudwatch_event_rule" "db_events" {
  name        = "${var.app_name}-${var.environment}-db-events"
  description = "Capture database events for ${var.app_name} ${var.environment}"

  event_pattern = jsonencode({
    source      = ["aws.rds"]
    detail-type = ["RDS DB Instance Event", "RDS DB Cluster Event"]
    detail = {
      SourceId = [aws_db_instance.main.id]
    }
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-events"
    Environment = var.environment
    Purpose     = "database-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_cloudwatch_event_target" "db_events_sns" {
  count     = length(var.alarm_actions) > 0 ? 1 : 0
  rule      = aws_cloudwatch_event_rule.db_events.name
  target_id = "SendToSNS"
  arn       = var.alarm_actions[0]
}

# Database proxy for connection pooling and security
resource "aws_db_proxy" "main" {
  count                  = var.create_db_proxy ? 1 : 0
  name                   = "${var.app_name}-${var.environment}-db-proxy"
  engine_family         = var.engine == "postgres" ? "POSTGRESQL" : "MYSQL"
  auth {
    auth_scheme = "SECRETS"
    secret_arn  = aws_secretsmanager_secret.db_credentials.arn
  }
  role_arn               = aws_iam_role.db_proxy[0].arn
  vpc_subnet_ids         = var.private_subnet_ids
  require_tls           = true
  idle_client_timeout   = var.proxy_idle_client_timeout
  max_connections_percent = var.proxy_max_connections_percent
  max_idle_connections_percent = var.proxy_max_idle_connections_percent

  target {
    db_instance_identifier = aws_db_instance.main.id
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-proxy"
    Environment = var.environment
    Purpose     = "database-proxy"
    Compliance  = "financial-grade"
  })
}

# IAM role for DB proxy
resource "aws_iam_role" "db_proxy" {
  count = var.create_db_proxy ? 1 : 0
  name  = "${var.app_name}-${var.environment}-db-proxy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-proxy-role"
    Environment = var.environment
    Purpose     = "database-proxy"
    Compliance  = "financial-grade"
  })
}

resource "aws_iam_role_policy" "db_proxy" {
  count = var.create_db_proxy ? 1 : 0
  name  = "${var.app_name}-${var.environment}-db-proxy-policy"
  role  = aws_iam_role.db_proxy[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }
    ]
  })
}
