# Enhanced Security Module for Financial Services
# Implements comprehensive security controls meeting financial industry standards

# Data sources for existing resources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# KMS Key for encryption at rest
resource "aws_kms_key" "main" {
  description             = "KMS key for ${var.app_name} ${var.environment} encryption"
  deletion_window_in_days = var.kms_deletion_window
  enable_key_rotation     = true
  multi_region           = var.multi_region_key

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-kms-key"
    Environment = var.environment
    Purpose     = "encryption"
    Compliance  = "financial-grade"
  })
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.app_name}-${var.environment}-key"
  target_key_id = aws_kms_key.main.key_id
}

# Enhanced Application Security Group with strict rules
resource "aws_security_group" "app" {
  name        = "${var.app_name}-${var.environment}-app-sg"
  description = "Enhanced security group for ${var.app_name} application in ${var.environment}"
  vpc_id      = var.vpc_id

  # HTTPS only - no HTTP allowed for financial applications
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "HTTPS from ALB only"
  }

  # Application port from ALB only
  ingress {
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Application port from ALB"
  }

  # SSH access restricted to bastion host
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "SSH from bastion host only"
  }

  # Monitoring port for health checks
  ingress {
    from_port       = var.health_check_port
    to_port         = var.health_check_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Health check from ALB"
  }

  # Restricted egress - only necessary outbound traffic
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound for API calls and updates"
  }

  egress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.db.id]
    description     = "MySQL to database"
  }

  egress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.redis.id]
    description     = "Redis connection"
  }

  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "DNS resolution"
  }

  egress {
    from_port   = 123
    to_port     = 123
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "NTP for time synchronization"
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-app-sg"
    Environment = var.environment
    Purpose     = "application-security"
    Compliance  = "financial-grade"
  })
}

# Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name        = "${var.app_name}-${var.environment}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTPS from allowed networks"
  }

  # Redirect HTTP to HTTPS
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTP redirect to HTTPS"
  }

  egress {
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "To application instances"
  }

  egress {
    from_port       = var.health_check_port
    to_port         = var.health_check_port
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Health check to application"
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-alb-sg"
    Environment = var.environment
    Purpose     = "load-balancer-security"
    Compliance  = "financial-grade"
  })
}

# Enhanced Database Security Group
resource "aws_security_group" "db" {
  name        = "${var.app_name}-${var.environment}-db-sg"
  description = "Enhanced security group for ${var.app_name} database in ${var.environment}"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "MySQL from application tier"
  }

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "MySQL from bastion for maintenance"
  }

  # No egress rules - database should not initiate outbound connections
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-db-sg"
    Environment = var.environment
    Purpose     = "database-security"
    Compliance  = "financial-grade"
  })
}

# Redis Security Group
resource "aws_security_group" "redis" {
  name        = "${var.app_name}-${var.environment}-redis-sg"
  description = "Security group for Redis cache"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Redis from application tier"
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-redis-sg"
    Environment = var.environment
    Purpose     = "cache-security"
    Compliance  = "financial-grade"
  })
}

# Bastion Host Security Group
resource "aws_security_group" "bastion" {
  name        = "${var.app_name}-${var.environment}-bastion-sg"
  description = "Security group for bastion host"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.admin_cidr_blocks
    description = "SSH from admin networks"
  }

  egress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id, aws_security_group.db.id]
    description     = "SSH to application and database tiers"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS for package updates"
  }

  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "DNS resolution"
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-bastion-sg"
    Environment = var.environment
    Purpose     = "bastion-security"
    Compliance  = "financial-grade"
  })
}

# WAF Web ACL for application protection
resource "aws_wafv2_web_acl" "main" {
  name  = "${var.app_name}-${var.environment}-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.rate_limit_per_5min
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - Core Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - Known Bad Inputs
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "KnownBadInputsRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  # SQL Injection Protection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 4

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SQLiRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  # Geographic restriction rule
  rule {
    name     = "GeoRestrictionRule"
    priority = 5

    action {
      block {}
    }

    statement {
      geo_match_statement {
        country_codes = var.blocked_countries
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "GeoRestrictionRule"
      sampled_requests_enabled   = true
    }
  }

  # IP reputation rule
  rule {
    name     = "AWSManagedRulesAmazonIpReputationList"
    priority = 6

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "IpReputationListMetric"
      sampled_requests_enabled   = true
    }
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-waf"
    Environment = var.environment
    Purpose     = "web-application-firewall"
    Compliance  = "financial-grade"
  })
}

# CloudTrail for audit logging
resource "aws_cloudtrail" "main" {
  name           = "${var.app_name}-${var.environment}-cloudtrail"
  s3_bucket_name = aws_s3_bucket.cloudtrail_logs.bucket

  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    exclude_management_event_sources = []

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.app_data.arn}/*"]
    }
  }

  insight_selector {
    insight_type = "ApiCallRateInsight"
  }

  kms_key_id                = aws_kms_key.main.arn
  include_global_service_events = true
  is_multi_region_trail     = var.multi_region_trail
  enable_log_file_validation = true

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-cloudtrail"
    Environment = var.environment
    Purpose     = "audit-logging"
    Compliance  = "financial-grade"
  })
}

# S3 bucket for CloudTrail logs
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket        = "${var.app_name}-${var.environment}-cloudtrail-logs-${random_id.bucket_suffix.hex}"
  force_destroy = var.environment != "prod"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-cloudtrail-logs"
    Environment = var.environment
    Purpose     = "audit-logs"
    Compliance  = "financial-grade"
  })
}

resource "aws_s3_bucket_versioning" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.main.arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# S3 bucket for application data
resource "aws_s3_bucket" "app_data" {
  bucket        = "${var.app_name}-${var.environment}-app-data-${random_id.bucket_suffix.hex}"
  force_destroy = var.environment != "prod"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-app-data"
    Environment = var.environment
    Purpose     = "application-data"
    Compliance  = "financial-grade"
  })
}

resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.main.arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  rule {
    id     = "financial_data_retention"
    status = "Enabled"

    expiration {
      days = var.data_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Random ID for unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# GuardDuty for threat detection
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-guardduty"
    Environment = var.environment
    Purpose     = "threat-detection"
    Compliance  = "financial-grade"
  })
}

# Config for compliance monitoring
resource "aws_config_configuration_recorder" "main" {
  name     = "${var.app_name}-${var.environment}-config-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.app_name}-${var.environment}-config-delivery"
  s3_bucket_name = aws_s3_bucket.config_logs.bucket
}

# S3 bucket for Config logs
resource "aws_s3_bucket" "config_logs" {
  bucket        = "${var.app_name}-${var.environment}-config-logs-${random_id.bucket_suffix.hex}"
  force_destroy = var.environment != "prod"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-config-logs"
    Environment = var.environment
    Purpose     = "compliance-logs"
    Compliance  = "financial-grade"
  })
}

resource "aws_s3_bucket_encryption" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.main.arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }
}

resource "aws_s3_bucket_public_access_block" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role for Config
resource "aws_iam_role" "config" {
  name = "${var.app_name}-${var.environment}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-config-role"
    Environment = var.environment
    Purpose     = "compliance-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_iam_role_policy_attachment" "config" {
  role       = aws_iam_role.config.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}

# Security Hub for centralized security findings
resource "aws_securityhub_account" "main" {
  enable_default_standards = true
}

# Inspector for vulnerability assessment
resource "aws_inspector2_enabler" "main" {
  account_ids    = [data.aws_caller_identity.current.account_id]
  resource_types = ["ECR", "EC2"]
}

# Network ACLs for additional network security
resource "aws_network_acl" "private" {
  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids

  # Allow inbound HTTPS from public subnets
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 443
    to_port    = 443
  }

  # Allow inbound application port from public subnets
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = var.app_port
    to_port    = var.app_port
  }

  # Allow inbound SSH from bastion
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 22
    to_port    = 22
  }

  # Allow return traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 130
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Allow outbound HTTPS
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Allow outbound database connections
  egress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 3306
    to_port    = 3306
  }

  # Allow outbound Redis connections
  egress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 6379
    to_port    = 6379
  }

  # Allow outbound DNS
  egress {
    protocol   = "udp"
    rule_no    = 130
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 53
    to_port    = 53
  }

  # Allow outbound NTP
  egress {
    protocol   = "udp"
    rule_no    = 140
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 123
    to_port    = 123
  }

  # Allow return traffic
  egress {
    protocol   = "tcp"
    rule_no    = 150
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-private-nacl"
    Environment = var.environment
    Purpose     = "network-security"
    Compliance  = "financial-grade"
  })
}

# VPC Flow Logs for network monitoring
resource "aws_flow_log" "vpc" {
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = var.vpc_id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vpc-flow-log"
    Environment = var.environment
    Purpose     = "network-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_cloudwatch_log_group" "vpc_flow_log" {
  name              = "/aws/vpc/${var.app_name}-${var.environment}-flow-log"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.main.arn

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vpc-flow-log-group"
    Environment = var.environment
    Purpose     = "network-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_iam_role" "flow_log" {
  name = "${var.app_name}-${var.environment}-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-flow-log-role"
    Environment = var.environment
    Purpose     = "network-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_iam_role_policy" "flow_log" {
  name = "${var.app_name}-${var.environment}-flow-log-policy"
  role = aws_iam_role.flow_log.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}
