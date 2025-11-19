# Enhanced Security Module Outputs for Financial Services

# Security Groups
output "app_security_group_id" {
  description = "ID of the application security group"
  value       = aws_security_group.app.id
}

output "alb_security_group_id" {
  description = "ID of the Application Load Balancer security group"
  value       = aws_security_group.alb.id
}

output "db_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.db.id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = aws_security_group.redis.id
}

output "bastion_security_group_id" {
  description = "ID of the bastion host security group"
  value       = aws_security_group.bastion.id
}

# KMS Key
output "kms_key_id" {
  description = "ID of the KMS key for encryption"
  value       = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  value       = aws_kms_key.main.arn
}

output "kms_alias_name" {
  description = "Name of the KMS key alias"
  value       = aws_kms_alias.main.name
}

# WAF
output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.id
}

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}

# S3 Buckets
output "app_data_bucket_id" {
  description = "ID of the application data S3 bucket"
  value       = aws_s3_bucket.app_data.id
}

output "app_data_bucket_arn" {
  description = "ARN of the application data S3 bucket"
  value       = aws_s3_bucket.app_data.arn
}

output "cloudtrail_logs_bucket_id" {
  description = "ID of the CloudTrail logs S3 bucket"
  value       = aws_s3_bucket.cloudtrail_logs.id
}

output "cloudtrail_logs_bucket_arn" {
  description = "ARN of the CloudTrail logs S3 bucket"
  value       = aws_s3_bucket.cloudtrail_logs.arn
}

output "config_logs_bucket_id" {
  description = "ID of the Config logs S3 bucket"
  value       = aws_s3_bucket.config_logs.id
}

output "config_logs_bucket_arn" {
  description = "ARN of the Config logs S3 bucket"
  value       = aws_s3_bucket.config_logs.arn
}

# CloudTrail
output "cloudtrail_arn" {
  description = "ARN of the CloudTrail"
  value       = aws_cloudtrail.main.arn
}

output "cloudtrail_home_region" {
  description = "Home region of the CloudTrail"
  value       = aws_cloudtrail.main.home_region
}

# GuardDuty
output "guardduty_detector_id" {
  description = "ID of the GuardDuty detector"
  value       = aws_guardduty_detector.main.id
}

# Config
output "config_recorder_name" {
  description = "Name of the Config configuration recorder"
  value       = aws_config_configuration_recorder.main.name
}

output "config_delivery_channel_name" {
  description = "Name of the Config delivery channel"
  value       = aws_config_delivery_channel.main.name
}

# Security Hub
output "security_hub_account_id" {
  description = "Account ID where Security Hub is enabled"
  value       = aws_securityhub_account.main.id
}

# Inspector
output "inspector_enabler_account_ids" {
  description = "Account IDs where Inspector is enabled"
  value       = aws_inspector2_enabler.main.account_ids
}

# Network ACL
output "private_network_acl_id" {
  description = "ID of the private network ACL"
  value       = aws_network_acl.private.id
}

# VPC Flow Logs
output "vpc_flow_log_id" {
  description = "ID of the VPC Flow Log"
  value       = aws_flow_log.vpc.id
}

output "vpc_flow_log_group_name" {
  description = "Name of the VPC Flow Log CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.vpc_flow_log.name
}

output "vpc_flow_log_group_arn" {
  description = "ARN of the VPC Flow Log CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.vpc_flow_log.arn
}

# IAM Roles
output "config_role_arn" {
  description = "ARN of the Config service role"
  value       = aws_iam_role.config.arn
}

output "flow_log_role_arn" {
  description = "ARN of the VPC Flow Log role"
  value       = aws_iam_role.flow_log.arn
}

# Security Configuration Summary
output "security_features_enabled" {
  description = "Summary of enabled security features"
  value = {
    encryption_at_rest        = var.enable_encryption_at_rest
    encryption_in_transit     = var.enable_encryption_in_transit
    audit_logging            = var.enable_audit_logging
    threat_detection         = var.enable_threat_detection
    vulnerability_scanning   = var.enable_vulnerability_scanning
    compliance_monitoring    = var.enable_compliance_monitoring
    network_monitoring       = var.enable_network_monitoring
    data_loss_prevention     = var.enable_data_loss_prevention
    waf_protection          = true
    ddos_protection         = var.enable_ddos_protection
    intrusion_detection     = var.enable_intrusion_detection
  }
}

# Compliance Configuration Summary
output "compliance_features_enabled" {
  description = "Summary of enabled compliance features"
  value = {
    pci_dss_compliance    = var.pci_dss_compliance
    sox_compliance        = var.sox_compliance
    gdpr_compliance       = var.gdpr_compliance
    hipaa_compliance      = var.hipaa_compliance
    iso_27001_compliance  = var.iso_27001_compliance
    regulatory_reporting  = var.enable_regulatory_reporting
    compliance_dashboard  = var.compliance_dashboard_enabled
  }
}

# Data Protection Summary
output "data_protection_configuration" {
  description = "Summary of data protection configuration"
  value = {
    data_retention_days           = var.data_retention_days
    backup_retention_days         = var.backup_retention_days
    backup_frequency_hours        = var.backup_frequency_hours
    point_in_time_recovery       = var.enable_point_in_time_recovery
    cross_region_backup          = var.cross_region_backup
    kms_key_rotation_enabled     = true
    s3_versioning_enabled        = true
    s3_encryption_enabled        = true
  }
}

# Monitoring and Alerting Summary
output "monitoring_configuration" {
  description = "Summary of monitoring and alerting configuration"
  value = {
    cloudtrail_enabled           = true
    guardduty_enabled           = true
    config_enabled              = true
    security_hub_enabled        = true
    inspector_enabled           = true
    vpc_flow_logs_enabled       = true
    real_time_monitoring        = var.enable_real_time_monitoring
    automated_response          = var.automated_response_enabled
    log_retention_days          = var.log_retention_days
  }
}

# Network Security Summary
output "network_security_configuration" {
  description = "Summary of network security configuration"
  value = {
    security_groups_count       = 5
    network_acl_enabled        = true
    waf_rules_count           = 6
    rate_limiting_enabled     = true
    geo_blocking_enabled      = true
    ip_reputation_filtering   = true
    sql_injection_protection  = true
    xss_protection           = true
  }
}

# Access Control Summary
output "access_control_configuration" {
  description = "Summary of access control configuration"
  value = {
    mfa_required              = var.enable_mfa_requirement
    session_timeout_minutes   = var.session_timeout_minutes
    password_policy_enforced  = true
    rbac_enabled             = true
    least_privilege_access   = true
    bastion_host_required    = true
  }
}

# Disaster Recovery Summary
output "disaster_recovery_configuration" {
  description = "Summary of disaster recovery configuration"
  value = {
    high_availability_enabled    = var.high_availability_enabled
    disaster_recovery_enabled    = var.disaster_recovery_enabled
    multi_region_deployment     = var.multi_region_trail
    rto_hours                   = var.recovery_time_objective_hours
    rpo_hours                   = var.recovery_point_objective_hours
    automated_failover          = var.auto_scaling_enabled
  }
}
