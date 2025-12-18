# Enhanced Security Module Variables for Financial Services

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

variable "vpc_id" {
  description = "ID of the VPC where resources will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "app_port" {
  description = "Port on which the application runs"
  type        = number
  default     = 8000
}

variable "health_check_port" {
  description = "Port for health check endpoint"
  type        = number
  default     = 8080
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "admin_cidr_blocks" {
  description = "List of CIDR blocks allowed for administrative access"
  type        = list(string)
  default     = []
}

variable "blocked_countries" {
  description = "List of country codes to block in WAF"
  type        = list(string)
  default     = ["CN", "RU", "KP", "IR"]
}

variable "rate_limit_per_5min" {
  description = "Rate limit per 5 minutes for WAF"
  type        = number
  default     = 2000
}

variable "kms_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 30
  validation {
    condition     = var.kms_deletion_window >= 7 && var.kms_deletion_window <= 30
    error_message = "KMS deletion window must be between 7 and 30 days."
  }
}

variable "multi_region_key" {
  description = "Whether to create a multi-region KMS key"
  type        = bool
  default     = false
}

variable "multi_region_trail" {
  description = "Whether to create a multi-region CloudTrail"
  type        = bool
  default     = true
}

variable "data_retention_days" {
  description = "Number of days to retain application data"
  type        = number
  default     = 2555 # 7 years for financial compliance
  validation {
    condition     = var.data_retention_days >= 365
    error_message = "Data retention must be at least 365 days for financial compliance."
  }
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 365
  validation {
    condition     = var.log_retention_days >= 90
    error_message = "Log retention must be at least 90 days for financial compliance."
  }
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project    = "quantis"
    ManagedBy  = "terraform"
    Compliance = "financial-grade"
    DataClass  = "confidential"
  }
}

# Compliance and Security Configuration
variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest for all storage resources"
  type        = bool
  default     = true
}

variable "enable_encryption_in_transit" {
  description = "Enable encryption in transit for all communications"
  type        = bool
  default     = true
}

variable "enable_audit_logging" {
  description = "Enable comprehensive audit logging"
  type        = bool
  default     = true
}

variable "enable_threat_detection" {
  description = "Enable threat detection services"
  type        = bool
  default     = true
}

variable "enable_vulnerability_scanning" {
  description = "Enable vulnerability scanning"
  type        = bool
  default     = true
}

variable "enable_compliance_monitoring" {
  description = "Enable compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_network_monitoring" {
  description = "Enable network traffic monitoring"
  type        = bool
  default     = true
}

variable "enable_data_loss_prevention" {
  description = "Enable data loss prevention measures"
  type        = bool
  default     = true
}

# Financial Compliance Specific Variables
variable "pci_dss_compliance" {
  description = "Enable PCI DSS compliance features"
  type        = bool
  default     = true
}

variable "sox_compliance" {
  description = "Enable SOX compliance features"
  type        = bool
  default     = true
}

variable "gdpr_compliance" {
  description = "Enable GDPR compliance features"
  type        = bool
  default     = true
}

variable "hipaa_compliance" {
  description = "Enable HIPAA compliance features (if handling health data)"
  type        = bool
  default     = false
}

variable "iso_27001_compliance" {
  description = "Enable ISO 27001 compliance features"
  type        = bool
  default     = true
}

# Security Monitoring Configuration
variable "security_notification_email" {
  description = "Email address for security notifications"
  type        = string
  default     = ""
}

variable "critical_alert_sns_topic" {
  description = "SNS topic ARN for critical security alerts"
  type        = string
  default     = ""
}

variable "enable_real_time_monitoring" {
  description = "Enable real-time security monitoring"
  type        = bool
  default     = true
}

variable "security_scan_schedule" {
  description = "Cron expression for security scan schedule"
  type        = string
  default     = "cron(0 2 * * ? *)" # Daily at 2 AM
}

# Access Control Configuration
variable "enable_mfa_requirement" {
  description = "Require MFA for all administrative access"
  type        = bool
  default     = true
}

variable "session_timeout_minutes" {
  description = "Session timeout in minutes"
  type        = number
  default     = 30
}

variable "password_policy" {
  description = "Password policy configuration"
  type = object({
    minimum_length            = number
    require_uppercase         = bool
    require_lowercase         = bool
    require_numbers           = bool
    require_symbols           = bool
    max_age_days              = number
    password_reuse_prevention = number
  })
  default = {
    minimum_length            = 14
    require_uppercase         = true
    require_lowercase         = true
    require_numbers           = true
    require_symbols           = true
    max_age_days              = 90
    password_reuse_prevention = 12
  }
}

# Network Security Configuration
variable "enable_ddos_protection" {
  description = "Enable DDoS protection"
  type        = bool
  default     = true
}

variable "enable_intrusion_detection" {
  description = "Enable intrusion detection system"
  type        = bool
  default     = true
}

variable "firewall_rules" {
  description = "Custom firewall rules"
  type = list(object({
    name        = string
    priority    = number
    action      = string
    protocol    = string
    source_cidr = string
    dest_port   = number
  }))
  default = []
}

# Data Protection Configuration
variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 2555 # 7 years for financial compliance
}

variable "backup_frequency_hours" {
  description = "Backup frequency in hours"
  type        = number
  default     = 24
}

variable "enable_point_in_time_recovery" {
  description = "Enable point-in-time recovery for databases"
  type        = bool
  default     = true
}

variable "cross_region_backup" {
  description = "Enable cross-region backup replication"
  type        = bool
  default     = true
}

# Incident Response Configuration
variable "incident_response_team_emails" {
  description = "List of email addresses for incident response team"
  type        = list(string)
  default     = []
}

variable "automated_response_enabled" {
  description = "Enable automated incident response"
  type        = bool
  default     = true
}

variable "quarantine_suspicious_activity" {
  description = "Automatically quarantine suspicious activity"
  type        = bool
  default     = true
}

# Regulatory Reporting Configuration
variable "enable_regulatory_reporting" {
  description = "Enable automated regulatory reporting"
  type        = bool
  default     = true
}

variable "reporting_frequency" {
  description = "Frequency of regulatory reports (daily, weekly, monthly)"
  type        = string
  default     = "daily"
  validation {
    condition     = contains(["daily", "weekly", "monthly"], var.reporting_frequency)
    error_message = "Reporting frequency must be one of: daily, weekly, monthly."
  }
}

variable "compliance_dashboard_enabled" {
  description = "Enable compliance dashboard"
  type        = bool
  default     = true
}

# Performance and Scalability
variable "auto_scaling_enabled" {
  description = "Enable auto-scaling for security components"
  type        = bool
  default     = true
}

variable "high_availability_enabled" {
  description = "Enable high availability configuration"
  type        = bool
  default     = true
}

variable "disaster_recovery_enabled" {
  description = "Enable disaster recovery configuration"
  type        = bool
  default     = true
}

variable "recovery_time_objective_hours" {
  description = "Recovery Time Objective in hours"
  type        = number
  default     = 4
}

variable "recovery_point_objective_hours" {
  description = "Recovery Point Objective in hours"
  type        = number
  default     = 1
}
